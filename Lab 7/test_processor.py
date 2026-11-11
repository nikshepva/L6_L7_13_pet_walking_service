from hypothesis import given, settings, strategies as st
import pytest
from processor import parse_walk_schedule, compute_pace_per_pet, lookup_temperament_surcharge

# ValueError is the documented response to malformed input.
# Any unexpected exception type is a fuzzing failure.

@settings(max_examples=200, deadline=None)
@given(st.one_of(st.text(), st.none()))
def test_parse_walk_schedule_handles_arbitrary_text(s):
    try:
        result = parse_walk_schedule(s)
        assert isinstance(result, str) and result.startswith("Walk:")
    except ValueError:
        pass

@settings(max_examples=200, deadline=None)
@given(st.one_of(st.text(), st.none()))
def test_compute_pace_per_pet_handles_arbitrary_text(s):
    try:
        result = compute_pace_per_pet(s)
        assert isinstance(result, float) and result >= 0
    except ValueError:
        pass

@settings(max_examples=200, deadline=None)
@given(st.one_of(st.text(), st.none()))
def test_lookup_temperament_surcharge_handles_arbitrary_text(s):
    try:
        result = lookup_temperament_surcharge(s)
        assert result in (0.0, 5.0, 12.0, 20.0)
    except ValueError:
        pass

@given(pets=st.integers(min_value=1, max_value=20),
       minutes=st.integers(min_value=1, max_value=240),
       weekend=st.sampled_from(["YES", "NO"]))
def test_valid_schedule_values(pets, minutes, weekend):
    result = parse_walk_schedule(f"{pets}-{minutes}-{weekend}")
    assert f"{pets} pets" in result and f"{minutes} mins" in result

@given(minutes=st.floats(min_value=0.01, max_value=10000, allow_nan=False, allow_infinity=False),
       pets=st.floats(min_value=0.01, max_value=100, allow_nan=False, allow_infinity=False))
def test_valid_pace_values(minutes, pets):
    assert compute_pace_per_pet(f"{minutes}/{pets}") >= 0

@given(code=st.sampled_from(["CALM", "PLAYFUL", "REACTIVE", "AGGRESSIVE"]))
def test_known_temperament_codes(code):
    assert lookup_temperament_surcharge(code) in (0.0, 5.0, 12.0, 20.0)

@pytest.mark.parametrize("bad", ["", "1-2", "1-2-YES-extra", "zero-30-NO",
                                 "0-30-YES", "2-0-YES", "2-30-MAYBE", "2--YES"])
def test_invalid_schedules_are_rejected(bad):
    with pytest.raises(ValueError):
        parse_walk_schedule(bad)

@pytest.mark.parametrize("bad", ["", "10", "10/0", "0/2", "abc/2",
                                 "10/2/3", "nan/2", "inf/2"])
def test_invalid_metrics_are_rejected(bad):
    with pytest.raises(ValueError):
        compute_pace_per_pet(bad)

@pytest.mark.parametrize("bad", ["", "UNKNOWN", "XYZ", "  "])
def test_invalid_temperament_is_rejected(bad):
    with pytest.raises(ValueError):
        lookup_temperament_surcharge(bad)

@pytest.mark.parametrize("func", [parse_walk_schedule, compute_pace_per_pet,
                                  lookup_temperament_surcharge])
def test_non_string_inputs_are_rejected(func):
    with pytest.raises(ValueError):
        func(None)
