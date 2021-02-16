from django.test import TestCase
# from django.utils import timezone
from django.core.validators import ValidationError
import datetime
from .models import Alias
from .utils import get_aliases, alias_replace

# Create your tests here.


class AliasTestCase(TestCase):
    def setUp(self):
        """Create simple Alias object for tests."""
        Alias.objects.create(
            alias="useful-object",
            target="types-slug-023xf",
            start="2019-02-01 00:00:00.000000+00:00",
            end="2019-08-01 05:23:47.657264+00:00",
        )

    def test_basic(self):
        """Test basic retrieval."""
        alias_obj = Alias.objects.get(alias="useful-object")
        referred_obj_slug = alias_obj.target
        self.assertEqual(referred_obj_slug, "types-slug-023xf")

    def test_overlap_ok_case1(self):
        """Test overlaping with different alias."""
        alias_obj = Alias.objects.create(
            alias="useful-object-2",
            target="types-slug-023xf",
            start="2019-08-01 05:23:47.657264+00:00",
            end=None,
        )
        referred_obj_slug = alias_obj.target
        self.assertEqual(referred_obj_slug, "types-slug-023xf")

    def test_overlap_ok_case2(self):
        """Test overlaping with different date range."""
        alias_obj = Alias.objects.create(
            alias="useful-object",
            target="types-slug-023xf",
            start="2020-08-01 05:23:47.657264+00:00",
            end=None,
        )
        referred_obj_slug = alias_obj.target
        self.assertEqual(referred_obj_slug, "types-slug-023xf")

    def test_overlap_case1(self):
        """Test bad overlaping."""
        with self.assertRaises(ValidationError):
            Alias.objects.create(
                alias="useful-object",
                target="types-slug-023xf",
                start="2019-01-01 00:00:00.000000+00:00",
                end="2019-02-01 05:23:47.657264+00:00",
            )

    def test_get_aliases_case1(self):
        """Test get_aliases function. No aliases found."""
        aliases = get_aliases(
            target="types-slug-023xf",
            from_date="2020-02-01 00:00:00.000000+00:00",
            to_date="2020-05-01 05:23:47.657264+00:00",
        )
        self.assertCountEqual(aliases, [])

    def test_get_aliases_case2(self):
        """Test get_aliases function. Found 1 alias."""
        obj = Alias.objects.create(
            alias="useful-object",
            target="types-slug-new",
            start="2020-03-01 00:00:00.000000+00:00",
            end="2020-04-01 05:23:47.657264+00:00",
        )
        aliases = get_aliases(
            target="types-slug-new",
            from_date="2020-02-01 00:00:00.000000+00:00",
            to_date="2020-05-01 05:23:47.657264+00:00",
        )
        self.assertCountEqual(aliases, [obj])
        self.assertEqual(aliases[0].alias, "useful-object")

    def test_alias_replace_ok_case1(self):
        """Test alias_replace function with good date."""
        alias_obj = Alias.objects.get(alias="useful-object")
        tgt = alias_obj.target
        resp = alias_replace(
            alias_obj, "2019-05-01 00:00:00.000000+00:00", "useful-object-2"
        )
        self.assertTrue(resp)
        alias_obj = Alias.objects.get(alias="useful-object")
        self.assertEqual(
            alias_obj.end,
            datetime.datetime.fromisoformat(
                "2019-05-01 00:00:00.000000+00:00"
            ),
        )
        alias_obj = Alias.objects.get(alias="useful-object-2")
        self.assertEqual(
            alias_obj.start,
            datetime.datetime.fromisoformat(
                "2019-05-01 00:00:00.000000+00:00"
            ),
        )
        self.assertEqual(alias_obj.end, None)
        self.assertEqual(alias_obj.target, tgt)

    def test_alias_replace_not_ok_case1(self):
        """Test alias_replace function with bad new date."""
        alias_obj = Alias.objects.get(alias="useful-object")
        resp = alias_replace(
            alias_obj, "2019-01-01 00:00:00.000000+00:00", "useful-object-2"
        )
        self.assertFalse(resp)

    def test_alias_replace_not_ok_case2(self):
        """Test alias_replace function with overlaping date for new alias."""
        Alias.objects.create(
            alias="useful-object-2",
            target="types-slug-023xf",
            start="2020-02-01 00:00:00.000000+00:00",
            end="2020-04-01 05:23:47.657264+00:00",
        )
        alias_obj = Alias.objects.get(alias="useful-object")
        resp = alias_replace(
            alias_obj, "2020-03-01 00:00:00.000000+00:00", "useful-object-2"
        )
        self.assertFalse(resp)
