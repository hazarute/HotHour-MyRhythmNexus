import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request


def print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def http_request(url: str, method: str = "GET", headers: dict | None = None, timeout: int = 20):
    req = urllib.request.Request(url=url, method=method)
    if headers:
        for key, value in headers.items():
            req.add_header(key, value)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return {
                "ok": True,
                "status": resp.status,
                "headers": dict(resp.headers.items()),
                "body": body,
                "error": None,
            }
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "status": err.code,
            "headers": dict(err.headers.items()) if err.headers else {},
            "body": body,
            "error": f"HTTPError: {err}",
        }
    except Exception as err:
        return {
            "ok": False,
            "status": None,
            "headers": {},
            "body": "",
            "error": f"{type(err).__name__}: {err}",
        }


def find_main_bundle(index_html: str) -> str | None:
    match = re.search(r'/assets/index-[^"\']+\.js', index_html)
    return match.group(0) if match else None


def check_frontend_bundle(frontend_url: str, backend_url: str) -> dict:
    result = {
        "index_ok": False,
        "bundle_ok": False,
        "bundle_url": None,
        "has_backend_url": False,
        "has_localhost": False,
        "error": None,
    }

    index_resp = http_request(frontend_url)
    if not index_resp["ok"]:
        result["error"] = f"Frontend index alınamadı: {index_resp['error']}"
        return result

    result["index_ok"] = True
    bundle_path = find_main_bundle(index_resp["body"])
    if not bundle_path:
        result["error"] = "Main bundle yolu bulunamadı (/assets/index-*.js)."
        return result

    bundle_url = urllib.parse.urljoin(frontend_url.rstrip("/") + "/", bundle_path.lstrip("/"))
    result["bundle_url"] = bundle_url

    js_resp = http_request(bundle_url)
    if not js_resp["ok"]:
        result["error"] = f"Bundle alınamadı: {js_resp['error']}"
        return result

    result["bundle_ok"] = True
    body = js_resp["body"]
    result["has_localhost"] = "127.0.0.1:8000" in body or "localhost:8000" in body
    result["has_backend_url"] = backend_url.rstrip("/") in body
    return result


def check_backend_endpoints(backend_url: str) -> dict:
    checks = {}
    health_url = backend_url.rstrip("/") + "/health"
    auctions_url = backend_url.rstrip("/") + "/api/v1/auctions?include_computed=true"

    checks["health"] = http_request(health_url)
    checks["auctions"] = http_request(auctions_url)
    return checks


def check_cors(backend_url: str, origins: list[str]) -> list[dict]:
    rows = []
    options_url = backend_url.rstrip("/") + "/api/v1/auctions?include_computed=true"
    for origin in origins:
        resp = http_request(
            options_url,
            method="OPTIONS",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )
        allow_origin = resp["headers"].get("Access-Control-Allow-Origin")
        rows.append(
            {
                "origin": origin,
                "status": resp["status"],
                "allow_origin": allow_origin,
                "ok": bool(resp["status"] in (200, 204) and allow_origin == origin),
                "error": resp["error"],
            }
        )
    return rows


def run_railway_logs(service: str, environment: str, lines: int) -> list[str]:
    cmd = [
        "railway",
        "logs",
        "--service",
        service,
        "--environment",
        environment,
        "--lines",
        str(lines),
    ]
    try:
        completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
        output = (completed.stdout or "") + ("\n" + completed.stderr if completed.stderr else "")
        return output.splitlines()
    except FileNotFoundError:
        return ["Railway CLI bulunamadı (railway komutu yok)."]
    except Exception as exc:
        return [f"Railway log çekme hatası: {type(exc).__name__}: {exc}"]


def print_summary(frontend_bundle: dict, backend_checks: dict, cors_rows: list[dict]) -> None:
    print_section("Özet")
    print(f"Frontend index: {'OK' if frontend_bundle['index_ok'] else 'FAIL'}")
    print(f"Frontend bundle: {'OK' if frontend_bundle['bundle_ok'] else 'FAIL'}")
    print(f"Bundle backend URL gömülü: {'EVET' if frontend_bundle['has_backend_url'] else 'HAYIR'}")
    print(f"Bundle localhost izi: {'EVET' if frontend_bundle['has_localhost'] else 'HAYIR'}")
    print(f"Backend /health: {backend_checks['health']['status']} ({'OK' if backend_checks['health']['ok'] else 'FAIL'})")
    print(f"Backend /api/v1/auctions: {backend_checks['auctions']['status']} ({'OK' if backend_checks['auctions']['ok'] else 'FAIL'})")
    cors_ok = all(r["ok"] for r in cors_rows) if cors_rows else True
    print(f"CORS kontrolü: {'OK' if cors_ok else 'FAIL'}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Railway frontend/backend fetch teşhis aracı")
    parser.add_argument("--frontend-url", required=True, help="Örn: https://hothour-frontend.up.railway.app")
    parser.add_argument("--backend-url", required=True, help="Örn: https://hothour-myrhythmnexus-production.up.railway.app")
    parser.add_argument("--origin", action="append", default=[], help="CORS test origin'i (birden fazla verilebilir)")
    parser.add_argument("--railway-service-backend", default="", help="Railway backend service adı")
    parser.add_argument("--railway-service-frontend", default="", help="Railway frontend service adı")
    parser.add_argument("--railway-environment", default="production", help="Railway environment")
    parser.add_argument("--railway-lines", type=int, default=120, help="Railway log satır sayısı")
    args = parser.parse_args()

    frontend_url = args.frontend_url.rstrip("/")
    backend_url = args.backend_url.rstrip("/")

    print_section("1) Frontend Bundle Kontrolü")
    bundle_result = check_frontend_bundle(frontend_url, backend_url)
    print(json.dumps(bundle_result, indent=2, ensure_ascii=False))

    print_section("2) Backend Endpoint Kontrolü")
    backend_checks = check_backend_endpoints(backend_url)
    print(json.dumps(
        {
            "health": {
                "status": backend_checks["health"]["status"],
                "ok": backend_checks["health"]["ok"],
                "error": backend_checks["health"]["error"],
                "body_preview": backend_checks["health"]["body"][:300],
            },
            "auctions": {
                "status": backend_checks["auctions"]["status"],
                "ok": backend_checks["auctions"]["ok"],
                "error": backend_checks["auctions"]["error"],
                "body_preview": backend_checks["auctions"]["body"][:300],
            },
        },
        indent=2,
        ensure_ascii=False,
    ))

    cors_origins = args.origin or [frontend_url]
    print_section("3) CORS Preflight Kontrolü")
    cors_rows = check_cors(backend_url, cors_origins)
    print(json.dumps(cors_rows, indent=2, ensure_ascii=False))

    if args.railway_service_backend:
        print_section("4) Railway Backend Log Örneği")
        lines = run_railway_logs(args.railway_service_backend, args.railway_environment, args.railway_lines)
        for line in lines[-40:]:
            print(line)

    if args.railway_service_frontend:
        print_section("5) Railway Frontend Log Örneği")
        lines = run_railway_logs(args.railway_service_frontend, args.railway_environment, args.railway_lines)
        for line in lines[-40:]:
            print(line)

    print_summary(bundle_result, backend_checks, cors_rows)

    if not bundle_result["index_ok"] or not bundle_result["bundle_ok"]:
        return 2
    if not backend_checks["health"]["ok"] or not backend_checks["auctions"]["ok"]:
        return 3
    if any(not row["ok"] for row in cors_rows):
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
