import asyncio
import socket
from datetime import datetime, timezone

import httpx
import pytest
import pytest_asyncio
import socketio
import uvicorn

from app.main import app
from app.services.socket_service import emit_price_update, emit_turbo_triggered


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest_asyncio.fixture(scope="function")
async def live_server_url():
    port = _get_free_port()
    config = uvicorn.Config(app=app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)

    task = asyncio.create_task(server.serve())

    deadline = asyncio.get_running_loop().time() + 10
    healthy = False
    while asyncio.get_running_loop().time() < deadline:
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(f"http://127.0.0.1:{port}/health", timeout=0.5)
            if res.status_code == 200:
                healthy = True
                break
        except Exception:
            await asyncio.sleep(0.05)

    if not healthy:
        server.should_exit = True
        await task
        raise RuntimeError("Live test server could not start in time")

    yield f"http://127.0.0.1:{port}"

    server.should_exit = True
    await task


@pytest.mark.asyncio
async def test_realtime_price_and_turbo_sync_to_multiple_clients(live_server_url: str):
    auction_id = 2026

    client_one = socketio.AsyncClient()
    client_two = socketio.AsyncClient()

    client_one_events = {"price_update": [], "turbo_triggered": []}
    client_two_events = {"price_update": [], "turbo_triggered": []}

    @client_one.on("price_update")
    async def _client_one_price_update(payload):
        client_one_events["price_update"].append(payload)

    @client_one.on("turbo_triggered")
    async def _client_one_turbo(payload):
        client_one_events["turbo_triggered"].append(payload)

    @client_two.on("price_update")
    async def _client_two_price_update(payload):
        client_two_events["price_update"].append(payload)

    @client_two.on("turbo_triggered")
    async def _client_two_turbo(payload):
        client_two_events["turbo_triggered"].append(payload)

    await client_one.connect(live_server_url, socketio_path="socket.io")
    await client_two.connect(live_server_url, socketio_path="socket.io")

    await client_one.emit("subscribe_auction", {"auction_id": auction_id})
    await client_two.emit("subscribe_auction", {"auction_id": auction_id})
    await asyncio.sleep(0.1)

    await emit_price_update(
        auction_id=auction_id,
        current_price="99.90",
        details={"stage": "normal", "drop_count": 1},
    )
    await emit_turbo_triggered(
        auction_id=auction_id,
        turbo_started_at=datetime.now(timezone.utc),
        remaining_minutes=12.5,
    )

    await asyncio.sleep(0.2)

    assert len(client_one_events["price_update"]) == 1
    assert len(client_two_events["price_update"]) == 1
    assert len(client_one_events["turbo_triggered"]) == 1
    assert len(client_two_events["turbo_triggered"]) == 1

    assert client_one_events["price_update"][0]["auction_id"] == auction_id
    assert client_two_events["price_update"][0]["auction_id"] == auction_id
    assert client_one_events["turbo_triggered"][0]["auction_id"] == auction_id
    assert client_two_events["turbo_triggered"][0]["auction_id"] == auction_id

    await client_one.disconnect()
    await client_two.disconnect()
