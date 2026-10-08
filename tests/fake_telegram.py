"""Fake only the external HTTP boundary; keep Telegram parsing/handlers real."""
import json

from telegram.request import BaseRequest


class FakeTelegram(BaseRequest):
    def __init__(self):
        self.sent = []
        self.failure = None

    @property
    def read_timeout(self):
        return 5

    async def initialize(self):
        pass

    async def shutdown(self):
        pass

    async def do_request(self, url, method, request_data=None, **kwargs):
        endpoint = url.rsplit("/", 1)[-1]
        params = request_data.parameters if request_data else {}
        if endpoint == "getMe":
            result = {"id": 123456, "is_bot": True, "first_name": "Sunny", "username": "sunny19354_bot"}
        elif endpoint == "sendMessage":
            if self.failure:
                code, description, extra = self.failure
                self.failure = None
                return code, json.dumps({"ok": False, "error_code": code, "description": description, **extra}).encode()
            self.sent.append(params)
            result = {"message_id": len(self.sent), "date": 1900000000,
                      "chat": {"id": int(params["chat_id"]), "type": "private"}, "text": params["text"]}
        elif endpoint == "setMyCommands":
            result = True
        else:
            raise AssertionError("Unexpected Telegram method: " + endpoint)
        return 200, json.dumps({"ok": True, "result": result}).encode()
