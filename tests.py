import json
from unittest import TestCase
from functools import wraps
from collections.abc import Iterable

from ip2w_app import application


class TestIp2w(TestCase):

    def test_ip2w_app(self):
        env = {
            "PATH_INFO": "/",
            "REMOTE_ADDR": "8.8.8.8"
        }

        def start_request(status, headers):
            self.assertEqual(status, "200 OK")
            self.assertTrue(hasattr(headers, "Content-Type"))
            self.assertTrue(hasattr(headers, "Content-Length"))
            self.assertEqual(headers["Content-Type"], "application/json")

        result = application(env, start_request)

        self.assertTrue(isinstance(result, Iterable))

        response = b""

        for data in result:
            response += data

        response = json.loads(response)

        self.assertIsNotNone(response.get("city"))
        self.assertIsNotNone(response.get("temp"))
        self.assertIsNotNone(response.get("conditions"))
