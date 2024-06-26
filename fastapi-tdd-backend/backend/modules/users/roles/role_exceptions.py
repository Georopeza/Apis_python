from shared.utils.app_exceptions import AppExceptionCase


class RoleExceptions:
    class RoleCreateExcepton(AppExceptionCase):
        """_
        Rol creation failed
        """

        def __init__(self, msg: str = ""):
            status_code = 500
            msg = "Error creando el rol"
            AppExceptionCase.__init__(self, status_code, msg)

    class RoleAlreadyExistsExcepton(AppExceptionCase):
        """_
        Rol already exists
        """

        def __init__(self, msg: str = ""):
            status_code = 409
            msg = "El nombre del rol ya ha sido declarado anteriormente"
            AppExceptionCase.__init__(self, status_code, msg)

    class RoleNameException(AppExceptionCase):
        """_
        Rol creation failed
        """

        def __init__(self, msg: str = ""):
            status_code = 422
            msg = "El rol debe tener un nombre"
            AppExceptionCase.__init__(self, status_code, msg)

    class RolePermissionsException(AppExceptionCase):
        """_
        Rol creation failed
        """

        def __init__(self, msg: str = ""):
            status_code = 422
            msg = "Sin información de permisos"
            AppExceptionCase.__init__(self, status_code, msg)

    class RolesListsException(AppExceptionCase):
        """_
        Role list failed
        """

        def __init__(self, msg: str = ""):
            status_code = 500
            msg = "No se pudo obtener la lista de roles"
            AppExceptionCase.__init__(self, status_code, msg)

    class RoleIdNoValidException(AppExceptionCase):
        """_
        Role id not valid
        """

        def __init__(self, msg: str = ""):
            status_code = 422
            msg = "Id no está en formato aceptable"
            AppExceptionCase.__init__(self, status_code, msg)

    class RoleNotFoundException(AppExceptionCase):
        """_
        Role not found
        """

        def __init__(self, msg: str = ""):
            status_code = 404
            msg = "No se ha encontrado un rol con el Id suministrado"
            AppExceptionCase.__init__(self, status_code, msg)

    class RoleInvalidUpdateParamsException(AppExceptionCase):
        """_
        Role with invalid params to update
        """

        def __init__(self, msg: str = ""):
            status_code = 400
            msg = "Parámetros inválidos para actualizar un rol"
            AppExceptionCase.__init__(self, status_code, msg)

    class PermissionNameException(AppExceptionCase):
        """_
        Rol creation failed
        """

        def __init__(self, msg: str = ""):
            status_code = 422
            msg = "Nombre de permiso ilegal en Permisos"
            AppExceptionCase.__init__(self, status_code, msg)

    class UsersUsingRoleException(AppExceptionCase):
        """_
        Rol can't be deactivate / delete because there are users
        with it
        """

        def __init__(self, msg: str = ""):
            status_code = 409
            msg = "No se puede desactivar / eliminar este rol. Hay usuarios que lo usan"
            AppExceptionCase.__init__(self, status_code, msg)
