def user_list_complements(order: str | None, direction: str | None):
    sql_sentence = ""
    if not order and not direction:
        sql_sentence = " ORDER BY us.username ASC;"
    elif order == "fullname" and direction == "DESC":
        sql_sentence = " ORDER BY us.fullname DESC;"
    elif order == "fullname" and (direction == "ASC" or direction == None):
        sql_sentence = " ORDER BY us.fullname ASC;"
    elif order == "username" and direction == "DESC":
        sql_sentence = " ORDER BY us.username DESC;"
    elif order == "username" and (direction == "ASC" or direction == None):
        sql_sentence = " ORDER BY us.username ASC;"
    elif order == "email" and direction == "DESC":
        sql_sentence = " ORDER BY us.email DESC;"
    elif order == "email" and (direction == "ASC" or direction == None):
        sql_sentence = " ORDER BY us.email ASC;"
    elif order == "rol" and direction == "DESC":
        sql_sentence = " ORDER BY ro.role DESC;"
    elif order == "rol" and (direction == "ASC" or direction == None):
        sql_sentence = " ORDER BY ro.role ASC;"
    elif order == "status" and direction == "DESC":
        sql_sentence = " ORDER BY ro.is_active DESC;"
    elif order == "status" and (direction == "ASC" or direction == None):
        sql_sentence = " ORDER BY ro.is_active ASC;"

    return sql_sentence


def user_list_search():
    return """ WHERE (us.fullname LIKE :search 
        or us.username ILIKE :search 
        or ro.role ILIKE :search
        or us.email ILIKE :search) """


CREATE_USER_ITEM = """
    INSERT INTO users (id, fullname, username, password, email, is_superadmin, role_id,
        is_active, created_by, created_at, updated_by, updated_at, salt)
    VALUES(:id, :fullname, :username, :password, :email, :is_superadmin, :role_id,
        :is_active, :created_by, :created_at, :updated_by, :updated_at, :salt)
    RETURNING id, fullname, username, email, is_superadmin, is_active, role_id, password, salt;
"""

GET_USER_BY_EMAIL = """
    SELECT us.id, us.fullname, us.username, us.password, us.salt, us.email, us.is_active, 
        us.is_superadmin, us.role_id,ro.role, ro.permissions
    FROM users AS us
    INNER JOIN roles as ro ON us.role_id = ro.id
    WHERE email = :email;
"""

GET_USER_BY_USERNAME = """
    SELECT us.id, us.fullname, us.username, us.password, us.salt, us.email, us.is_active, 
        us.is_superadmin, us.role_id,ro.role, ro.permissions
    FROM users AS us 
    INNER JOIN roles as ro ON us.role_id = ro.id
    WHERE username = :username;
"""

GET_USER_BY_ID = """
    SELECT us.id, us.fullname, us.username, us.password, us.salt, us.email, us.is_active, 
        us.is_superadmin, us.role_id,ro.role, ro.permissions
    FROM users AS us 
    INNER JOIN roles as ro ON us.role_id = ro.id
    WHERE us.id = :id; 
"""

GET_USERS_LIST = """
    SELECT us.id, us.fullname, us.username, us.password, us.salt, us.email, us.is_superadmin, 
        us.is_active, us.role_id, ro.role, ro.permissions, us1.fullname AS created_by, 
        us2.fullname AS updated_by
    FROM users AS us
    INNER JOIN roles AS ro ON us.role_id = ro.id
    LEFT JOIN users AS us1 ON us1.id = us.created_by
    LEFT JOIN users AS us2 ON us2.id = us.updated_by
"""

GET_USERS_LIST_BY_ROLE_ID = """
    SELECT *
    FROM users AS us
    WHERE us.role_id = :role_id
"""

UPDATE_USER_BY_ID = """
    UPDATE users
    SET fullname      = :fullname,
        username      = :username,
        email         = :email,
        password      = :password,
        role_id       = :role_id,
        is_superadmin = :is_superadmin,
        is_active     = :is_active,
        salt          = :salt,
        created_by    = :created_by,
        created_at    = :created_at,
        updated_by    = :updated_by,
        updated_at    = :updated_at
    WHERE id = :id
    RETURNING id, fullname, username, email, is_superadmin, role_id, password, salt, updated_by;
"""

UPDATE_PSW_BY_ID = """
    UPDATE users
    SET password      = :password,
        salt          = :salt,
        updated_by    = :updated_by,
        updated_at    = :updated_at
    WHERE id = :id
    RETURNING id, password;
"""

DELETE_USER_BY_ID = """
    DELETE from users
    WHERE id = :id
    RETURNING id
"""
