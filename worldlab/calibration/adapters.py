"""Adapters from external indicators to WORLD LAB context parameters.

Adapters intentionally use explicit formulas. They do not infer culture,
personality or emotion from a country label.
"""

from .profile import CalibrationProfile
from worldlab.core.social import SocialContext


def build_social_context(
    profile: CalibrationProfile,
    *,
    location_id: int,
    inequality_indicator: str = "inequality",
    institutional_trust_indicator: str = "institutional_trust",
    support_indicator: str = "social_support_access",
) -> SocialContext:
    """Create a social context from explicitly supplied calibrated indicators.

    Expected indicator values are normalized to [0, 1]. Raw units belong in the
    evidence record; normalization is an adapter responsibility.
    """

    profile.require(
        inequality_indicator,
        institutional_trust_indicator,
        support_indicator,
    )

    values = {
        "inequality": profile.indicators[inequality_indicator].value,
        "institutional_trust": profile.indicators[institutional_trust_indicator].value,
        "social_support_access": profile.indicators[support_indicator].value,
    }
    for name, value in values.items():
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be normalized to [0, 1]")

    context = SocialContext(
        location_id=location_id,
        inequality=values["inequality"],
        institutional_trust=values["institutional_trust"],
        social_support_access=values["social_support_access"],
    )
    context.validate()
    return context


def build_parameter_map(
    profile: CalibrationProfile,
    *,
    mapping: dict[str, str],
) -> dict[str, float]:
    """Map named evidence indicators to model parameters without hidden rules."""

    profile.require(*mapping.values())
    return {
        parameter: profile.indicators[indicator].value
        for parameter, indicator in mapping.items()
    }
