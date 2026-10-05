from src.services.configuration import ConfigManager


class PollingRateService:
    DEFAULT_POLLING_RATE_SECONDS = 10

    @classmethod
    def get_polling_rate_seconds(cls, config_manager: ConfigManager | None) -> int:
        settings = getattr(getattr(config_manager, "config", None), "settings", None)
        configured_rate = getattr(
            settings,
            "polling_rate_seconds",
            cls.DEFAULT_POLLING_RATE_SECONDS,
        )
        try:
            polling_rate = int(configured_rate)
        except (TypeError, ValueError):
            return cls.DEFAULT_POLLING_RATE_SECONDS

        return polling_rate if polling_rate > 0 else cls.DEFAULT_POLLING_RATE_SECONDS