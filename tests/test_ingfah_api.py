import io
import json
import tempfile
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
        self.assertEqual(
            captured["request"].get_header("User-agent"), f"ingfah-skill/{ingfah_api.__version__}"
        )

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

    def test_json_body_accepts_inline_document(self):
        self.assertEqual(ingfah_api._load_json_body('{"name": "batch"}'), {"name": "batch"})

    def test_json_body_accepts_file_path(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            handle.write('{"name": "from-file"}')
            path = handle.name
        self.addCleanup(os.unlink, path)
        self.assertEqual(ingfah_api._load_json_body(path), {"name": "from-file"})

    def test_json_body_file_error_is_user_safe(self):
        with self.assertRaisesRegex(ingfah_api.ClientError, "could not read JSON body file"):
            ingfah_api._load_json_body("/nonexistent/body.json")

    def test_undocumented_routes_are_rejected(self):
        with patch.dict(os.environ, {"INGFAH_API_KEY": "secret-key"}, clear=False):
            for path in (
                "/client/analytics/summary",
                "/client/text-chats/conversations",
                "/client/text-analytics/summary",
            ):
                with self.assertRaises(ingfah_api.ClientError):
                    ingfah_api.request("GET", path)



    def test_error_detail_is_surfaced(self):
        message = ingfah_api._format_api_error(
            400, {"status": "error", "error": "bad request",
                  "error_detail": "bad request: schedule 0 time_slots is required"}
        )
        self.assertEqual(
            message,
            "Ingfah API returned HTTP 400: bad request: schedule 0 time_slots is required",
        )

    def test_error_detail_absent_falls_back_to_error(self):
        message = ingfah_api._format_api_error(404, {"error": "resource not found"})
        self.assertEqual(message, "Ingfah API returned HTTP 404: resource not found")


    def test_agent_and_postprocessor_write_routes_are_allowed(self):
        for method, path in (
            ("PUT", "/client/agents/my-agent/description"),
            ("PUT", "/client/agents/my-agent/visibility"),
            ("POST", "/client/agents/my-agent/revisions"),
            ("POST", "/client/agents/my-agent/revisions/12/publish"),
            ("DELETE", "/client/agents/my-agent/revisions/12"),
            ("POST", "/client/products/227/postprocessors"),
            ("PUT", "/client/products/227/postprocessors/451"),
            ("DELETE", "/client/products/227/postprocessors/451"),
        ):
            self.assertTrue(ingfah_api._is_allowed(method, path), f"{method} {path}")
            self.assertTrue(ingfah_api._is_mutation(method, path), f"{method} {path}")

    def test_product_detail_read_is_allowed(self):
        self.assertTrue(ingfah_api._is_allowed("GET", "/client/products/227"))
        self.assertFalse(ingfah_api._is_mutation("GET", "/client/products/227"))

    def test_agent_writes_still_require_confirmation(self):
        with patch.dict(os.environ, {"INGFAH_API_KEY": "secret-key"}, clear=False), patch(
            "scripts.ingfah_api.urllib.request.urlopen"
        ) as urlopen:
            for method, path in (
                ("POST", "/client/agents/my-agent/revisions/12/publish"),
                ("DELETE", "/client/products/227/postprocessors/451"),
            ):
                with self.assertRaises(ingfah_api.ClientError):
                    ingfah_api.request(method, path)
            urlopen.assert_not_called()

    def test_unlisted_product_subroutes_stay_rejected(self):
        # There is no GET postprocessors route: a product's postprocessors are
        # read from GET /client/products/{id}. Automations, by contrast, have
        # their own list route, covered below.
        self.assertFalse(ingfah_api._is_allowed("GET", "/client/products/227/postprocessors"))

    def test_automation_routes_are_allowed(self):
        for method, path in (
            ("GET", "/client/products/227/automations"),
            ("POST", "/client/products/227/automations"),
            ("PUT", "/client/products/227/automations/5"),
            ("DELETE", "/client/products/227/automations/5"),
        ):
            self.assertTrue(ingfah_api._is_allowed(method, path), f"{method} {path}")
        # The collection takes no id, and an automation is not deleted by POST.
        self.assertFalse(ingfah_api._is_allowed("POST", "/client/products/227/automations/5"))


    def test_chat_session_recording_routes_are_allowed(self):
        for path in (
            "/client/chat-sessions/abc-123/record",
            "/client/chat-sessions/abc-123/record/download",
            "/client/chat-sessions/abc-123/record/checksum",
        ):
            self.assertTrue(ingfah_api._is_allowed("GET", path), path)
        self.assertFalse(ingfah_api._is_allowed("GET", "/client/chat-sessions/abc-123/record/foo"))
        self.assertFalse(ingfah_api._is_allowed("DELETE", "/client/chat-sessions/abc-123/record"))
        # A test call's recording is dashboard-login only.
        self.assertFalse(ingfah_api._is_allowed("GET", "/client/agents/bot/chat-session-tests/abc-123/record"))

    def test_binary_download_is_kept_as_bytes(self):
        audio = b"OggS\x00\x02\xff\xfe"
        self.assertEqual(ingfah_api._decode_body(audio, "audio/ogg"), audio)
        self.assertEqual(ingfah_api._decode_body(b"a,b\n1,2\n", "text/csv; charset=utf-8"), "a,b\n1,2\n")

    def test_cli_refuses_to_print_binary_response(self):
        response = ingfah_api.ApiResponse(200, b"OggS\xff", "audio/ogg")
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch("scripts.ingfah_api.request", return_value=response), redirect_stdout(stdout), redirect_stderr(stderr):
            code = ingfah_api.main(["GET", "/client/chat-sessions/abc/record/download"])
        self.assertEqual(code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("--output", stderr.getvalue())

    def test_cli_output_saves_exact_bytes_and_will_not_overwrite(self):
        audio = b"OggS\x00\xff\xfe"
        response = ingfah_api.ApiResponse(200, audio, "audio/ogg")
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "call.ogg")
            args = ["GET", "/client/chat-sessions/abc/record/download", "--output", path]
            with patch("scripts.ingfah_api.request", return_value=response) as request, redirect_stdout(io.StringIO()):
                self.assertEqual(ingfah_api.main(args), 0)
                with open(path, "rb") as handle:
                    self.assertEqual(handle.read(), audio)
                with redirect_stderr(io.StringIO()) as stderr:
                    self.assertEqual(ingfah_api.main(args), 1)
                self.assertIn("already exists", stderr.getvalue())
                self.assertEqual(request.call_count, 1)

if __name__ == "__main__":
    unittest.main()
