import unittest
from ..person import Person

class TestPerson(unittest.TestCase):
    def setUp(self):
        self.name = "Test Person"
        self.email = "test@example.org"

    def _person(self):
        return Person(self.name, self.email)

    def test_noName(self):
        p = Person(None, self.email)
        assert p.name is None
        assert p.email == self.email

    def test_noEmail(self):
        p = Person(self.name)
        assert p.name == self.name
        assert p.email is None

    def test_bothNameAndEmail(self):
        p = Person(self.name, self.email)
        assert p.name == self.name
        assert p.email == self.email

    def test_settingName(self):
        other_name = "Mary Sue"
        p = self._person()
        p.name = other_name
        assert p.name == other_name
        assert p.email == self.email

        p.name = None
        assert p.name is None
        assert p.email == self.email

    def test_settingEmail(self):
        other_email = "noreply@example.org"
        p = self._person()
        p.email = other_email
        assert p.name == self.name
        assert p.email == other_email

        p.email = None
        assert p.name == self.name
        assert p.email is None

    def test_invalidConstruction(self):
        self.assertRaises(ValueError, Person)

    def test_invalidSettingName(self):
        p = Person(self.name)
        self.assertRaises(ValueError, setattr, p, "name", None)
        assert p.name == self.name

    def test_invalidSettingEmail(self):
        p = Person(email=self.email)
        self.assertRaises(ValueError, setattr, p, "email", None)
        assert p.email == self.email

    def test_changingFromNameToMail(self):
        p = Person(name=self.name)
        p.email = self.email
        p.name = None

        assert p.email == self.email
        assert p.name is None

    def test_changingFromMailToName(self):
        p = Person(email=self.email)
        p.name = self.name
        p.email = None

        assert p.name == self.name
        assert p.email is None
