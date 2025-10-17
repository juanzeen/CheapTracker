from django.test import TestCase
from django.db import connection
from django.db.utils import OperationalError

class DatabaseConnectionTest(TestCase):
  "Testes para verificar conexão com o banco de dados."
  def test_database_connection(self):
    "Testa se a conexão com o banco de dados é bem-sucedida"
    db_conn = connection
    try:
      db_conn.cursor()
    except OperationalError:
        connected = False
    else:
        connected = True
    self.assertTrue(connected, "Conexão com o banco falhou")
