import os
import json
import unittest
from functools import wraps
from collections.abc import Iterable
import logging

from pathlib import Path

import settings

settings.LOG_FILE = ""

from ip2w_app import application


class TestIp2w(unittest.TestCase):

    def test_ip2w_app(self):
        env = {
            "PATH_INFO": "/",
            "REMOTE_ADDR": "8.8.8.8"
        }

        def start_request(status, headers):
            self.assertEqual(status, "200 OK")
            headers = dict(headers)

            self.assertIn("Content-Type", headers.keys())
            self.assertIn("Content-Length", headers.keys())
            self.assertEqual(headers["Content-Type"], "application/json")
            self.assertRegex(headers["Content-Length"], r'^\d+$')

        result = application(env, start_request)

        self.assertTrue(isinstance(result, Iterable))

        response = b""

        for data in result:
            response += data

        response = json.loads(response)

        self.assertIsNotNone(response.get("city"))
        self.assertIsInstance(response.get('city'), str)

        self.assertIsNotNone(response.get("temp"))
        self.assertIsInstance(response.get('temp'), str)
        self.assertRegex(response.get('temp'), r'^[-+]?\d*\.?\d*$')
        
        self.assertIsNotNone(response.get("conditions"))
        self.assertIsInstance(response.get('conditions'), str)

if __name__ == "__main__":
    unittest.main()
