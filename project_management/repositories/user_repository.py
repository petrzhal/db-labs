import psycopg2
from psycopg2 import OperationalError
from ..models import *

class UserRepository:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def _connect(self):
        connection = psycopg2.connect(self.connection_string)
        return connection

    def get_user_by_id(self, user_id):
        query = "SELECT id, username, email, role_id, password FROM \"user\" WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                return User(*result) if result else None
            
    def get_user_by_username(self, username):
        query = "SELECT id, username, email, role_id, password FROM \"user\" WHERE username = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (username,))
                result = cursor.fetchone()
                return User(*result) if result else None
            
    def get_user_by_email(self, email):
        query = "SELECT id, username, email, role_id, password FROM \"user\" WHERE email = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (email,))
                result = cursor.fetchone()
                return User(*result) if result else None       

    def get_all_users(self):
        query = "SELECT id, username, email, role_id, password FROM \"user\";"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return [User(*row) for row in results]

    def create_user_with_profile(self, username, email, password, role_name, phone, address, birthday):
        query = """
        CALL create_user_with_profile(%s, %s, %s, %s, %s, %s, %s);
        """
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (username, email, password, role_name, phone, address, birthday))
                conn.commit()

    def update_user(self, user_id, username=None, email=None, password=None, role_id=None):
        updates = []
        params = []

        if username is not None:
            updates.append("username = %s")
            params.append(username)
        if email is not None:
            updates.append("email = %s")
            params.append(email)
        if password is not None:
            updates.append("password = %s")
            params.append(password)
        if role_id is not None:
            updates.append("role_id = %s")
            params.append(role_id)

        if updates:
            query = f"UPDATE \"user\" SET {', '.join(updates)} WHERE id = %s;"
            params.append(user_id)
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, tuple(params))
                    conn.commit()

    def delete_user(self, user_id):
        query = "DELETE FROM profile WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id,))
                conn.commit()
        query = "DELETE FROM \"user\" WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id,))
                conn.commit()

    def get_user_role(self, user_id):
        query = """
        SELECT r.id, r.name
        FROM "user" u
        JOIN "role" r ON u.role_id = r.id
        WHERE u.id = %s;
        """
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                return Role(*result) if result else None


    def get_user_profile(self, user_id):
        query = "SELECT * FROM profile WHERE id = %s;"
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                return Profile(*result) if result else None

    def update_user_profile(self, user_id, phone=None, address=None, birthday=None):
        updates = []
        params = []

        if phone is not None:
            updates.append("phone = %s")
            params.append(phone)
        if address is not None:
            updates.append("address = %s")
            params.append(address)
        if birthday is not None:
            updates.append("birthday = %s")
            params.append(birthday)

        if updates:
            query = f"UPDATE profile SET {', '.join(updates)} WHERE id = %s;"
            params.append(user_id)
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, tuple(params))
                    conn.commit()