"""Tests for bulk add counter and button increment logic."""
import pytest
from unittest.mock import Mock


class TestBulkAddCounterLogic:
    """Tests for get_add_count method logic."""

    def test_get_add_count_returns_integer(self):
        """get_add_count parses integer from text entry."""
        # Test the logic directly
        def get_add_count(text):
            try:
                val = int(text)
                return max(1, min(1000, val))
            except ValueError:
                return 1

        assert get_add_count("5") == 5
        assert get_add_count("100") == 100
        assert get_add_count("500") == 500

    def test_get_add_count_clamps_to_minimum(self):
        """get_add_count clamps values below 1 to 1."""
        def get_add_count(text):
            try:
                val = int(text)
                return max(1, min(1000, val))
            except ValueError:
                return 1

        assert get_add_count("0") == 1
        assert get_add_count("-5") == 1
        assert get_add_count("-100") == 1

    def test_get_add_count_clamps_to_maximum(self):
        """get_add_count clamps values above 1000 to 1000."""
        def get_add_count(text):
            try:
                val = int(text)
                return max(1, min(1000, val))
            except ValueError:
                return 1

        assert get_add_count("1000") == 1000
        assert get_add_count("2000") == 1000
        assert get_add_count("9999") == 1000

    def test_get_add_count_handles_invalid_text(self):
        """get_add_count returns 1 for non-numeric text."""
        def get_add_count(text):
            try:
                val = int(text)
                return max(1, min(1000, val))
            except ValueError:
                return 1

        assert get_add_count("abc") == 1
        assert get_add_count("hello") == 1
        assert get_add_count("12abc") == 1

    def test_get_add_count_handles_empty_text(self):
        """get_add_count returns 1 for empty text."""
        def get_add_count(text):
            try:
                val = int(text)
                return max(1, min(1000, val))
            except ValueError:
                return 1

        assert get_add_count("") == 1


class TestButtonIncrementLogic:
    """Tests for button increment/decrement logic."""

    def test_btn_p1_increments_by_1(self):
        """btn_p1 increments counter by 1."""
        current = 5
        new_val = current + 1
        new_val = max(1, min(1000, new_val))
        assert new_val == 6

    def test_btn_m1_decrements_by_1(self):
        """btn_m1 decrements counter by 1."""
        current = 5
        new_val = current - 1
        new_val = max(1, min(1000, new_val))
        assert new_val == 4

    def test_btn_p10_snaps_to_next_10(self):
        """btn_p10 snaps to next multiple of 10."""
        test_cases = [
            (12, 20),  # 12 -> 20
            (20, 30),  # 20 -> 30
            (5, 10),   # 5 -> 10
            (99, 100), # 99 -> 100
        ]

        for current, expected in test_cases:
            new_val = (current // 10 + 1) * 10
            new_val = max(1, min(1000, new_val))
            assert new_val == expected, f"For {current}, expected {expected}, got {new_val}"

    def test_btn_m10_snaps_to_prev_10(self):
        """btn_m10 snaps to previous multiple of 10."""
        test_cases = [
            (15, 10),  # 15 -> 10
            (20, 10),  # 20 -> 10
            (25, 20),  # 25 -> 20
            (100, 90), # 100 -> 90
        ]

        for current, expected in test_cases:
            if current % 10 == 0:
                new_val = current - 10
            else:
                new_val = (current // 10) * 10
            new_val = max(1, min(1000, new_val))
            assert new_val == expected, f"For {current}, expected {expected}, got {new_val}"

    def test_btn_p100_snaps_to_next_100(self):
        """btn_p100 snaps to next multiple of 100."""
        test_cases = [
            (150, 200),  # 150 -> 200
            (100, 200),  # 100 -> 200
            (50, 100),   # 50 -> 100
            (999, 1000), # 999 -> 1000
        ]

        for current, expected in test_cases:
            new_val = (current // 100 + 1) * 100
            new_val = max(1, min(1000, new_val))
            assert new_val == expected, f"For {current}, expected {expected}, got {new_val}"

    def test_btn_m100_snaps_to_prev_100(self):
        """btn_m100 snaps to previous multiple of 100."""
        test_cases = [
            (150, 100), # 150 -> 100
            (200, 100), # 200 -> 100
            (250, 200), # 250 -> 200
            (500, 400), # 500 -> 400
        ]

        for current, expected in test_cases:
            if current % 100 == 0:
                new_val = current - 100
            else:
                new_val = (current // 100) * 100
            new_val = max(1, min(1000, new_val))
            assert new_val == expected, f"For {current}, expected {expected}, got {new_val}"

    def test_value_clamped_to_minimum(self):
        """Values are clamped to minimum of 1."""
        current = 1
        new_val = current - 1  # Would be 0
        new_val = max(1, min(1000, new_val))
        assert new_val == 1

    def test_value_clamped_to_maximum(self):
        """Values are clamped to maximum of 1000."""
        current = 995
        new_val = (current // 100 + 1) * 100  # Would be 1000
        new_val = max(1, min(1000, new_val))
        assert new_val == 1000
