"""
Official Grafana MCP Client Adapter.

Communicates with the official Grafana MCP server (mcp-grafana)
via standard Model Context Protocol (MCP) using standard I/O (stdio) JSON-RPC.
"""

import asyncio
import json
import logging
import os
import shlex
from typing import Any, Dict, List, Optional

from postwire.config import settings
from postwire.grafana.integration.interface import GrafanaMCPClientInterface

logger = logging.getLogger(__name__)


_UNSET = object()


class LiveGrafanaMCPClient(GrafanaMCPClientInterface):
    """
    Client connecting to the official Grafana mcp-grafana server over stdio MCP transport.
    Uses official MCP Python SDK (mcp.client.stdio.stdio_client and ClientSession).
    """

    def __init__(
        self,
        grafana_url: Any = _UNSET,
        token: Any = _UNSET,
        command: Optional[str] = None,
        prometheus_uid: Optional[str] = None,
        loki_uid: Optional[str] = None,
    ):
        if grafana_url is not _UNSET:
            self.grafana_url = (grafana_url or "").rstrip("/")
        else:
            self.grafana_url = (settings.grafana_url or "").rstrip("/")

        if token is not _UNSET:
            self.token = token
        else:
            self.token = settings.grafana_service_account_token

        self.command = command or settings.grafana_mcp_command
        self.prometheus_uid = prometheus_uid or settings.grafana_prometheus_uid
        self.loki_uid = loki_uid or settings.grafana_loki_uid
        self._validate_configuration()

    @property
    def mode(self) -> str:
        return f"live (Official mcp-grafana server via stdio -> {self.grafana_url})"

    def _validate_configuration(self) -> None:
        """Validates that credentials exist. Fails explicitly rather than pretending."""
        if not self.token:
            raise ValueError(
                "GRAFANA_SERVICE_ACCOUNT_TOKEN is required to connect to the live Grafana MCP server. "
                "For local development/testing without Grafana credentials, use MockGrafanaMCPClient or set POSTWIRE_GRAFANA_MODE=mock."
            )
        if not self.grafana_url:
            raise ValueError("GRAFANA_URL is required to connect to the live Grafana MCP server.")

    def _get_server_params(self):
        """Constructs StdioServerParameters with required Grafana environment variables."""
        from mcp import StdioServerParameters

        parts = shlex.split(self.command)
        if not parts:
            raise ValueError("GRAFANA_MCP_COMMAND cannot be empty.")

        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        env = dict(os.environ)
        env["GRAFANA_URL"] = self.grafana_url
        env["GRAFANA_SERVICE_ACCOUNT_TOKEN"] = self.token

        return StdioServerParameters(
            command=cmd,
            args=args,
            env=env
        )

    async def _execute_mcp_session(self, callback, timeout_seconds: float = 25.0) -> Any:
        """
        Connects via stdio, initializes session, runs callback(session), and returns result.
        Safely handles timeouts, missing executables, and session errors.
        """
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        try:
            params = self._get_server_params()
        except Exception as exc:
            return {
                "status": "error",
                "error": "configuration_error",
                "message": str(exc),
            }

        try:
            async with asyncio.timeout(timeout_seconds):
                try:
                    async with stdio_client(params) as (read_stream, write_stream):
                        async with ClientSession(read_stream, write_stream) as session:
                            await session.initialize()
                            return await callback(session)
                except FileNotFoundError as fnf:
                    logger.error("mcp-grafana executable not found: %s", self.command)
                    return {
                        "status": "error",
                        "error": "mcp_executable_missing",
                        "message": (
                            f"mcp-grafana command '{self.command}' could not be executed. "
                            f"Ensure mcp-grafana is installed or uv tool is available. Details: {fnf}"
                        ),
                    }
                except ConnectionError as conn_err:
                    logger.error("Failed to connect or communicate with mcp-grafana: %s", conn_err)
                    return {
                        "status": "error",
                        "error": "mcp_connection_failed",
                        "message": f"Connection to mcp-grafana failed: {conn_err}",
                    }
                except Exception as session_exc:
                    logger.error("MCP session error: %s", session_exc)
                    return {
                        "status": "error",
                        "error": "mcp_session_error",
                        "message": str(session_exc),
                    }
        except TimeoutError:
            logger.error("Timeout (%ss) while communicating with mcp-grafana", timeout_seconds)
            return {
                "status": "error",
                "error": "mcp_tool_timeout",
                "message": f"mcp-grafana session timed out after {timeout_seconds}s",
            }

    def _parse_tool_result(self, result: Any) -> Any:
        """Parses MCP CallToolResult content blocks into structured Python objects."""
        if not result:
            return {}

        if hasattr(result, "content"):
            content_blocks = result.content
            parsed_items = []
            for block in content_blocks:
                text = getattr(block, "text", "")
                if not text and isinstance(block, dict):
                    text = block.get("text", "")

                try:
                    parsed_items.append(json.loads(text))
                except Exception:
                    parsed_items.append({"text": text})

            if len(parsed_items) == 1:
                return parsed_items[0]
            return parsed_items

        if isinstance(result, dict):
            return result
        return {"data": str(result)}

    async def _resolve_datasource_uid(self, session, ds_type: str) -> Optional[str]:
        """Resolves datasource UID for prometheus or loki using list_datasources tool."""
        try:
            res = await session.call_tool("list_datasources", {"type": ds_type, "limit": 10})
            parsed = self._parse_tool_result(res)
            # parsed can be list of datasources or dict with datasources
            datasources = parsed if isinstance(parsed, list) else parsed.get("datasources", [parsed])
            for ds in datasources:
                if isinstance(ds, dict) and ds.get("uid"):
                    return ds["uid"]
        except Exception as e:
            logger.debug("Auto-resolving datasource UID for %s returned: %s", ds_type, e)
        return None

    async def discover_tools(self, timeout_seconds: float = 15.0) -> List[Dict[str, Any]]:
        """Queries tools/list from mcp-grafana to inspect all available tools."""
        async def run_list(session):
            tools_result = await session.list_tools()
            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": getattr(tool, "input_schema", getattr(tool, "inputSchema", {})),
                }
                for tool in tools_result.tools
            ]

        res = await self._execute_mcp_session(run_list, timeout_seconds=timeout_seconds)
        if isinstance(res, dict) and res.get("status") == "error":
            return [res]
        return res if isinstance(res, list) else [res]

    async def query_prometheus(self, query: str, time_range: str = "5m") -> Dict[str, Any]:
        """
        Executes PromQL query using official mcp-grafana tool 'query_prometheus'.
        Auto-resolves datasource UID if not explicitly configured.
        """
        async def run_prom(session):
            # Resolve datasource UID
            ds_uid = self.prometheus_uid
            if not ds_uid:
                ds_uid = await self._resolve_datasource_uid(session, "prometheus") or "grafanacloud-prom"
                self.prometheus_uid = ds_uid

            # Call query_prometheus matching mcp-grafana signature
            tool_args = {
                "datasourceUid": ds_uid,
                "expr": query,
                "endTime": "now",
                "queryType": "instant"
            }
            res = await session.call_tool("query_prometheus", tool_args)
            return self._parse_tool_result(res)

        raw = await self._execute_mcp_session(run_prom)
        if isinstance(raw, dict) and raw.get("status") == "error":
            return raw

        return {
            "status": "success",
            "data": raw if isinstance(raw, dict) else {"result": raw},
            "mcp_source": "official_mcp_grafana"
        }

    async def query_loki(self, logql: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Executes LogQL query using official mcp-grafana tool 'query_loki_logs'.
        Auto-resolves datasource UID if not explicitly configured.
        """
        async def run_loki(session):
            # Resolve datasource UID
            ds_uid = self.loki_uid
            if not ds_uid:
                ds_uid = await self._resolve_datasource_uid(session, "loki") or "grafanacloud-logs"
                self.loki_uid = ds_uid

            tool_args = {
                "datasourceUid": ds_uid,
                "logql": logql,
                "limit": limit
            }
            # Official mcp-grafana uses 'query_loki_logs'
            res = await session.call_tool("query_loki_logs", tool_args)
            return self._parse_tool_result(res)

        raw = await self._execute_mcp_session(run_loki)
        if isinstance(raw, dict) and raw.get("status") == "error":
            return [raw]

        if isinstance(raw, list):
            return raw
        return [raw]

    async def list_active_alerts(self, filter_labels: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Retrieves active alerts using official mcp-grafana tool 'alerting_manage_rules' or 'list_alert_groups'.
        """
        async def run_alerts(session):
            try:
                res = await session.call_tool("alerting_manage_rules", {"operation": "list"})
                parsed = self._parse_tool_result(res)
                if parsed is None or parsed == {}:
                    return []
                if isinstance(parsed, list):
                    return parsed
                if isinstance(parsed, dict) and "error" not in parsed:
                    return [parsed]
            except Exception as e:
                logger.debug("alerting_manage_rules failed (%s), trying list_alert_groups", e)

            tool_args = {}
            if filter_labels:
                tool_args["labels"] = [f"{k}:{v}" for k, v in filter_labels.items()]

            res = await session.call_tool("list_alert_groups", tool_args)
            parsed = self._parse_tool_result(res)
            if parsed is None or parsed == {}:
                return []
            return parsed if isinstance(parsed, list) else [parsed]

        raw = await self._execute_mcp_session(run_alerts, timeout_seconds=15.0)
        if isinstance(raw, dict) and raw.get("status") == "error":
            return [raw]

        if isinstance(raw, list):
            return raw
        return [] if raw is None else [raw]
