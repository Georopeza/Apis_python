SAVE_TOKEN = """ 
    INSERT INTO token_store (id, token, created_at)
    VALUES (:id, :token, :created_at)
    RETURNING id, token, created_at;
"""

GET_TOKEN_BY_VALUE = """
    SELECT id, token
    FROM token_store
    WHERE token = :token
"""
