import psycopg2
from ..models import *

class TaskRepository:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def _connect(self):
        return psycopg2.connect(self.connection_string)

    def create_task(self, name, description, project_id, priority_id, status_id, due_date):
        query = """
        INSERT INTO Task (name, description, project_id, priority_id, status_id, due_date)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (name, description, project_id, priority_id, status_id, due_date))
                task_id = cursor.fetchone()[0]
                conn.commit()
                return task_id

    def get_all_priorities(self):
        query = "SELECT * FROM priority;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query,)
                results = cursor.fetchall()
                return [Priority(*row) for row in results]
            
    def get_priority_by_name(self, priority_name):
        query = "SELECT * FROM priority WHERE name = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (priority_name,)) 
                result = cursor.fetchone()
                return Priority(*result) if result else None    
            
    def get_priority_by_id(self, priority_id):
        query = "SELECT * FROM priority WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (priority_id,)) 
                result = cursor.fetchone()
                return Priority(*result) if result else None 
    
    def get_task_by_id(self, task_id):
        query = "SELECT * FROM task WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (task_id,))
                result = cursor.fetchone()
                return Task(*result) if result else None

    def get_tasks_by_project(self, project_id):
        query = "SELECT * FROM task WHERE project_id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (project_id,))
                results = cursor.fetchall()
                return [Task(*row) for row in results]
            
    def get_user_tasks(self, user_id):
        query = "SELECT * FROM task WHERE id IN (SELECT task_id FROM task_assignment WHERE user_id = %s);"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id,))
                results = cursor.fetchall()
                return [Task(*row) for row in results]

    def update_task(self, task_id, name=None, description=None, priority_id=None, status_id=None, due_date=None):
        updates = []
        params = []

        if name is not None:
            updates.append("name = %s")
            params.append(name)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if priority_id is not None:
            updates.append("priority_id = %s")
            params.append(priority_id)
        if status_id is not None:
            updates.append("status_id = %s")
            params.append(status_id)
        if due_date is not None:
            updates.append("due_date = %s")
            params.append(due_date)

        if updates:
            query = f"UPDATE Task SET {', '.join(updates)} WHERE id = %s;"
            params.append(task_id)
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, tuple(params))
                    conn.commit()
        return True


    def delete_task(self, task_id):
        query = "DELETE FROM comment WHERE task_id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (task_id,))
                conn.commit()
        query = "DELETE FROM task_assignment WHERE task_id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (task_id,))
                conn.commit()
        query = "DELETE FROM file WHERE task_id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (task_id,))
                conn.commit()
        query = "DELETE FROM task WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (task_id,))
                conn.commit()

    def update_task_status(self, task_ids, new_status_name):
        query = """
        CALL update_task_status(%s, %s);
        """
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (task_ids, new_status_name))
                conn.commit()

    def get_tasks_by_project_and_status(self, project_id, status_name):
        query = """
        CALL get_tasks_by_project_and_status(%s, %s);
        """
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (project_id, status_name))
                results = cursor.fetchall()
                return [Task(*row) for row in results]

    def add_comment_to_task(self, task_id, user_id, comment_text):
        query = """
        INSERT INTO Comment (task_id, user_id, text, created_at)
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP);
        """
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (task_id, user_id, comment_text))
                conn.commit()

    # def log_user_action(self, user_id, action):
    #     query = """
    #     INSERT INTO ActionLog (user_id, action, timestamp)
    #     VALUES (%s, %s, CURRENT_TIMESTAMP);
    #     """
    #     with self._connect() as conn:
    #         with conn.cursor() as cursor:
    #             cursor.execute(query, (user_id, action))
    #             conn.commit()
