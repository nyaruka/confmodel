from unittest import TestCase

from confmodel.config import Config
from confmodel.fallbacks import SingleFieldFallback, FormatStringFieldFallback
from confmodel.fields import ConfigText, ConfigInt


class TestFieldFallbacks(TestCase):

    # Tests for SingleFieldFallback

    def test_single_field_fallback(self):
        class ConfigWithFallback(Config):
            field = ConfigText("field", default="foo")

        fallback = SingleFieldFallback("field")
        self.assertEqual(fallback.build_value(ConfigWithFallback({})), "foo")
        self.assertEqual(
            fallback.build_value(ConfigWithFallback({"field": "bar"})), "bar")

    # Tests for FormatStringFieldFallback

    def test_format_string_field_fallback(self):
        class ConfigWithFallback(Config):
            text_field = ConfigText("text_field")
            int_field = ConfigInt("int_field")

        fallback = FormatStringFieldFallback(
            "{text_field}::{int_field:02d}", ["text_field", "int_field"])

        cfg = ConfigWithFallback({"int_field": 3})
        self.assertEqual(fallback.present(cfg), False)

        cfg = ConfigWithFallback({"text_field": "bar", "int_field": 37})
        self.assertEqual(fallback.present(cfg), True)
        self.assertEqual(fallback.build_value(cfg), "bar::37")

    def test_format_string_field_fallback_optional_fields(self):
        class ConfigWithFallback(Config):
            text_field = ConfigText("text_field", default="foo")
            int_field = ConfigInt("int_field")

        fallback = FormatStringFieldFallback(
            "{text_field}::{int_field:02d}", ["int_field"], ["text_field"])

        cfg = ConfigWithFallback({"int_field": 3})
        self.assertEqual(fallback.present(cfg), True)
        self.assertEqual(fallback.build_value(cfg), "foo::03")

        cfg = ConfigWithFallback({"text_field": "bar", "int_field": 37})
        self.assertEqual(fallback.present(cfg), True)
        self.assertEqual(fallback.build_value(cfg), "bar::37")


class TestConfigFieldWithFallback(TestCase):
    def test_field_uses_fallback(self):
        class ConfigWithFallback(Config):
            oldfield = ConfigText("oldfield", required=False)
            newfield = ConfigText(
                "newfield", required=True,
                fallbacks=[SingleFieldFallback("oldfield")])

        config = ConfigWithFallback({"oldfield": "foo"})
        self.assertEqual(config.newfield, "foo")

    def test_field_ignores_unnecessary_fallback(self):
        class ConfigWithFallback(Config):
            oldfield = ConfigText("oldfield", required=False)
            newfield = ConfigText(
                "newfield", required=True,
                fallbacks=[SingleFieldFallback("oldfield")])

        config = ConfigWithFallback({"oldfield": "foo", "newfield": "bar"})
        self.assertEqual(config.newfield, "bar")

    def test_field_present_if_fallback_present(self):
        class ConfigWithFallback(Config):
            oldfield = ConfigText("oldfield", required=False)
            newfield = ConfigText(
                "newfield", required=True,
                fallbacks=[SingleFieldFallback("oldfield")])

        config = ConfigWithFallback({"oldfield": "foo"})
        self.assertEqual(ConfigWithFallback.newfield.present(config), True)

    def test_field_not_present_if_fallback_missing(self):
        class ConfigWithFallback(Config):
            oldfield = ConfigText("oldfield", required=False)
            newfield = ConfigText(
                "newfield", required=False,
                fallbacks=[SingleFieldFallback("oldfield")])

        config = ConfigWithFallback({})
        self.assertEqual(ConfigWithFallback.newfield.present(config), False)
