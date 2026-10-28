
import pytest
from pet_walking_service import (
    process_walking_routes,
    inspect_gps_collars,
)


@pytest.mark.parametrize("routes, fee, expected", [
    ([], 5, "ZERO_EARNINGS"),
    ([{"route_confirmed": False}], 5, "ZERO_EARNINGS"),
    ([{"route_confirmed": True, "session_type": "bad"}], 5,
     "ZERO_EARNINGS"),
    ([{"route_confirmed": True,
       "walks": [{"num_pets": 0}]}], 5, "ZERO_EARNINGS"),
    ([{"route_confirmed": True,
       "walks": [{"num_pets": 1}]}], 5, "COMPLETED"),
    ([{"route_confirmed": True,
       "walks": [{"num_pets": 4}]}], 5, "COMPLETED"),
    ([{"route_confirmed": True, "is_weekend": True,
       "walks": [{"num_pets": 1, "needs_meds": True}]}],
     5, "COMPLETED"),
])
def test_route_decisions(routes, fee, expected):
    assert process_walking_routes(routes, fee)["status"] == expected


def test_invalid_input():
    with pytest.raises(ValueError):
        process_walking_routes(None, 5)


def test_negative_fee():
    with pytest.raises(ValueError):
        process_walking_routes([], -1)


def test_long_session_aggression_breaks():
    result = process_walking_routes([{
        "route_confirmed": True,
        "session_type": "standard_60",
        "walks": [{"num_pets": 1, "aggression_alert": True}],
        "is_weekend": True,
    }], 5)
    assert result["total_revenue"] == 5


def test_incident_audit():
    routes = [
        {"route_confirmed": True, "session_type": "bad"}
        for _ in range(5)
    ]
    assert process_walking_routes(routes, 5)["status"] == "INCIDENT_AUDIT"


@pytest.mark.parametrize("matrix, expected", [
    ([], "NO_DATA"),
    ([[30, 40, 25]], "ONLINE"),
    ([[10, 15]], "LOST_SIGNAL_ALERT"),
    ([[10, 30, 10]], "ONLINE"),
    ([[30, 10, 15]], "LOST_SIGNAL_ALERT"),
])
def test_gps_branches(matrix, expected):
    assert inspect_gps_collars(matrix) == expected
