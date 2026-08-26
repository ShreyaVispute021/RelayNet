from dataclasses import dataclass


@dataclass
class ScenarioConfig:
    name: str
    mobility_factor: float
    traffic_factor: float
    battery_drain: float
    stability_drain: float
    failure_time: int | None = None


SCENARIOS = [

    ScenarioConfig(
        name="normal",
        mobility_factor=1.0,
        traffic_factor=1.0,
        battery_drain=0.05,
        stability_drain=0.0005,
        failure_time=None
    ),

    ScenarioConfig(
        name="high_mobility",
        mobility_factor=2.0,
        traffic_factor=1.0,
        battery_drain=0.05,
        stability_drain=0.001,
        failure_time=None
    ),

    ScenarioConfig(
        name="high_congestion",
        mobility_factor=1.0,
        traffic_factor=2.5,
        battery_drain=0.08,
        stability_drain=0.0008,
        failure_time=None
    ),

    ScenarioConfig(
        name="low_battery",
        mobility_factor=1.0,
        traffic_factor=1.0,
        battery_drain=0.15,
        stability_drain=0.0005,
        failure_time=None
    ),

    ScenarioConfig(
        name="relay_failure",
        mobility_factor=1.0,
        traffic_factor=1.0,
        battery_drain=0.08,
        stability_drain=0.001,
        failure_time=500
    ),
]