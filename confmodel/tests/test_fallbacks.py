from unittest import TestCase

from confmodel.config import Config
from confmodel.fallbacks import (
    FieldFallback, SingleFieldFallback, FormatStringFieldFallback)
from confmodel.fields import ConfigText, ConfigInt
from confmodel.errors import ConfigError


class TestFieldFallback(TestCase):
    def test_get_field_descriptor(self):
        class ConfigWithFallback(Config):
            field = ConfigText("field")

        cfg = ConfigWithFallback({"field": "foo"})
        fallback = FieldFallback()
        self.assertEqual(
            fallback.get_field_descriptor(cfg, "field"),
            ConfigWithFallback.field)
        self.assertRaises(
            ConfigError, fallback.get_field_descriptor, cfg, "no_field")

    def test_field_present(self):
        class ConfigWithFallback(Config):
            field = ConfigText("field")
            field_empty = ConfigText("field_empty")
            field_default = ConfigText("field_default", default="bar")

        cfg = ConfigWithFallback({"field": "foo"})
        fallback = FieldFallback()
        self.assertEqual(fallback.field_present(cfg, "field"), True)
        self.assertEqual(fallback.field_present(cfg, "field_empty"), False)
        self.assertEqual(fallback.field_present(cfg, "field_default"), False)

    def test_present_not_implemented(self):
        fallback = FieldFallback()
        self.assertRaises(NotImplementedError, fallback.present, None)

    def test_present(self):
        class ConfigWithFallback(Config):
            field = ConfigText("field")
            field_empty = ConfigText("field_empty")
            field_default = ConfigText("field_default", default="bar")
            field_default_required = ConfigText("field_default", default="baz")

        fallback = FieldFallback()
        fallback.required_fields = ("field", "field_default_required")

        self.assertEqual(fallback.present(ConfigWithFallback({})), False)

        cfg = ConfigWithFallback({
            "field": "foo",
            "field_default_required": "bar",
        })
        self.assertEqual(fallback.present(cfg), True)

    def test_build_value_not_implemented(self):
        fallback = FieldFallback()
        self.assertRaises(NotImplementedError, fallback.build_value, None)

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
