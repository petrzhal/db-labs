class User:
    def __init__(self, id, username, email, role_id, password=None):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.role_id = role_id

class Profile:
    def __init__(self, id, phone=None, address=None, birthday=None):
        self.id = id
        self.phone = phone
        self.address = address
        self.birthday = birthday

class Role:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Project:
    def __init__(self, id, name, description, start_date, end_date, status_id, manager_id):
        self.id = id
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.status_id = status_id
        self.manager_id = manager_id

class Task:
    def __init__(self, id, name, description, project_id, priority_id, status_id, due_date):
        self.id = id
        self.name = name
        self.description = description
        self.project_id = project_id
        self.priority_id = priority_id
        self.status_id = status_id
        self.due_date = due_date

class TaskAssignment:
    def __init__(self, id, task_id, user_id, assigned_date):
        self.id = id
        self.task_id = task_id
        self.user_id = user_id
        self.assigned_date = assigned_date

class Status:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Comment:
    def __init__(self, id, task_id, user_id, text, publication_date):
        self.id = id
        self.task_id = task_id
        self.user_id = user_id
        self.text = text
        self.publication_date = publication_date

class Log:
    def __init__(self, id, action, action_date):
        self.id = id
        self.action = action
        self.action_date = action_date

class File:
    def __init__(self, id, task_id, file_name, file_path, uploaded_date):
        self.id = id
        self.task_id = task_id
        self.file_name = file_name
        self.file_path = file_path
        self.uploaded_date = uploaded_date

class Priority:
    def __init__(self, id, name):
        self.id = id
        self.name = name
