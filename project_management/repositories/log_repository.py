import psycopg2
from ..models import *

class LogRepository:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def _connect(self):
        return psycopg2.connect(self.connection_string)
            
    def get_latest_logs(self):
        query = "SELECT * FROM log ORDER BY action_date DESC LIMIT 5;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return [Log(*row) for row in results]

    def get_all_logs(self):
        query = "SELECT id, action, action_date FROM log ORDER BY action_date DESC;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return [Log(*row) for row in results]

    def delete_log(self, log_id):
        query = "DELETE FROM log WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (log_id,))
                conn.commit()
