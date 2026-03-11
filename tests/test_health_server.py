import json
import socket
import threading
import unittest
from urllib.request import urlopen

from packages.shared.config.settings import ServiceSettings
from packages.shared.runtime.http_service import create_http_server


class HealthServerTests(unittest.TestCase):
    @staticmethod
    def _find_free_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])

    def setUp(self) -> None:
        self.port = self._find_free_port()
        settings = ServiceSettings(
            service_name="test-service",
            host="127.0.0.1",
            port=self.port,
            environment="test",
            app_version="0.0.1",
        )
        self.server = create_http_server(settings)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_health_endpoint_returns_expected_payload(self) -> None:
        with urlopen(f"http://127.0.0.1:{self.port}/health", timeout=3) as response:
            body = response.read().decode("utf-8")
            payload = json.loads(body)
            self.assertEqual(response.status, 200)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["service"], "test-service")
            self.assertEqual(payload["environment"], "test")
            self.assertEqual(payload["version"], "0.0.1")


if __name__ == "__main__":
    unittest.main()
