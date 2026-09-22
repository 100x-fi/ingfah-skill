import io
import json
import os
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from scripts import ingfah_api


class FakeResponse:
    def __init__(self, body, status=200, content_type="application/json"):
        self.body = body
        self.status = status
        self.headers = {"Content-Type": content_type}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.body

    def getcode(self):
        return self.status


class IngfahApiTests(unittest.TestCase):
    def test_get_sends_api_key_and_returns_json(self):
        captured = {}

        def open_request(request, timeout):
            captured["request"] = request
            captured["timeout"] = timeout
            return FakeResponse(b'{"status":"success","data":[]}', 200)

        with patch.dict(os.environ, {"INGFAH_API_KEY": "secret-key"}, clear=False), patch(
            "scripts.ingfah_api.urllib.request.urlopen", open_request
        ):
            result = ingfah_api.request("GET", "/client/products")

        self.assertEqual(result.status, 200)
        self.assertEqual(result.body, {"status": "success", "data": []})
        self.assertEqual(captured["request"].get_header("X-api-key"), "secret-key")
        self.assertEqual(captured["request"].full_url, "https://api.ingfah.ai/client/products")

    def test_rejects_route_outside_skill_allowlist(self):
        with patch.dict(os.environ, {"INGFAH_API_KEY": "secret-key"}, clear=False):
            with self.assertRaises(ingfah_api.ClientError):
                ingfah_api.request("GET", "/client/profile")

    def test_mutation_requires_confirmation(self):
        with patch.dict(os.environ, {"INGFAH_API_KEY": "secret-key"}, clear=False), patch(
            "scripts.ingfah_api.urllib.request.urlopen"
        ) as urlopen:
            with self.assertRaises(ingfah_api.ClientError):
                ingfah_api.request("POST", "/client/outbound/batches", {"name": "test"})
            urlopen.assert_not_called()

    def test_confirmation_is_required_for_path_mutations(self):
        with patch.dict(os.environ, {"INGFAH_API_KEY": "secret-key"}, clear=False), patch(
            "scripts.ingfah_api.urllib.request.urlopen",
            return_value=FakeResponse(b'{"status":"success"}', 200),
        ) as urlopen:
            ingfah_api.request(
                "POST", "/client/outbound/batches/7/pause", confirm=True
            )
            request = urlopen.call_args.args[0]
            self.assertEqual(request.get_method(), "POST")

    def test_missing_key_is_clear_and_does_not_make_request(self):
        with patch.dict(os.environ, {}, clear=True), patch(
            "scripts.ingfah_api.urllib.request.urlopen"
        ) as urlopen:
            with self.assertRaisesRegex(ingfah_api.ClientError, "INGFAH_API_KEY"):
                ingfah_api.request("GET", "/client/products")
            urlopen.assert_not_called()

    def test_cli_never_prints_api_key(self):
        secret = "secret-key"
        output = io.StringIO()
        with patch.dict(os.environ, {"INGFAH_API_KEY": secret}, clear=False), patch(
            "scripts.ingfah_api.request",
            return_value=ingfah_api.ApiResponse(200, {"status": "success"}),
        ):
            with redirect_stdout(output), redirect_stderr(output):
                self.assertEqual(
                    ingfah_api.main(["GET", "/client/products"]), 0
                )
        self.assertNotIn(secret, output.getvalue())


if __name__ == "__main__":
    unittest.main()
