# MIT License
# Discord Bot Emulator

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Dict, List

from aiohttp import WSMsgType, web


class DiscordEmulator:
    """In-memory Discord HTTP and Gateway emulator."""

    def __init__(self) -> None:
        self.guilds: Dict[str, Dict] = {
            "1": {
                "id": "1",
                "name": "Test Guild",
                "channels": [
                    {
                        "id": "10",
                        "name": "general",
                        "type": 0,
                    }
                ],
            }
        }
        self.messages: Dict[str, Dict[str, Dict]] = {}
        self.websockets: List[web.WebSocketResponse] = []
        self.heartbeat_interval = 5000
        self.sequence = 0

    def _rate_headers(self) -> Dict[str, str]:
        return {
            "X-RateLimit-Bucket": "emulator",
            "X-RateLimit-Limit": "5",
            "X-RateLimit-Remaining": "5",
        }

    async def gateway(self, request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.websockets.append(ws)
        await ws.send_json(
            {"op": 10, "d": {"heartbeat_interval": self.heartbeat_interval}}
        )

        try:
            async for msg in ws:
                if msg.type != WSMsgType.TEXT:
                    continue
                data = json.loads(msg.data)
                op = data.get("op")
                if op == 1:  # Heartbeat
                    await ws.send_json({"op": 11})
                elif op == 2:  # Identify
                    self.sequence += 1
                    payload = {
                        "op": 0,
                        "t": "READY",
                        "s": self.sequence,
                        "d": {
                            "user": {"id": "999", "username": "bot"},
                            "guilds": [{"id": g["id"]} for g in self.guilds.values()],
                        },
                    }
                    await ws.send_json(payload)
        finally:
            self.websockets.remove(ws)
        return ws

    async def _broadcast(self, event: Dict) -> None:
        if not self.websockets:
            return
        for ws in list(self.websockets):
            try:
                await ws.send_json(event)
            except ConnectionResetError:
                self.websockets.remove(ws)

    async def get_channels(self, request: web.Request) -> web.Response:
        gid = request.match_info["guild_id"]
        guild = self.guilds.get(gid)
        if not guild:
            return web.json_response({"message": "Unknown Guild"}, status=404)
        return web.json_response(guild["channels"], headers=self._rate_headers())

    async def post_message(self, request: web.Request) -> web.Response:
        cid = request.match_info["channel_id"]
        if not any(cid == c["id"] for g in self.guilds.values() for c in g["channels"]):
            return web.json_response({"message": "Unknown Channel"}, status=404)
        data = await request.json()
        message_id = str(uuid.uuid4())
        msg = {
            "id": message_id,
            "channel_id": cid,
            "content": data.get("content", ""),
        }
        self.messages.setdefault(cid, {})[message_id] = msg
        await self._broadcast({"op": 0, "t": "MESSAGE_CREATE", "d": msg})
        return web.json_response(msg, headers=self._rate_headers())

    async def patch_message(self, request: web.Request) -> web.Response:
        cid = request.match_info["channel_id"]
        mid = request.match_info["message_id"]
        channel = self.messages.get(cid, {})
        if mid not in channel:
            return web.json_response({"message": "Unknown Message"}, status=404)
        data = await request.json()
        channel[mid].update({"content": data.get("content", "")})
        return web.json_response(channel[mid], headers=self._rate_headers())

    async def delete_message(self, request: web.Request) -> web.Response:
        cid = request.match_info["channel_id"]
        mid = request.match_info["message_id"]
        channel = self.messages.get(cid, {})
        if mid not in channel:
            return web.json_response({"message": "Unknown Message"}, status=404)
        channel.pop(mid)
        return web.json_response({}, headers=self._rate_headers())

    async def post_interaction(self, request: web.Request) -> web.Response:
        data = await request.json()
        return web.json_response(
            {"type": 4, "data": data}, headers=self._rate_headers()
        )

    async def post_webhook(self, request: web.Request) -> web.Response:
        return await self.post_message(request)

    def create_app(self) -> web.Application:
        app = web.Application()
        app.router.add_get("/gateway", self.gateway)
        app.router.add_get("/api/v10/guilds/{guild_id}/channels", self.get_channels)
        app.router.add_post(
            "/api/v10/channels/{channel_id}/messages", self.post_message
        )
        app.router.add_patch(
            "/api/v10/channels/{channel_id}/messages/{message_id}", self.patch_message
        )
        app.router.add_delete(
            "/api/v10/channels/{channel_id}/messages/{message_id}", self.delete_message
        )
        app.router.add_post("/api/v10/interactions", self.post_interaction)
        app.router.add_post("/api/v10/webhooks/{app_id}/{token}", self.post_webhook)
        return app


async def run(port: int = 8001) -> None:
    emulator = DiscordEmulator()
    runner = web.AppRunner(emulator.create_app())
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", port)
    await site.start()
    print(f"Discord emulator running on http://127.0.0.1:{port}")
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(run())
