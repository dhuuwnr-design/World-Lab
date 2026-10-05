import pytest

from worldlab.calibration.adapters import build_parameter_map, build_social_context
from worldlab.calibration.profile import CalibrationProfile
from worldlab.calibration.validation import compare


def profile() -> CalibrationProfile:
    p = CalibrationProfile("TEST", 2025)
    p.add_indicator("inequality", 0.4, source="test", unit="normalized")
    p.add_indicator("institutional_trust", 0.7, source="test", unit="normalized")
    p.add_indicator("social_support_access", 0.8, source="test", unit="normalized")
    p.add_indicator("employment", 0.6, source="test", unit="normalized")
    return p


def test_profile_preserves_provenance():
    p = profile()
    assert p.indicators["employment"].source == "test"
    assert p.indicators["employment"].year == 2025


def test_social_context_is_built_only_from_explicit_indicators():
    context = build_social_context(profile(), location_id=7)
    assert context.location_id == 7
    assert context.inequality == 0.4
    assert context.institutional_trust == 0.7
    assert context.social_support_access == 0.8


def test_parameter_mapping_is_transparent():
    result = build_parameter_map(profile(), mapping={"employment_rate": "employment"})
    assert result == {"employment_rate": 0.6}


def test_out_of_range_normalized_input_is_rejected():
    p = profile()
    p.indicators["inequality"] = p.indicators["inequality"].__class__(
        "inequality", 1.4, "test", 2025, "normalized", ""
    )
    with pytest.raises(ValueError):
        build_social_context(p, location_id=1)


def test_validation_gate():
    report = compare({"population": 100.0}, {"population": 105.0}, threshold=0.10)
    assert report.passed
