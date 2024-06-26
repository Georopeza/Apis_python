CREATE_TASK_ITEM = """
    INSERT INTO tasks (id, task_name, is_active, created_by, created_at, updated_by, updated_at)
    VALUES(:id, :task_name,:is_active, :created_by, :created_at, :updated_by, :updated_at)
    RETURNING id,  task_name, is_active, created_by, created_at, updated_by, updated_at;
"""

GET_TASKS_LIST = """
    SELECT t.id, t.task_name, t.is_active, t.created_at, t.updated_at, 
        us1.fullname AS created_by, us2.fullname AS updated_by
    FROM tasks AS t
    LEFT JOIN users AS us1 ON us1.id = t.created_by
    LEFT JOIN users AS us2 ON us2.id = t.updated_by
"""

def task_list_search():
    return """ WHERE (t.task_name LIKE :search) """

def task_list_complements(order: str | None, direction: str | None):
    sql_sentence = ""
    if not order and not direction:
        sql_sentence = " ORDER BY t.task_name ASC;"
    elif order == "task_name" and direction == "DESC":
        sql_sentence = " ORDER BY t.task_name DESC;"
    elif order == "task_name" and (direction == "ASC" or direction == None):
        sql_sentence = " ORDER BY t.task_name ASC;"
    elif order == "status" and direction == "DESC":
        sql_sentence = " ORDER BY t.is_active DESC;"
    elif order == "status" and (direction == "ASC" or direction == None):
        sql_sentence = " ORDER BY t.is_active ASC;"

    return sql_sentence

GET_TASK_BY_ID = """
    SELECT t.id, t.task_name, t.is_active, t.created_by, t.created_at, t.updated_at, 
        t.created_by, t.updated_by
    FROM tasks AS t
    WHERE t.id = :id; 
"""
UPDATE_TASK_BY_ID = """
    UPDATE tasks
    SET task_name     = :task_name,
        is_active     = :is_active,
        created_by    = :created_by,
        created_at    = :created_at,
        updated_by    = :updated_by,
        updated_at    = :updated_at
    WHERE id = :id
    RETURNING id, task_name, is_active, created_by, created_at, updated_by, updated_at;
"""

DELETE_TASK_BY_ID = """
    DELETE FROM tasks
    WHERE id = :id
    RETURNING id;
"""