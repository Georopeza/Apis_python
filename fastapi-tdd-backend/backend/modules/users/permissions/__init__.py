from typing import List

from loguru import logger


async def get_permissions() -> List:
    """_
        function that configurates and returns permissions to access
        all routes defined in the system

    Returns:
        a List[Dict[key: "funtionality_name" : route[List[Dict]]]]
        List: _description_
    """

    permissions = [
        {
            "functionality": "USUARIOS",
            "routes": [
                {"permissions:list-permissions": "Listar permisos"},
                {"roles:create-role": "Crear rol"},
                {"roles:roles_list": "Listar roles"},
                {"roles:get-role-by-id": "Obtener un rol por su id"},
                {"roles:update-role-by-id": "Actualizar un rol por su id"},
                {"roles:update-activate-role-by-id": "Activar / Desactivar un rol por su id"},
                {"roles:delete-role-by-id": "Eliminar un rol por su id"},
                {"users:create-user": "Crear usuario"},
                {"users:users_list": "Listar usuarios"},
                {"users:get-user-by-id": "Obtener un usuario por su id"},
                {"users:activate-user-by-id": "Activar / Desactivar un usuario por su id"},
                {"users:update-user-by-id": "Actualizar un usuario por su id"},
                {"users:delete-user-by-id": "Eliminar un usuario por su id"},
                {"users:change-password-by-id": "Actualizar password por el propio usuario"},
            ],
        },
        {
            "functionality": "TAREAS",
            "routes": [
                {"tasks:create-task": "Crear tarea"},
                {"tasks:get_tasks_list": "Listar tareas"},
                {"tasks:get-task-by-id": "Obtener una tarea por su ID"},
                {"tasks:update-task-by-id": "Actualizar una tarea por su ID"},
                {"tasks:delete-task-by-id": "Eliminar una tarea por su ID"}
            ]
        }
    ]

    return permissions


async def verify_permissions(permission: str) -> bool:
    permissions = await get_permissions()

    found = False
    for dic in permissions:
        routes = dic.get("routes")
        for route in routes:
            if permission in route:
                found = True
                return found

    return found
