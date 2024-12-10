CREATE TABLE role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    role_id INTEGER REFERENCES role (id)
);

CREATE TABLE project (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    manager_id INTEGER REFERENCES "user" (id),
    status_id INTEGER REFERENCES status (id),
    CHECK (end_date > start_date) 
);

CREATE TABLE task (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    project_id INTEGER REFERENCES project (id),
    priority_id INTEGER REFERENCES priority (id),
    status_id INTEGER REFERENCES status (id),
    due_date DATE NOT NULL,
    CHECK (status_id IN (1, 2, 3))
);

CREATE TABLE task_assignment (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES task (id),
    user_id INTEGER REFERENCES "user" (id),
    assigned_date DATE NOT NULL
);

CREATE TABLE status (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE comment (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES task (id),
    user_id INTEGER REFERENCES "user" (id),
    text TEXT NOT NULL,
    publication_date TIMESTAMPTZ NOT NULL
);

CREATE TABLE log (
    id SERIAL PRIMARY KEY,
    action VARCHAR(255) NOT NULL,
    action_date TIMESTAMPTZ NOT NULL
);

CREATE TABLE file (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES task (id),
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    uploaded_date DATE NOT NULL
);

CREATE TABLE priority (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE profile (
    id INTEGER PRIMARY KEY REFERENCES "user" (id),
    phone VARCHAR(20),
    address VARCHAR(255),
    birthday DATE
);


CREATE OR REPLACE PROCEDURE add_project_with_members(
    project_name CHARACTER VARYING,
    project_description TEXT,
    start_date DATE,
    end_date DATE,
    status_name CHARACTER VARYING,
    manager_id INT,
    members INT[]
)
LANGUAGE plpgsql AS $$
DECLARE
    project_id INT;
    member_id INT;
BEGIN
    INSERT INTO project (name, description, start_date, end_date, status_id, manager_id) 
    VALUES (project_name, project_description, start_date, end_date, 
            (SELECT id FROM status WHERE name = status_name), 
            manager_id)
    RETURNING id INTO project_id;

    FOREACH member_id IN ARRAY members LOOP
        INSERT INTO task_assignment (task_id, user_id, assigned_date)
        VALUES (project_id, member_id, CURRENT_DATE);
    END LOOP;
END;
$$;


CREATE OR REPLACE FUNCTION get_tasks_by_project(project_id INT)
RETURNS TABLE (
    task_id INT,
    task_name CHARACTER VARYING,
    task_description TEXT,
    priority_name CHARACTER VARYING,
    status_name CHARACTER VARYING
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT t.id, t.name, t.description, p.name AS priority, s.name AS status
    FROM task t
    JOIN priority p ON t.priority_id = p.id
    JOIN status s ON t.status_id = s.id
    WHERE t.project_id = project_id;
END;
$$;


CREATE OR REPLACE PROCEDURE update_task_status(
    task_ids INT[],
    new_status_name CHARACTER VARYING
)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE task
    SET status_id = (SELECT id FROM status WHERE name = new_status_name)
    WHERE id = ANY(task_ids);
END;
$$;


CREATE OR REPLACE PROCEDURE create_user_with_profile(
    username CHARACTER VARYING,
    email CHARACTER VARYING,
    password CHARACTER VARYING,
    role_name CHARACTER VARYING,
    phone CHARACTER VARYING,
    address CHARACTER VARYING,
    birthday DATE
)
LANGUAGE plpgsql AS $$
DECLARE
    user_id INT;
BEGIN
    INSERT INTO "user" (username, email, password, role_id)
    VALUES (username, email, password, (SELECT id FROM role WHERE name = role_name))
    RETURNING id INTO user_id;

    INSERT INTO profile (id, phone, address, birthday)
    VALUES (user_id, phone, address, birthday);
END;
$$;


CREATE OR REPLACE PROCEDURE delete_project_with_dependencies(project_id INT)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM comment WHERE task_id IN (SELECT id FROM task WHERE project_id = project_id);

    DELETE FROM file WHERE task_id IN (SELECT id FROM task WHERE project_id = project_id);

    DELETE FROM task WHERE project_id = project_id;

    DELETE FROM project WHERE id = project_id;
END;
$$;


CREATE OR REPLACE FUNCTION get_project_report(project_id INT)
RETURNS TABLE (
    project_name CHARACTER VARYING,
    start_date DATE,
    end_date DATE,
    status_name CHARACTER VARYING,
    manager_id INT, 
    task_id INT,
    task_name CHARACTER VARYING,
    priority_name CHARACTER VARYING,
    task_status_name CHARACTER VARYING
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT p.name AS project_name, p.start_date, p.end_date, s.name AS status,
           p.manager_id,
           t.id AS task_id, t.name AS task_name, pr.name AS priority, ts.name AS task_status
    FROM project p
    JOIN task t ON p.id = t.project_id
    JOIN priority pr ON t.priority_id = pr.id
    JOIN status ts ON t.status_id = ts.id
    JOIN status s ON p.status_id = s.id
    WHERE p.id = project_id;
END;
$$;


CREATE OR REPLACE FUNCTION get_project_participants(project_id_param INTEGER)
RETURNS TABLE(
    user_id INTEGER,
    username TEXT,
    email TEXT,
    role_name TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        u.id AS user_id,
        u.username,
        u.email,
        r.name AS role_name
    FROM "user" u
    INNER JOIN task_assignment ta ON ta.user_id = u.id
    INNER JOIN task t ON t.id = ta.task_id
    INNER JOIN project p ON p.id = t.project_id
    LEFT JOIN role r ON r.id = u.role_id
    WHERE p.id = project_id_param;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION log_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO log (action, action_date)
    VALUES (CONCAT('Changing table values: ', TG_TABLE_NAME, ': ID=', NEW.id), 
            NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trigger_log_task_update
AFTER UPDATE ON task
FOR EACH ROW
EXECUTE FUNCTION log_changes();

CREATE OR REPLACE TRIGGER trigger_log_project_update
AFTER UPDATE ON project
FOR EACH ROW
EXECUTE FUNCTION log_changes();

CREATE OR REPLACE TRIGGER trigger_log_user_update
AFTER UPDATE ON "user"
FOR EACH ROW
EXECUTE FUNCTION log_changes();


CREATE OR REPLACE FUNCTION check_task_deadline()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.due_date < CURRENT_DATE AND NEW.status_id != (SELECT id FROM status WHERE name = 'Completed') THEN
        UPDATE task 
        SET status_id = (SELECT id FROM status WHERE name = 'Expired') 
        WHERE id = NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trigger_check_task_deadline
BEFORE INSERT OR UPDATE ON task
FOR EACH ROW
EXECUTE FUNCTION check_task_deadline();


CREATE OR REPLACE FUNCTION assign_default_role()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.role_id IS NULL THEN
        NEW.role_id := (SELECT id FROM role WHERE name = 'User');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trigger_assign_default_role
BEFORE INSERT ON "user"
FOR EACH ROW
EXECUTE FUNCTION assign_default_role();


CREATE OR REPLACE FUNCTION update_project_status()
RETURNS TRIGGER AS $$
DECLARE
    unfinished_tasks INTEGER;
BEGIN
    SELECT COUNT(*) INTO unfinished_tasks
    FROM task
    WHERE project_id = NEW.project_id AND status_id != (SELECT id FROM status WHERE name = 'Closed');

    IF unfinished_tasks = 0 AND NEW.manager_id IS NOT NULL THEN
        UPDATE project 
        SET status_id = (SELECT id FROM status WHERE name = 'Closed') 
        WHERE id = NEW.project_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trigger_update_project_status
AFTER UPDATE ON task
FOR EACH ROW
EXECUTE FUNCTION update_project_status();


CREATE OR REPLACE FUNCTION auto_assign_task()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO task_assignment (task_id, user_id, assigned_date)
    VALUES (NEW.id, NEW.user_id, NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trigger_auto_assign_task
AFTER INSERT ON task
FOR EACH ROW
EXECUTE FUNCTION auto_assign_task();


CREATE OR REPLACE FUNCTION check_unique_project_name()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM project WHERE name = NEW.name) THEN
        RAISE EXCEPTION 'Project with the same name already exists.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trigger_check_unique_project_name
BEFORE INSERT ON project
FOR EACH ROW
EXECUTE FUNCTION check_unique_project_name();
