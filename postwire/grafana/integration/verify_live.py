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
    print("PostWire — Milestone 2B: Grafana Cloud MCP Verification")
    print("=" * 70)

    # Task 1 & 2: Command and binary check
    cmd = settings.grafana_mcp_command
    url = settings.grafana_url
    token_present = bool(settings.grafana_service_account_token)
    masked_token = (
        f"{settings.grafana_service_account_token[:6]}...{settings.grafana_service_account_token[-4:]}"
        if token_present and len(settings.grafana_service_account_token) > 10
        else ("***PROVIDED***" if token_present else "NOT CONFIGURED")
    )

    print(f"[*] Configured Command: {cmd}")
    print(f"[*] Target Grafana URL: {url}")
    print(f"[*] Service Account Token: {masked_token}")
    print("-" * 70)

    results = {
        "mcp_server_verified": "FAIL",
        "mcp_initialization": "FAIL",
        "tools_list": "FAIL",
        "grafana_cloud_connection": "FAIL",
        "prometheus_query": "FAIL",
        "loki_query": "FAIL",
        "active_alerts": "FAIL",
    }

    if not token_present:
        print("[!] GRAFANA_SERVICE_ACCOUNT_TOKEN is not set.")
        print("    Please set GRAFANA_URL and GRAFANA_SERVICE_ACCOUNT_TOKEN in .env to verify live queries.")
        print("-" * 70)

    try:
        client = LiveGrafanaMCPClient(
            grafana_url=url if token_present else "https://grafana.com",
            token=settings.grafana_service_account_token or "glsa_test_token_verification"
        )
    except Exception as exc:
        print(f"[!] Client initialization error: {exc}")
        return results

    # Test Stdio Handshake & Tool Discovery
    print("[1/4] Testing official mcp-grafana stdio protocol handshake...")
    try:
        from mcp import ClientSession
        from mcp.client.stdio import stdio_client

        params = client._get_server_params()
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                init_res = await session.initialize()
                server_name = init_res.server_info.name
                server_ver = init_res.server_info.version
                print(f"    [+] Handshake Succeeded! Server: '{server_name}' (Version: {server_ver})")
                
                if server_name == "mcp-grafana":
                    results["mcp_server_verified"] = "PASS"
                    results["mcp_initialization"] = "PASS"

                print("[2/4] Testing tools/list discovery from official server...")
                tools_res = await session.list_tools()
                tool_names = [t.name for t in tools_res.tools]
                print(f"    [+] Discovered {len(tool_names)} official tools.")
                
                # Check for core observability tools
                has_prom = "query_prometheus" in tool_names
                has_loki = "query_loki_logs" in tool_names or "query_loki" in tool_names
                has_alerts = "list_alert_groups" in tool_names or "list_alerts" in tool_names

                print(f"        - Prometheus tool ('query_prometheus'): {'FOUND' if has_prom else 'MISSING'}")
                print(f"        - Loki tool ('query_loki_logs'): {'FOUND' if has_loki else 'MISSING'}")
                print(f"        - Alerting tool ('list_alert_groups'): {'FOUND' if has_alerts else 'MISSING'}")

                if len(tool_names) > 0:
                    results["tools_list"] = "PASS"

    except Exception as exc:
        print(f"    [-] MCP handshake/discovery failed: {exc}")

    # If real token is configured, test live queries against Grafana Cloud
    if token_present:
        print("[3/4] Testing live Grafana Cloud Prometheus query...")
        try:
            prom_res = await client.query_prometheus("up")
            if prom_res.get("status") == "success":
                print("    [+] Prometheus Query Succeeded!")
                results["prometheus_query"] = "PASS"
                results["grafana_cloud_connection"] = "PASS"
            else:
                print(f"    [-] Prometheus Query returned: {prom_res}")
        except Exception as exc:
            print(f"    [-] Prometheus Query failed: {exc}")

        print("[4/4] Testing live Grafana Cloud Loki log query & Alerts...")
        try:
            loki_res = await client.query_loki('{job=~".+"}', limit=5)
            if isinstance(loki_res, list) and not (len(loki_res) == 1 and loki_res[0].get("status") == "error"):
                print("    [+] Loki Query Succeeded!")
                results["loki_query"] = "PASS"
            else:
                print(f"    [-] Loki Query returned: {loki_res}")
        except Exception as exc:
            print(f"    [-] Loki Query failed: {exc}")

        try:
            alerts_res = await client.list_active_alerts()
            if isinstance(alerts_res, list) and not (len(alerts_res) == 1 and alerts_res[0].get("status") == "error"):
                print("    [+] Active Alerts Query Succeeded!")
                results["active_alerts"] = "PASS"
            else:
                print(f"    [-] Active Alerts returned: {alerts_res}")
        except Exception as exc:
            print(f"    [-] Active Alerts Query failed: {exc}")

    else:
        print("[!] Skipping live queries 3 & 4 because GRAFANA_SERVICE_ACCOUNT_TOKEN is not configured.")

    print("\n" + "=" * 70)
    print("VERIFICATION SCORECARD:")
    print(f"  * Official mcp-grafana binary:   {results['mcp_server_verified']}")
    print(f"  * MCP stdio initialization:     {results['mcp_initialization']}")
    print(f"  * tools/list discovery:          {results['tools_list']}")
    print(f"  * Grafana Cloud connection:     {results['grafana_cloud_connection']}")
    print(f"  * Prometheus query:              {results['prometheus_query']}")
    print(f"  * Loki query:                    {results['loki_query']}")
    print(f"  * active alerts:                 {results['active_alerts']}")
    print("=" * 70)

    return results


if __name__ == "__main__":
    asyncio.run(run_verification())
