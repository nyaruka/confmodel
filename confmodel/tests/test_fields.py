from unittest import TestCase

from confmodel.errors import ConfigError
from confmodel.fields import (
    ConfigText, ConfigInt, ConfigFloat, ConfigBool, ConfigList, ConfigDict,
    ConfigUrl, ConfigRegex)


class FakeModel(object):
    def __init__(self, config):
        self._config_data = config


class TestConfigFields(TestCase):
    def fake_model(self, *value, **kw):
        config = kw.pop('config', {})
        if value:
            assert len(value) == 1
            config['foo'] = value[0]
        return FakeModel(config)

    def field_value(self, field, *value, **kw):
        self.assert_field_valid(field, *value, **kw)
        return field.get_value(self.fake_model(*value, **kw))

    def assert_field_valid(self, field, *value, **kw):
        field.validate(self.fake_model(*value, **kw))

    def assert_field_invalid(self, field, *value, **kw):
        self.assertRaises(ConfigError, field.validate,
                          self.fake_model(*value, **kw))

    def make_field(self, field_cls, **kw):
        field = field_cls("desc", **kw)
        field.setup('foo')
        return field

    def test_text_field(self):
        field = self.make_field(ConfigText)
        self.assertEqual('foo', self.field_value(field, 'foo'))
        self.assertEqual(u'foo', self.field_value(field, u'foo'))
        self.assertEqual(u'foo\u1234', self.field_value(field, u'foo\u1234'))
        self.assertEqual(None, self.field_value(field, None))
        self.assertEqual(None, self.field_value(field))
        self.assert_field_invalid(field, object())
        self.assert_field_invalid(field, 1)

    def test_regex_field(self):
        field = self.make_field(ConfigRegex)
        value = self.field_value(field, '^v[a-z]m[a-z]$')
        self.assertTrue(value.match('vumi'))
        self.assertFalse(value.match('notvumi'))
        self.assertEqual(None, self.field_value(field, None))

    def test_int_field(self):
        field = self.make_field(ConfigInt)
        self.assertEqual(0, self.field_value(field, 0))
        self.assertEqual(1, self.field_value(field, 1))
        self.assertEqual(100, self.field_value(field, "100"))
        self.assertEqual(100, self.field_value(field, u"100"))
        self.assertEqual(None, self.field_value(field, None))
        self.assertEqual(None, self.field_value(field))
        self.assert_field_invalid(field, object())
        self.assert_field_invalid(field, 2.3)
        self.assert_field_invalid(field, "foo")
        self.assert_field_invalid(field, u"foo\u1234")

    def test_float_field(self):
        field = self.make_field(ConfigFloat)
        self.assertEqual(0, self.field_value(field, 0))
        self.assertEqual(1, self.field_value(field, 1))
        self.assertEqual(0.5, self.field_value(field, 0.5))
        self.assertEqual(0.5, self.field_value(field, "0.5"))
        self.assertEqual(100, self.field_value(field, "100"))
        self.assertEqual(100, self.field_value(field, u"100"))
        self.assertEqual(None, self.field_value(field, None))
        self.assertEqual(None, self.field_value(field))
        self.assert_field_invalid(field, object())
        self.assert_field_invalid(field, "foo")
        self.assert_field_invalid(field, u"foo\u1234")

    def test_bool_field(self):
        field = self.make_field(ConfigBool)
        self.assertEqual(False, self.field_value(field, 0))
        self.assertEqual(True, self.field_value(field, 1))
        self.assertEqual(False, self.field_value(field, "0"))
        self.assertEqual(True, self.field_value(field, "true"))
        self.assertEqual(True, self.field_value(field, "TrUe"))
        self.assertEqual(False, self.field_value(field, u"false"))
        self.assertEqual(False, self.field_value(field, ""))
        self.assertEqual(True, self.field_value(field, True))
        self.assertEqual(False, self.field_value(field, False))
        self.assertEqual(None, self.field_value(field, None))
        self.assertEqual(None, self.field_value(field))

    def test_list_field(self):
        field = self.make_field(ConfigList)
        self.assertEqual([], self.field_value(field, []))
        self.assertEqual([], self.field_value(field, ()))
        self.assertEqual([0], self.field_value(field, [0]))
        self.assertEqual(["foo"], self.field_value(field, ["foo"]))
        self.assertEqual(None, self.field_value(field, None))
        self.assertEqual(None, self.field_value(field))
        self.assert_field_invalid(field, object())
        self.assert_field_invalid(field, "foo")
        self.assert_field_invalid(field, 123)

    def test_list_field_immutable(self):
        field = self.make_field(ConfigList)
        model = self.fake_model(['fault', 'mine'])
        value = field.get_value(model)
        self.assertEqual(value, ['fault', 'mine'])
        value[1] = 'yours'
        self.assertEqual(field.get_value(model), ['fault', 'mine'])

    def test_dict_field(self):
        field = self.make_field(ConfigDict)
        self.assertEqual({}, self.field_value(field, {}))
        self.assertEqual({'foo': 1}, self.field_value(field, {'foo': 1}))
        self.assertEqual({1: 'foo'}, self.field_value(field, {1: 'foo'}))
        self.assertEqual(None, self.field_value(field, None))
        self.assertEqual(None, self.field_value(field))
        self.assert_field_invalid(field, object())
        self.assert_field_invalid(field, "foo")
        self.assert_field_invalid(field, 123)

    def test_dict_field_immutable(self):
        field = self.make_field(ConfigDict)
        model = self.fake_model({'fault': 'mine'})
        value = field.get_value(model)
        self.assertEqual(value, {'fault': 'mine'})
        value['fault'] = 'yours'
        self.assertEqual(field.get_value(model), {'fault': 'mine'})

    def test_url_field(self):
        def assert_url(value,
                       scheme='', netloc='', path='', query='', fragment=''):
            self.assertEqual(value.scheme, scheme)
            self.assertEqual(value.netloc, netloc)
            self.assertEqual(value.path, path)
            self.assertEqual(value.query, query)
            self.assertEqual(value.fragment, fragment)

        field = self.make_field(ConfigUrl)
        assert_url(self.field_value(field, 'foo'), path='foo')
        assert_url(self.field_value(field, u'foo'), path='foo')
        assert_url(self.field_value(field, u'foo\u1234'),
                   path='foo\xe1\x88\xb4')
        self.assertEqual(None, self.field_value(field, None))
        self.assertEqual(None, self.field_value(field))
        self.assert_field_invalid(field, object())
        self.assert_field_invalid(field, 1)
