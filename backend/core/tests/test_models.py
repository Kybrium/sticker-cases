from .factories import UserFactory

def test_user_str(db):
    u = UserFactory()
    assert str(u) == u.get_username()