import psycopg2
from ..models import *

class CommentRepository:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def _connect(self):
        return psycopg2.connect(self.connection_string)

    def get_comment_by_id(self, comment_id):
        query = "SELECT * FROM comment WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (comment_id,))
                result = cursor.fetchone()
                return Comment(*result) if result else None

    def get_comments_by_task_id(self, task_id):
        query = "SELECT * FROM comment WHERE task_id = %s ORDER BY publication_date;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (task_id,))
                results = cursor.fetchall()
                return [Comment(*row) for row in results]

    def add_comment(self, task_id, user_id, text):
        query = "INSERT INTO comment (task_id, user_id, text, publication_date) VALUES (%s, %s, %s, CURRENT_TIMESTAMP) RETURNING id;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (task_id, user_id, text))
                comment_id = cursor.fetchone()[0]
                conn.commit()
                return comment_id

    def update_comment(self, comment_id, new_content):
        query = "UPDATE comment SET content = %s WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (new_content, comment_id))
                conn.commit()

    def delete_comment(self, comment_id):
        query = "DELETE FROM comment WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (comment_id,))
                conn.commit()
