"""
Official Grafana MCP Client Adapter.

Communicates with the official Grafana MCP server (e.g., mcp-grafana)
via standard Model Context Protocol (MCP) using standard I/O (stdio) JSON-RPC.

This is the REAL runtime integration required for the hackathon submission.
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


class LiveGrafanaMCPClient(GrafanaMCPClientInterface):
    """
    Client connecting to the official Grafana mcp-grafana server over stdio MCP transport.
    Uses official MCP Python SDK (mcp.client.stdio.stdio_client and ClientSession).
    """

    def __init__(
        self,
        grafana_url: Optional[str] = None,
        token: Optional[str] = None,
        command: Optional[str] = None,
    ):
        raw_url = grafana_url if grafana_url is not None else settings.grafana_url
        self.grafana_url = raw_url.rstrip("/") if raw_url else ""
        self.token = token if token is not None else settings.grafana_service_account_token
        self.command = command or settings.grafana_mcp_command
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

        # Parse command string into binary and arguments
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

    async def _execute_mcp_call(self, tool_name: str, arguments: Dict[str, Any], timeout_seconds: float = 15.0) -> Any:
        """
        Spawns mcp-grafana via stdio, initializes the session, and executes a tool call.
        Handles missing executable, timeouts, auth errors, and malformed responses cleanly.
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
                            result = await session.call_tool(tool_name, arguments)
                            return self._parse_tool_result(result)
                except FileNotFoundError as fnf:
                    logger.error("mcp-grafana executable not found: %s", self.command)
                    return {
                        "status": "error",
                        "error": "mcp_executable_missing",
                        "message": (
                            f"mcp-grafana executable '{self.command}' not found on system PATH. "
                            f"Please install mcp-grafana or configure GRAFANA_MCP_COMMAND. Details: {fnf}"
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
                    logger.error("MCP session error calling tool %s: %s", tool_name, session_exc)
                    return {
                        "status": "error",
                        "error": "mcp_session_error",
                        "message": str(session_exc),
                    }
        except TimeoutError:
            logger.error("Timeout (%ss) while executing MCP tool %s", timeout_seconds, tool_name)
            return {
                "status": "error",
                "error": "mcp_tool_timeout",
                "message": f"Execution of Grafana MCP tool '{tool_name}' timed out after {timeout_seconds}s",
            }

    def _parse_tool_result(self, result: Any) -> Any:
        """Parses MCP CallToolResult content blocks into structured Python objects."""
        if not result:
            return {}

        # If result has content blocks (standard MCP CallToolResult)
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

    async def discover_tools(self, timeout_seconds: float = 10.0) -> List[Dict[str, Any]]:
        """
        Queries mcp-grafana tools/list to inspect all tools exposed by the official server.
        """
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        try:
            params = self._get_server_params()
            async with asyncio.timeout(timeout_seconds):
                async with stdio_client(params) as (read_stream, write_stream):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        tools_result = await session.list_tools()
                        return [
                            {
                                "name": tool.name,
                                "description": tool.description,
                                "inputSchema": tool.inputSchema,
                            }
                            for tool in tools_result.tools
                        ]
        except Exception as exc:
            logger.warning("Could not discover tools from mcp-grafana: %s", exc)
            return [
                {
                    "error": "tool_discovery_failed",
                    "message": str(exc),
                }
            ]

    async def query_prometheus(self, query: str, time_range: str = "5m") -> Dict[str, Any]:
        """Call official Grafana MCP tool for Prometheus queries."""
        raw = await self._execute_mcp_call(
            tool_name="query_prometheus",
            arguments={"query": query, "time_range": time_range}
        )

        if isinstance(raw, dict) and raw.get("status") == "error":
            return raw

        if isinstance(raw, dict) and "data" in raw:
            raw["status"] = "success"
            raw["mcp_source"] = "official_mcp_grafana"
            return raw

        return {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": raw if isinstance(raw, list) else [raw]
            },
            "mcp_source": "official_mcp_grafana"
        }

    async def query_loki(self, logql: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Call official Grafana MCP tool for Loki queries."""
        raw = await self._execute_mcp_call(
            tool_name="query_loki",
            arguments={"query": logql, "limit": limit}
        )

        if isinstance(raw, dict) and raw.get("status") == "error":
            return [raw]

        if isinstance(raw, list):
            return raw
        if isinstance(raw, dict) and "logs" in raw:
            return raw["logs"]
        return [raw]

    async def list_active_alerts(self, filter_labels: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Call official Grafana MCP tool for alerts."""
        raw = await self._execute_mcp_call(
            tool_name="list_alerts",
            arguments={"filter": filter_labels or {}}
        )

        if isinstance(raw, dict) and raw.get("status") == "error":
            return [raw]

        if isinstance(raw, list):
            return raw
        return [raw]
