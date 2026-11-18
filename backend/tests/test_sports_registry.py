import unittest

from app.sports.registry import (
    SportDefinition,
    SportRegistry,
    build_default_registry,
)


class SportRegistryTests(unittest.TestCase):
    def test_default_registry_contains_initial_sports(self):
        registry = build_default_registry()
        self.assertTrue(registry.supports("cricket"))
        self.assertTrue(registry.supports("football"))
        self.assertEqual(
            [item.code for item in registry.list()],
            ["cricket", "football"],
        )

    def test_registry_normalizes_codes(self):
        registry = SportRegistry([SportDefinition(" Cricket ", "Cricket")])
        self.assertTrue(registry.supports("CRICKET"))
        self.assertEqual(registry.get("cricket").display_name, "Cricket")

    def test_duplicate_sport_is_rejected(self):
        registry = build_default_registry()
        with self.assertRaisesRegex(ValueError, "already registered"):
            registry.register(SportDefinition("cricket", "Another Cricket"))

    def test_unknown_sport_is_rejected(self):
        registry = build_default_registry()
        with self.assertRaisesRegex(KeyError, "unsupported sport"):
            registry.get("basketball")

    def test_invalid_definition_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "code"):
            SportDefinition(" ", "Unknown")


if __name__ == "__main__":
    unittest.main()
