import psycopg2
from ..models import *

class StatusRepository:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def _connect(self):
        return psycopg2.connect(self.connection_string)

    def get_status_by_id(self, status_id):
        query = "SELECT * FROM status WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (status_id,))
                result = cursor.fetchone()
                return Status(*result) if result else None
            
    def get_status_by_name(self, status_name):
        query = "SELECT * FROM status WHERE name = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (status_name,))
                result = cursor.fetchone()
                return Status(*result) if result else None

    def get_all_statuses(self):
        query = "SELECT * FROM status;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return [Status(*row) for row in results]

    def add_status(self, status_name):
        query = "INSERT INTO status (name) VALUES (%s) RETURNING id;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (status_name,))
                status_id = cursor.fetchone()[0]
                conn.commit()
                return status_id

    def update_status(self, status_id, new_name):
        query = "UPDATE status SET name = %s WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (new_name, status_id))
                conn.commit()

    def delete_status(self, status_id):
        query = "DELETE FROM status WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (status_id,))
                conn.commit()
