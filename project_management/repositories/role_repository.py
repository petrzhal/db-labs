import psycopg2
from psycopg2 import OperationalError
from ..models import *

class RoleRepository:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def _connect(self):
        connection = psycopg2.connect(self.connection_string)
        return connection

    def get_role_by_id(self, role_id):
        query = "SELECT * FROM role WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (role_id,))
                result = cursor.fetchone()
                return Role(*result) if result else None
            
    def get_role_id(self, role_name):
        query = "SELECT id FROM role WHERE name = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (name,))
                result = cursor.fetchone()
                return Role(*result) if result else None        

    def get_all_roles(self):
        query = "SELECT * FROM role;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return [Role(*row) for row in results]

    def create_role(self, role_name):
        query = "INSERT INTO role (name) VALUES (%s);"        
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (role_name,))
                conn.commit()


    def delete_role(self, role_id):
        query = "DELETE FROM role WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (role_id,))
                conn.commit()
