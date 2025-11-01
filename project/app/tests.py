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
    """Testing if the user has been retrieved by user crud"""
    users = UserCrud.read()
    self.assertGreater(len(users), 0)

  def test_update_user(self):
    """Testing if the user has been updated by user crud"""
    user = UserCrud.read_by_email("emaildeexemplo@gmail.com")
    updatedUser = UserCrud.update(user.id, name="User Test With Changes", age=22)
    self.assertEqual(updatedUser.name, "User Test With Changes")
    self.assertEqual(updatedUser.age, 22)

  def test_delete_user(self):
    """Testing if the user has been deleted by user crud"""
    user = UserCrud.read_by_email("emaildeexemplo@gmail.com")
    UserCrud.delete(user.id)
    with self.assertRaises(user.DoesNotExist):
      UserCrud.read_by_email("emaildeexemplo@gmail.com")
