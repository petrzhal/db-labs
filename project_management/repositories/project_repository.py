import psycopg2
from ..models import Project, User

class ProjectRepository:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def _connect(self):
        return psycopg2.connect(self.connection_string)

    def get_project_by_id(self, project_id):
        query = "SELECT * FROM project WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (project_id,))
                result = cursor.fetchone()
                return Project(*result) if result else None

    def get_all_projects(self):
        query = "SELECT * FROM project;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return [Project(*row) for row in results]

    def add_project(self, project_name, project_description, start_date, end_date, status_id, manager_id):
        query = """
            INSERT INTO project (name, description, start_date, end_date, status_id, manager_id)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (project_name, project_description, start_date, end_date, status_id, manager_id))
                conn.commit()


    def get_user_projects(self, user_id):
        query = "SELECT * FROM get_user_projects(%s);"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id,))
                results = cursor.fetchall()
                return [Project(*row) for row in results]

    def delete_project_with_dependencies(self, project_id):
        query = "CALL delete_project_with_dependencies(%s);"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (project_id,))
                conn.commit()

    def update_project(self, project_id, name=None, description=None, start_date=None, end_date=None, status_id=None, manager_id=None):
        updates = []
        params = []

        if name is not None:
            updates.append("name = %s")
            params.append(name)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if start_date is not None:
            updates.append("start_date = %s")
            params.append(start_date)
        if end_date is not None:
            updates.append("end_date = %s")
            params.append(end_date)
        if status_id is not None:
            updates.append("status_id = %s")
            params.append(status_id)
        if manager_id is not None:
            updates.append("manager_id = %s")
            params.append(manager_id)

        if updates:
            query = f"UPDATE project SET {', '.join(updates)} WHERE id = %s;"
            params.append(project_id)
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, tuple(params))
                    conn.commit()

    def get_project_members(self, project_id):
        query = "SELECT * FROM get_project_participants(%s);"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (project_id,))
                results = cursor.fetchall()
                return [User(*row) for row in results]

    def get_tasks_by_project(self, project_id):
        query = "SELECT * FROM get_tasks_by_project(%s);"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (project_id,))
                results = cursor.fetchall()
                return results  # Consider mapping to a Task model if applicable

    def update_task_status(self, task_ids, new_status_name):
        query = "CALL update_task_status(%s, %s);"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (task_ids, new_status_name))
                conn.commit()
