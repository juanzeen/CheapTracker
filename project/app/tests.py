from django.test import TestCase
from app.cruds.user_crud import UserCrud

class BasicUserCrudTest(TestCase):
  "Tests to check users CRUD"
  def setUp(self):
    UserCrud.create(role="Shop", name="User Test", age=20, email="emaildeexemplo@gmail.com", password="8charminpass")
    return super().setUp()

  def test_create_user_and_get_by_email(self):
    """ Testing if the users has been created correctly """
    UserCrud.create(role="Shop", name="User Test", age=20, email="testedecriacao@gmail.com", password="8charminpass")
    user = UserCrud.read_by_email("testedecriacao@gmail.com")
    self.assertEqual(user.name, "User Test")

  def test_retriver_users(self):
    """Testing if the user has been retrieved by use crud"""
    users = UserCrud.read()
    self.assertGreater(len(users), 0)
