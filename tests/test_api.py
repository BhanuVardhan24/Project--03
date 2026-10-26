import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from app.main import Handler


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.server.server_address[1]

        cls.thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True,
        )
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, path):
        connection = HTTPConnection(
            "127.0.0.1",
            self.port,
            timeout=5,
        )

        try:
            connection.request("GET", path)
            response = connection.getresponse()

            return (
                response.status,
                response.getheader("Content-Type"),
                json.loads(response.read()),
            )
        finally:
            connection.close()

    def test_health_returns_healthy(self):
        status, content_type, body = self.request("/health")

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(body, {"status": "healthy"})

    def test_version_returns_release_information(self):
        with patch.dict(
            "os.environ",
            {
                "APP_VERSION": "0.1.0-test",
                "GIT_SHA": "test-commit",
            },
        ):
            status, _, body = self.request("/version")

        self.assertEqual(status, 200)
        self.assertEqual(
            body,
            {
                "version": "0.1.0-test",
                "commit": "test-commit",
            },
        )

    def test_unknown_route_returns_not_found(self):
        status, _, body = self.request("/missing")

        self.assertEqual(status, 404)
        self.assertEqual(body, {"error": "not found"})


if __name__ == "__main__":
    unittest.main()