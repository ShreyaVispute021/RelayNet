from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class RLConfig:
    """Documented hyperparameters for RelayNet's tabular MARL prototype."""

    learning_rate: float = 0.15
    discount_factor: float = 0.90
    epsilon_start: float = 0.20
    epsilon_decay: float = 0.97
    epsilon_min: float = 0.02
    kg_weight: float = 0.65
    training_episodes: int = 60
    packets_per_episode: int = 250
    reward_success: float = 4.0
    reward_failure: float = -1.0
    stability_reward_weight: float = 0.40
    battery_reward_weight: float = 0.25
    queue_penalty_weight: float = 0.50
    random_seed: int = 42

    def as_dict(self):
        return asdict(self)
