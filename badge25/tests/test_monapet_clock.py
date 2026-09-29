import importlib.util
from pathlib import Path
from unittest import mock


MODULE_PATH = (
    Path(__file__).parents[1] / "apps" / "monapet" / "clock.py"
)
SPEC = importlib.util.spec_from_file_location("monapet_clock", MODULE_PATH)
clock = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(clock)


def test_uk_offset_uses_bst_during_summer():
    assert clock.uk_offset_hours((2026, 9, 29, 14, 0, 0, 1, 272)) == 1


def test_uk_offset_changes_at_one_utc_on_last_sunday_in_march():
    assert clock.uk_offset_hours((2026, 3, 29, 0, 59, 0, 6, 88)) == 0
    assert clock.uk_offset_hours((2026, 3, 29, 1, 0, 0, 6, 88)) == 1


def test_uk_offset_changes_at_one_utc_on_last_sunday_in_october():
    assert clock.uk_offset_hours((2026, 10, 25, 0, 59, 0, 6, 298)) == 1
    assert clock.uk_offset_hours((2026, 10, 25, 1, 0, 0, 6, 298)) == 0


def test_clock_is_hidden_until_rtc_has_a_valid_time():
    with mock.patch.object(
        clock.time, "gmtime", return_value=(2021, 1, 1, 0, 0, 0, 4, 1)
    ):
        assert clock.current_time_text() is None
