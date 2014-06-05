from unittest import TestCase

from confmodel.config import Config, ConfigField, FieldFallback
from confmodel.errors import ConfigError
from confmodel.fields import ConfigText, ConfigInt


class TestConfig(TestCase):
    def test_simple_config(self):
        class FooConfig(Config):
            "Test config."
            foo = ConfigField("foo")
            bar = ConfigField("bar")

        conf = FooConfig({'foo': 'blah'})
        self.assertEqual(conf.foo, 'blah')
        self.assertEqual(conf.bar, None)

        conf = FooConfig({'bar': 'blah'})
        self.assertEqual(conf.foo, None)
        self.assertEqual(conf.bar, 'blah')

    def test_required_field(self):
        class FooConfig(Config):
            "Test config."
            foo = ConfigField("foo", required=True)
            bar = ConfigField("bar")

        conf = FooConfig({'foo': 'blah'})
        self.assertEqual(conf.foo, 'blah')
        self.assertEqual(conf.bar, None)

        self.assertRaises(ConfigError, FooConfig, {'bar': 'blah'})

    def test_static_field(self):
        class FooConfig(Config):
            "Test config."
            foo = ConfigField("foo", required=True, static=True)
            bar = ConfigField("bar")

        conf = FooConfig({'foo': 'blah', 'bar': 'baz'}, static=True)
        self.assertEqual(conf.foo, 'blah')
        self.assertRaises(ConfigError, lambda: conf.bar)

    def test_default_field(self):
        class FooConfig(Config):
            "Test config."
            foo = ConfigField("what 'twas", default="brillig")
            bar = ConfigField("tove status", default="slithy")

        conf = FooConfig({'foo': 'blah'})
        self.assertEqual(conf.foo, 'blah')
        self.assertEqual(conf.bar, 'slithy')

        conf = FooConfig({'bar': 'blah'})
        self.assertEqual(conf.foo, 'brillig')
        self.assertEqual(conf.bar, 'blah')

    def test_doc(self):
        class FooConfig(Config):
            "Test config."
            foo = ConfigField("A foo field.")
            bar = ConfigText("A bar field.")

        self.assertEqual(FooConfig.__doc__, '\n'.join([
            "Test config.",
            "",
            "Configuration options:",
            "",
            ":param foo:",
            "",
            "    A foo field.",
            "",
            ":param str bar:",
            "",
            "    A bar field.",
            ]))

        # And again with the fields defined in a different order to check that
        # we document fields in definition order.
        class BarConfig(Config):
            "Test config."
            bar = ConfigField("A bar field.")
            foo = ConfigField("A foo field.")

        self.assertEqual(BarConfig.__doc__, '\n'.join([
            "Test config.",
            "",
            "Configuration options:",
            "",
            ":param bar:",
            "",
            "    A bar field.",
            "",
            ":param foo:",
            "",
            "    A foo field.",
            ]))

    def test_doc_indentation(self):
        expected_doc = '\n'.join([
            "Test config.",
            "    Indented.",
            "",
            "Outdented.",
            "",
            "Configuration options:",
            "",
            ":param foo:",
            "",
            "    A foo field.",
            ])

        class FooConfig(Config):
            """
            Test config.
                Indented.

            Outdented.
            """
            foo = ConfigField("A foo field.")

        self.assertEqual(FooConfig.__doc__, expected_doc)

        class BarConfig(Config):
            """Test config.
                Indented.

            Outdented."""
            foo = ConfigField("A foo field.")

        self.assertEqual(BarConfig.__doc__, expected_doc)

    def test_inheritance(self):
        class FooConfig(Config):
            "Test config."
            foo = ConfigField("From base class.")

        class BarConfig(FooConfig):
            "Another test config."
            bar = ConfigField("New field.")

        conf = BarConfig({'foo': 'blah', 'bar': 'bleh'})
        self.assertEqual(conf._get_fields(),
                         [FooConfig.foo, BarConfig.bar])
        self.assertEqual(conf.foo, 'blah')
        self.assertEqual(conf.bar, 'bleh')

        # Inherited fields should come before local fields.
        self.assertEqual(BarConfig.__doc__, '\n'.join([
            "Another test config.",
            "",
            "Configuration options:",
            "",
            ":param foo:",
            "",
            "    From base class.",
            "",
            ":param bar:",
            "",
            "    New field.",
            ]))

    def test_double_inheritance(self):
        class FooConfig(Config):
            "Test config."
            foo = ConfigField("From base class.")

        class BarConfig(FooConfig):
            "Another test config."
            bar = ConfigField("From middle class.")

        class BazConfig(BarConfig):
            "Second-level inheritance test config."
            baz = ConfigField("From top class.")

        conf = BazConfig({'foo': 'blah', 'bar': 'bleh', 'baz': 'blerg'})
        self.assertEqual(conf._get_fields(),
                         [FooConfig.foo, BarConfig.bar, BazConfig.baz])
        self.assertEqual(conf.foo, 'blah')
        self.assertEqual(conf.bar, 'bleh')
        self.assertEqual(conf.baz, 'blerg')

    def test_validation(self):
        class FooConfig(Config):
            "Test config."
            foo = ConfigField("foo", required=True, static=True)
            bar = ConfigInt("bar", required=True)

        conf = FooConfig({'foo': 'blah', 'bar': 1})
        self.assertEqual(conf.foo, 'blah')
        self.assertEqual(conf.bar, 1)

        self.assertRaises(ConfigError, FooConfig, {})
        self.assertRaises(ConfigError, FooConfig, {'foo': 'blah', 'baz': 'hi'})

    def test_static_validation(self):
        class FooConfig(Config):
            "Test config."
            foo = ConfigField("foo", required=True, static=True)
            bar = ConfigInt("bar", required=True)

        conf = FooConfig({'foo': 'blah'}, static=True)
        self.assertEqual(conf.foo, 'blah')

        conf = FooConfig({'foo': 'blah', 'bar': 'hi'}, static=True)
        self.assertEqual(conf.foo, 'blah')

        self.assertRaises(ConfigError, FooConfig, {}, static=True)

    def test_post_validate(self):
        class FooConfig(Config):
            foo = ConfigInt("foo", required=True)

            def post_validate(self):
                if self.foo < 0:
                    self.raise_config_error("'foo' must be non-negative")

        conf = FooConfig({'foo': 1})
        self.assertEqual(conf.foo, 1)

        self.assertRaises(ConfigError, FooConfig, {'foo': -1})

    def test_fields_read_only(self):
        class FooConfig(Config):
            foo = ConfigInt("foo")

        conf = FooConfig({'foo': 1})
        self.assertRaises(AttributeError, setattr, conf, 'foo', 2)


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
