import pytest
from hypothesis import given, strategies as st

from processor import (
    parse_walk_schedule,
    compute_pace_per_pet,
    lookup_temperament_surcharge,
)


# --------------------------------------------------
# 1. FUZZ TESTING - SCHEDULE INPUT
# --------------------------------------------------

@given(data=st.one_of(st.text(), st.none()))
def test_parse_walk_schedule_handles_arbitrary_text(data):
    try:
        result = parse_walk_schedule(data)
        assert isinstance(result, str)
    except ValueError:
        pass


# --------------------------------------------------
# 2. FUZZ TESTING - PACE CALCULATION
# --------------------------------------------------

@given(data=st.one_of(st.text(), st.none()))
def test_compute_pace_per_pet_handles_arbitrary_text(data):
    try:
        result = compute_pace_per_pet(data)
        assert isinstance(result, (int, float))
    except ValueError:
        pass


# --------------------------------------------------
# 3. FUZZ TESTING - TEMPERAMENT SURCHARGE
# --------------------------------------------------

@given(data=st.one_of(st.text(), st.none()))
def test_lookup_temperament_surcharge_handles_arbitrary_text(data):
    try:
        result = lookup_temperament_surcharge(data)
        assert isinstance(result, (int, float))
    except ValueError:
        pass


# --------------------------------------------------
# 4. PROPERTY-BASED TESTING - VALID INPUTS
# --------------------------------------------------

@given(
    pets=st.integers(min_value=1, max_value=20),
    minutes=st.integers(min_value=1, max_value=180),
    weekend=st.sampled_from(["YES", "NO"])
)
def test_valid_schedule_values(pets, minutes, weekend):
    result = parse_walk_schedule(f"{pets}-{minutes}-{weekend}")
    assert isinstance(result, str)
    assert "Walk:" in result
    assert "Total $" in result


@given(
    minutes=st.floats(
        min_value=1,
        max_value=500,
        allow_nan=False,
        allow_infinity=False
    ),
    pets=st.floats(
        min_value=1,
        max_value=50,
        allow_nan=False,
        allow_infinity=False
    )
)
def test_valid_pace_values(minutes, pets):
    result = compute_pace_per_pet(f"{minutes}/{pets}")
    assert isinstance(result, float)
    assert result >= 0


# --------------------------------------------------
# 5. KNOWN TEMPERAMENT CODES
# --------------------------------------------------

@given(
    code=st.sampled_from([
        "CALM",
        "PLYFUL",
        "REACTIVE",
        "AGGRESSIVE"
    ])
)
def test_known_temperament_codes(code):
    assert lookup_temperament_surcharge(code) in (
        0.0, 5.0, 12.0, 20.0
    )


# --------------------------------------------------
# 6. INVALID SCHEDULE INPUTS
# --------------------------------------------------

@pytest.mark.parametrize(
    "data",
    [
        "",
        "abc",
        "1-",
        "1-30",
        "1-30-MAYBE",
        "0-30-YES",
        "-1-30-YES",
        "2-0-YES",
        "2-30-YES-extra",
        "two-30-YES",
        "2-thirty-YES",
        "2-30-NOPE",
    ]
)
def test_invalid_schedules_are_rejected(data):
    with pytest.raises(ValueError):
        parse_walk_schedule(data)


# --------------------------------------------------
# 7. INVALID PACE INPUTS
# --------------------------------------------------

@pytest.mark.parametrize(
    "data",
    [
        "",
        "abc",
        "10",
        "10/",
        "/2",
        "0/2",
        "10/0",
        "-10/2",
        "10/-2",
        "nan/2",
        "inf/2",
        "10/inf",
        "10/2/3",
        "ten/two",
    ]
)
def test_invalid_metrics_are_rejected(data):
    with pytest.raises(ValueError):
        compute_pace_per_pet(data)


# --------------------------------------------------
# 8. INVALID TEMPERAMENT INPUTS
# --------------------------------------------------

@pytest.mark.parametrize(
    "data",
    [
        "",
        "UNKNOWN",
        "XYZ",
        "BAD",
        " ",
    ]
)
def test_invalid_temperament_is_rejected(data):
    with pytest.raises(ValueError):
        lookup_temperament_surcharge(data)


# --------------------------------------------------
# 9. NON-STRING INPUT VALIDATION
# --------------------------------------------------

@pytest.mark.parametrize(
    "function",
    [
        parse_walk_schedule,
        compute_pace_per_pet,
        lookup_temperament_surcharge,
    ]
)
def test_non_string_inputs_are_rejected(function):
    with pytest.raises(ValueError):
        function(None)
        
