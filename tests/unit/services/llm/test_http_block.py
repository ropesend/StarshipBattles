"""Verify the autouse `_block_real_http` fixture in tests/conftest.py works.

Without this fixture a buggy test could silently make real HTTP calls,
spending real money and producing flaky results. The fixture replaces
`requests.post` / `requests.get` / etc. with raisers; tests that need
HTTP must explicitly `unittest.mock.patch` them inside their own scope.
"""
from unittest.mock import patch

import pytest
import requests


class TestHttpBlock:
    def test_real_post_is_blocked(self):
        with pytest.raises(RuntimeError, match="Real HTTP forbidden"):
            requests.post("http://example.invalid")

    def test_real_get_is_blocked(self):
        with pytest.raises(RuntimeError, match="Real HTTP forbidden"):
            requests.get("http://example.invalid")

    def test_real_request_is_blocked(self):
        with pytest.raises(RuntimeError, match="Real HTTP forbidden"):
            requests.request("PUT", "http://example.invalid")

    def test_explicit_patch_overrides_block(self):
        """A test that explicitly mocks requests.post wins."""
        sentinel = object()
        with patch("requests.post", return_value=sentinel):
            assert requests.post("http://example.invalid") is sentinel
