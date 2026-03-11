import unittest

from packages.shared.config.settings import ServiceSettings


class ServiceSettingsTests(unittest.TestCase):
    def test_from_env_uses_defaults(self) -> None:
        settings = ServiceSettings.from_env("subscription-service", env={})
        self.assertEqual(settings.host, "0.0.0.0")
        self.assertEqual(settings.port, 8000)
        self.assertEqual(settings.environment, "dev")
        self.assertEqual(settings.log_level, "INFO")

    def test_from_env_parses_values(self) -> None:
        env = {
            "HOST": "127.0.0.1",
            "PORT": "8081",
            "APP_ENV": "prod",
            "LOG_LEVEL": "debug",
            "APP_VERSION": "1.2.3",
        }
        settings = ServiceSettings.from_env("notification-service", env=env)
        self.assertEqual(settings.host, "127.0.0.1")
        self.assertEqual(settings.port, 8081)
        self.assertEqual(settings.environment, "prod")
        self.assertEqual(settings.log_level, "DEBUG")
        self.assertEqual(settings.app_version, "1.2.3")

    def test_port_validation_rejects_invalid_values(self) -> None:
        with self.assertRaises(ValueError):
            ServiceSettings.from_env("fast-price-provider-service", env={"PORT": "bad"})
        with self.assertRaises(ValueError):
            ServiceSettings.from_env("fast-price-provider-service", env={"PORT": "70000"})


if __name__ == "__main__":
    unittest.main()

