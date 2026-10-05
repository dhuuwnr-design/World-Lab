"""Spatial physical-world state and conservative human-environment coupling.

This module is a Reality Layer foundation, not a calibrated climate or Earth-system
model. Default values are structural priors. Real observations can replace them later
through an evidence/data-assimilation layer with explicit provenance and uncertainty.
"""

from dataclasses import dataclass


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


@dataclass
class EnvironmentCell:
    """Mutable environmental state associated with one simulation location."""

    temperature_c: float = 20.0
    precipitation_mm: float = 800.0
    freshwater_availability: float = 0.5
    soil_fertility: float = 0.5
    vegetation: float = 0.5
    biodiversity: float = 0.5
    air_quality: float = 0.8
    land_use_intensity: float = 0.2
    built_intensity: float = 0.2
    pollution: float = 0.1
    resource_availability: float = 0.5
    state_confidence: float = 0.1
    source_class: str = "synthetic-structural-prior"

    def validate(self) -> None:
        for name in (
            "freshwater_availability",
            "soil_fertility",
            "vegetation",
            "biodiversity",
            "air_quality",
            "land_use_intensity",
            "built_intensity",
            "pollution",
            "resource_availability",
            "state_confidence",
        ):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if self.precipitation_mm < 0.0:
            raise ValueError("precipitation_mm must be non-negative")


def annual_step(
    cell: EnvironmentCell,
    *,
    human_pressure: float,
    built_pressure: float,
    climate_forcing_c: float = 0.0,
) -> None:
    """Advance the local environmental state by one year.

    The rates are deliberately small structural mechanisms. They are not presented
    as measured Earth-system coefficients and should be replaced/calibrated by
    evidence-backed sector models as the Reality Layer grows.
    """

    human_pressure = clamp(human_pressure)
    built_pressure = clamp(built_pressure)
    climate_forcing_c = float(climate_forcing_c)

    cell.temperature_c += climate_forcing_c
    cell.land_use_intensity = clamp(
        cell.land_use_intensity + 0.02 * human_pressure + 0.03 * built_pressure
        - 0.01 * (1.0 - human_pressure)
    )
    cell.built_intensity = clamp(
        cell.built_intensity + 0.025 * built_pressure - 0.005 * (1.0 - built_pressure)
    )

    cell.pollution = clamp(
        cell.pollution
        + 0.025 * human_pressure
        + 0.02 * built_pressure
        - 0.015 * (1.0 - human_pressure) * (1.0 - built_pressure)
    )
    cell.air_quality = clamp(
        cell.air_quality - 0.025 * cell.pollution - 0.01 * human_pressure
        + 0.01 * (1.0 - built_pressure)
    )

    precipitation_support = clamp(cell.precipitation_mm / 1200.0)
    cell.freshwater_availability = clamp(
        cell.freshwater_availability
        + 0.015 * precipitation_support
        - 0.02 * human_pressure
        - 0.01 * cell.pollution
    )
    cell.soil_fertility = clamp(
        cell.soil_fertility
        + 0.008 * precipitation_support
        - 0.012 * cell.land_use_intensity
    )
    cell.vegetation = clamp(
        cell.vegetation
        + 0.015 * cell.soil_fertility
        + 0.01 * precipitation_support
        - 0.025 * cell.land_use_intensity
        - 0.01 * cell.pollution
    )
    cell.biodiversity = clamp(
        cell.biodiversity
        + 0.008 * cell.vegetation
        - 0.02 * cell.land_use_intensity
        - 0.015 * cell.pollution
    )
    cell.resource_availability = clamp(
        cell.resource_availability
        + 0.008 * cell.biodiversity
        - 0.02 * human_pressure
        - 0.008 * cell.land_use_intensity
    )
    cell.state_confidence = clamp(cell.state_confidence)


def perception_signals(cell: EnvironmentCell) -> dict[str, float]:
    """Expose normalized environmental conditions to individual agents."""

    return {
        "environment_freshwater": cell.freshwater_availability,
        "environment_soil": cell.soil_fertility,
        "environment_vegetation": cell.vegetation,
        "environment_biodiversity": cell.biodiversity,
        "environment_air_quality": cell.air_quality,
        "environment_pollution": cell.pollution,
        "environment_resources": cell.resource_availability,
        "environment_land_use": cell.land_use_intensity,
        "environment_built": cell.built_intensity,
        "environment_state_confidence": cell.state_confidence,
    }
