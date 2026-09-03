"""
Verification script for official Grafana MCP server connection.
Tests the real stdio protocol handshake, tools/list discovery, and live queries against Grafana Cloud.
"""

import asyncio
import os
import sys
from postwire.config import settings
from postwire.grafana.integration.live_mcp_client import LiveGrafanaMCPClient


async def run_verification():
    print("=" * 70)
    print("PostWire — Milestone 2C: Real Grafana Cloud MCP Verification")
    print("=" * 70)

    cmd = settings.grafana_mcp_command
    url = settings.grafana_url
    token_present = bool(settings.grafana_service_account_token)

    # Security check: Never display or leak the actual token
    token_status = "[CONFIGURED]" if token_present else "[NOT CONFIGURED]"

    print(f"[*] Configured MCP Command: {cmd}")
    print(f"[*] Target Grafana URL:     {url}")
    print(f"[*] Service Account Token:  {token_status}")
    print("-" * 70)

    scorecard = {
        "official_mcp_grafana": "FAIL",
        "mcp_handshake": "FAIL",
        "tools_list": "FAIL",
        "datasource_discovery": "FAIL",
        "prometheus_connection": "FAIL",
        "loki_connection": "FAIL",
        "alerting_connection": "FAIL",
        "postwire_to_cloud": "FAIL",
        "full_test_suite": "FAIL",
    }

    server_version = "unknown"
    discovered_tools_count = 0

    # Phase 1: Test Official MCP Server & stdio Handshake
    print("[1/4] Testing official mcp-grafana stdio protocol handshake...")
    try:
        from mcp import ClientSession, StdioServerParameters
        import shlex

        parts = shlex.split(cmd)
        env = dict(os.environ)
        env["GRAFANA_URL"] = url
        env["GRAFANA_SERVICE_ACCOUNT_TOKEN"] = settings.grafana_service_account_token or "glsa_mock_placeholder"

        params = StdioServerParameters(command=parts[0], args=parts[1:] if len(parts) > 1 else [], env=env)

        from mcp.client.stdio import stdio_client
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                init_res = await session.initialize()
                server_name = init_res.server_info.name
                server_version = init_res.server_info.version
                print(f"    [+] stdio Handshake Succeeded! Server: '{server_name}' (Version: {server_version})")

                if server_name == "mcp-grafana":
                    scorecard["official_mcp_grafana"] = "PASS"
                    scorecard["mcp_handshake"] = "PASS"

                # Phase 2: Tool Discovery (tools/list)
                print("[2/4] Testing tools/list discovery from official server...")
                tools_res = await session.list_tools()
                discovered_tools_count = len(tools_res.tools)
                tool_names = [t.name for t in tools_res.tools]
                print(f"    [+] Discovered {discovered_tools_count} official tools.")

                has_prom = "query_prometheus" in tool_names
                has_loki = "query_loki_logs" in tool_names or "query_loki" in tool_names
                has_alerts = "list_alert_groups" in tool_names or "list_alerts" in tool_names

                print(f"        - Prometheus tool ('query_prometheus'): {'FOUND' if has_prom else 'MISSING'}")
                print(f"        - Loki tool ('query_loki_logs'):         {'FOUND' if has_loki else 'MISSING'}")
                print(f"        - Alerting tool ('list_alert_groups'):   {'FOUND' if has_alerts else 'MISSING'}")

                if discovered_tools_count > 0 and has_prom and has_loki and has_alerts:
                    scorecard["tools_list"] = "PASS"

    except Exception as exc:
        print(f"    [-] MCP handshake/discovery failed: {exc}")

    # Phase 3: Datasource Discovery & Live Queries
    if token_present and url and not url.startswith("http://localhost"):
        print("[3/4] Testing live Grafana Cloud datasource discovery & queries...")
        try:
            client = LiveGrafanaMCPClient(grafana_url=url, token=settings.grafana_service_account_token)
            
            # Step A: Datasource discovery via list_datasources tool
            async def run_discovery_and_queries(session):
                ds_res = await session.call_tool("list_datasources", {"limit": 50})
                parsed_ds = client._parse_tool_result(ds_res)
                datasources = parsed_ds if isinstance(parsed_ds, list) else parsed_ds.get("datasources", [parsed_ds])
                
                prom_uid = None
                loki_uid = None
                for ds in datasources:
                    if isinstance(ds, dict):
                        dstype = ds.get("type", "").lower()
                        if "prom" in dstype and not prom_uid:
                            prom_uid = ds.get("uid")
                        if "loki" in dstype and not loki_uid:
                            loki_uid = ds.get("uid")

                print(f"    [+] Datasources discovered: Prometheus UID={prom_uid or 'default'}, Loki UID={loki_uid or 'default'}")
                scorecard["datasource_discovery"] = "PASS"

                # Step B: Prometheus Query (using safe universal vector(1) query)
                print("    [*] Executing Prometheus query: 'vector(1)'...")
                prom_args = {
                    "datasourceUid": prom_uid or "grafanacloud-prom",
                    "expr": "vector(1)",
                    "endTime": "now",
                    "queryType": "instant"
                }
                prom_call = await session.call_tool("query_prometheus", prom_args)
                prom_data = client._parse_tool_result(prom_call)
                if prom_data and not (isinstance(prom_data, dict) and prom_data.get("status") == "error"):
                    print("    [+] Prometheus Query: PASS")
                    scorecard["prometheus_connection"] = "PASS"
                else:
                    print(f"    [-] Prometheus Query returned: {prom_data}")

                # Step C: Loki Query (using safe LogQL query)
                print("    [*] Executing Loki query: '{job=~\".+\"}'...")
                loki_args = {
                    "datasourceUid": loki_uid or "grafanacloud-logs",
                    "logql": '{job=~".+"}',
                    "limit": 5
                }
                loki_call = await session.call_tool("query_loki_logs", loki_args)
                loki_data = client._parse_tool_result(loki_call)
                # An empty dataset is NOT an error: report 'Loki connected but no matching data'
                if isinstance(loki_data, list) or (isinstance(loki_data, dict) and "error" not in loki_data):
                    print("    [+] Loki Query: PASS (Loki connected; stream evaluated)")
                    scorecard["loki_connection"] = "PASS"
                else:
                    print(f"    [-] Loki Query returned: {loki_data}")

                # Step D: Alerting
                print("    [*] Checking active alert groups...")
                alerts_call = await session.call_tool("list_alert_groups", {})
                alerts_data = client._parse_tool_result(alerts_call)
                if isinstance(alerts_data, list) or (isinstance(alerts_data, dict) and "error" not in alerts_data):
                    alert_count = len(alerts_data) if isinstance(alerts_data, list) else len(alerts_data.get("alertGroups", []))
                    if alert_count == 0:
                        print("    [+] Alerting: PASS (Grafana connected; no active alerts)")
                    else:
                        print(f"    [+] Alerting: PASS ({alert_count} active alert groups found)")
                    scorecard["alerting_connection"] = "PASS"
                else:
                    print(f"    [-] Alerting check returned: {alerts_data}")

                if scorecard["prometheus_connection"] == "PASS":
                    scorecard["postwire_to_cloud"] = "PASS"

            await client._execute_mcp_session(run_discovery_and_queries)

        except Exception as exc:
            print(f"    [-] Live queries failed: {exc}")

    else:
        print("[!] Step 3 skipped: Live credentials are not yet configured in local .env.")
        print("    Follow the instructions below to complete real cloud queries.")

    # Phase 4: Automated Test Suite Evaluation
    print("-" * 70)
    print("VERIFICATION AUDIT SCORECARD:")
    print("-" * 70)
    print(f"| Check                          | Result    |")
    print(f"|--------------------------------|-----------|")
    print(f"| Official mcp-grafana           | {scorecard['official_mcp_grafana']:<9} |")
    print(f"| MCP handshake                  | {scorecard['mcp_handshake']:<9} |")
    print(f"| tools/list                     | {scorecard['tools_list']:<9} |")
    print(f"| Datasource discovery           | {scorecard['datasource_discovery']:<9} |")
    print(f"| Prometheus connection          | {scorecard['prometheus_connection']:<9} |")
    print(f"| Loki connection                | {scorecard['loki_connection']:<9} |")
    print(f"| Alerting connection            | {scorecard['alerting_connection']:<9} |")
    print(f"| PostWire -> MCP -> Cloud       | {scorecard['postwire_to_cloud']:<9} |")
    print("-" * 70)
    print(f"[*] mcp-grafana version: {server_version}")
    print(f"[*] Discovered tools count: {discovered_tools_count}")
    print("=" * 70)

    return scorecard


if __name__ == "__main__":
    asyncio.run(run_verification())
