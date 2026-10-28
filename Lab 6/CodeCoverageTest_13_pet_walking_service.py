import pytest
from pet_walking_service import (
    process_walking_routes,
    inspect_gps_collars,
)


def test_single_standard_30_walk():
    routes = [{
        "route_confirmed": True,
        "session_type": "standard_30",
        "is_weekend": False,
        "walks": [{"num_pets": 1}]
    }]
    assert process_walking_routes(routes, 5.0) == {
        "total_revenue": 27.0,
        "status": "COMPLETED",
    }


def test_invalid_routes():
    with pytest.raises(ValueError):
        process_walking_routes("invalid", 5.0)


def test_negative_transport_fee():
    with pytest.raises(ValueError):
        process_walking_routes([], -1)


def test_unconfirmed_route_is_skipped():
    result = process_walking_routes(
        [{"route_confirmed": False}], 5.0
    )
    assert result["status"] == "ZERO_EARNINGS"


@pytest.mark.parametrize(
    "session, expected",
    [
        ("standard_60", 40.0),
        ("standard_30", 27.0),
        ("express_15", 19.0),
    ],
)
def test_session_types(session, expected):
    routes = [{
        "route_confirmed": True,
        "session_type": session,
        "walks": [{"num_pets": 1}],
    }]
    assert process_walking_routes(routes, 5.0)["total_revenue"] == expected


def test_unknown_session():
    result = process_walking_routes(
        [{"route_confirmed": True, "session_type": "unknown"}], 5.0
    )
    assert result["status"] == "ZERO_EARNINGS"


def test_zero_pets():
    result = process_walking_routes(
        [{"route_confirmed": True,
          "walks": [{"num_pets": 0}]}], 5.0
    )
    assert result["status"] == "ZERO_EARNINGS"


def test_aggression_alert():
    result = process_walking_routes(
        [{"route_confirmed": True,
          "walks": [{"num_pets": 1, "aggression_alert": True}]}], 5.0
    )
    assert result["status"] == "ZERO_EARNINGS"


def test_aggression_on_long_session():
    result = process_walking_routes(
        [{"route_confirmed": True, "session_type": "standard_60",
          "walks": [{"num_pets": 1, "aggression_alert": True}]}], 5.0
    )
    assert result["status"] == "ZERO_EARNINGS"


def test_more_than_three_pets():
    result = process_walking_routes(
        [{"route_confirmed": True,
          "walks": [{"num_pets": 4}]}], 5.0
    )
    assert result["total_revenue"] == 48.6


def test_medication_fee():
    result = process_walking_routes(
        [{"route_confirmed": True,
          "walks": [{"num_pets": 1, "needs_meds": True}]}], 5.0
    )
    assert result["total_revenue"] == 33.0


def test_weekend_transport_fee():
    result = process_walking_routes(
        [{"route_confirmed": True, "is_weekend": True,
          "walks": [{"num_pets": 1}]}], 5.0
    )
    assert result["total_revenue"] == 32.0


def test_incident_audit():
    routes = [
        {"route_confirmed": True, "session_type": "unknown"}
        for _ in range(5)
    ]
    assert process_walking_routes(routes, 5.0)["status"] == "INCIDENT_AUDIT"


def test_gps_no_data():
    assert inspect_gps_collars([]) == "NO_DATA"


def test_gps_online():
    assert inspect_gps_collars([[30, 25, 40]]) == "ONLINE"


def test_gps_lost_signal():
    assert inspect_gps_collars([[30, 10, 15]]) == "LOST_SIGNAL_ALERT"


def test_gps_signal_recovers():
    assert inspect_gps_collars([[10, 30, 10]]) == "ONLINE"