import psycopg2

class TaskAssignmentRepository:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def _connect(self):
        return psycopg2.connect(self.connection_string)

    def assign_task_to_user(self, task_id, user_id):
        query = """
        INSERT INTO task_assignment (task_id, user_id, assigned_date)
        VALUES (%s, %s, CURRENT_TIMESTAMP);
        """
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (task_id, user_id))
                conn.commit()

    def remove_assignment(self, task_id, user_id):
        query = """
        DELETE FROM task_assignment
        WHERE task_id = %s AND user_id = %s;
        """
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (task_id, user_id))
                conn.commit()

    def get_assignments_by_task_id(self, task_id):
        query = """
        SELECT user_id FROM task_assignment
        WHERE task_id = %s;
        """
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (task_id,))
                results = cursor.fetchall()
                return [user_id for (user_id,) in results]

    def get_assignments_by_user_id(self, user_id):
        query = """
        SELECT task_id FROM task_assignment
        WHERE user_id = %s;
        """
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id,))
                results = cursor.fetchall()
                return [task_id for (task_id,) in results]

    def get_all_assignments(self):
        query = """
        SELECT task_id, user_id FROM task_assignment;
        """
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return [(task_id, user_id) for (task_id, user_id) in results]

    # def log_assignment_action(self, task_id, user_id, action):
    #     query = """
    #     INSERT INTO ActionLog (task_id, user_id, action, timestamp)
    #     VALUES (%s, %s, %s, CURRENT_TIMESTAMP);
    #     """
    #     with self._connect() as conn:
    #         with conn.cursor() as cursor:
    #             cursor.execute(query, (task_id, user_id, action))
    #             conn.commit()
