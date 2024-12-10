class ProjectViewModel:
    def __init__(self, id, name, description, start_date, end_date, status, manager):
        self.id = id
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.manager = manager
        
        
class ProjectDetailsViewModel:
    def __init__(self, id, name, description, start_date, end_date, status, manager, tasks, members, all_users):
        self.id = id
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.manager = manager
        self.tasks = tasks
        self.members = members
        self.all_users = all_users
        
class AddTaskViewModel:
    def __init__(self, users, statuses, priorities, files):
        self.users = users
        self.statuses = statuses
        self.priorities = priorities
        self.files = files
        

class TaskDetailsViewModel:
    def __init__(self, id, name, description, status, priority, all_priorities, due_date, files, assigned_to):
        self.id = id
        self.name = name
        self.description = description
        self.status = status
        self.priority = priority
        self.all_priorities = all_priorities
        self.due_date = due_date
        self.files = files
        self.assigned_to = assigned_to
    
class TaskViewModel:
    def __init__(self, id, name, description, project_id, priority, status, due_date, assigned_to):
        self.id = id
        self.name = name
        self.description = description
        self.project_id = project_id
        self.priority = priority
        self.status = status
        self.due_date = due_date
        self.assigned_to = assigned_to
        

class CommentViewModel:
    def __init__(self, user, text, publication_date):
        self.user = user
        self.text = text
        self.publication_date = publication_date