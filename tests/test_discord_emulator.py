import json

import httpx
import pytest
import websockets
from aiohttp import web

from discord_emulator import DiscordEmulator


@pytest.mark.asyncio
async def test_gateway_ready_and_message_create():
    emulator = DiscordEmulator()
    app = emulator.create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 9010)
    await site.start()

    try:
        async with websockets.connect("ws://127.0.0.1:9010/gateway") as ws:
            hello = json.loads(await ws.recv())
            assert hello["op"] == 10
            await ws.send(json.dumps({"op": 2}))
            ready = json.loads(await ws.recv())
            assert ready["t"] == "READY"
            async with httpx.AsyncClient(base_url="http://127.0.0.1:9010") as client:
                r = await client.post(
                    "/api/v10/channels/10/messages", json={"content": "hi"}
                )
                assert r.status_code == 200
            event = json.loads(await ws.recv())
            assert event["t"] == "MESSAGE_CREATE"
    finally:
        await runner.cleanup()


@pytest.mark.asyncio
async def test_post_message_unknown_channel():
    emulator = DiscordEmulator()
    app = emulator.create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 9011)
    await site.start()

    try:
        async with httpx.AsyncClient(base_url="http://127.0.0.1:9011") as client:
            r = await client.post(
                "/api/v10/channels/999/messages", json={"content": "x"}
            )
            assert r.status_code == 404
    finally:
        await runner.cleanup()
