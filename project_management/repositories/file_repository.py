import psycopg2
from ..models import *

class FileRepository:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def _connect(self):
        return psycopg2.connect(self.connection_string)

    def get_file_by_id(self, file_id):
        query = "SELECT * FROM file WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (file_id,))
                result = cursor.fetchone()
                return File(*result) if result else None

    def get_files_by_task_id(self, task_id):
        query = "SELECT * FROM file WHERE task_id = %s ORDER BY uploaded_date;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (task_id,))
                results = cursor.fetchall()
                return [File(*row) for row in results]

    def add_file(self, file):
        query = "INSERT INTO file (task_id, file_name, file_path, uploaded_date) VALUES (%s, %s, %s, CURRENT_TIMESTAMP) RETURNING id;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (file.task_id, file.file_name, file.file_path))
                file_id = cursor.fetchone()[0]
                conn.commit()
                return file_id

    def update_file(self, file_id, new_file_name=None, new_file_path=None):
        updates = []
        params = []

        if new_file_name is not None:
            updates.append("file_name = %s")
            params.append(new_file_name)
        if new_file_path is not None:
            updates.append("file_path = %s")
            params.append(new_file_path)

        if updates:
            query = f"UPDATE File SET {', '.join(updates)} WHERE id = %s;"
            params.append(file_id)
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, tuple(params))
                    conn.commit()

    def delete_file(self, file_id):
        query = "DELETE FROM file WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (file_id,))
                conn.commit()
