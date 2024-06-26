from typing import Any

from shared.utils.app_exceptions import AppExceptionCase


class UserExceptions:
    class UserCreateExcepton(AppExceptionCase):
        """_
        User creation failed
        """

        def __init__(self, msg: str = ""):
            status_code = 500
            msg = "Error creando usuario"
            AppExceptionCase.__init__(self, status_code, msg)

    class UserWithNoRoleException(AppExceptionCase):
        """_
        User with no rol creation failed
        """

        def __init__(self, msg: str = ""):
            status_code = 422
            msg = "Usuario debe tener un rol"
            AppExceptionCase.__init__(self, status_code, msg)

    class UserWithNoUsernameException(AppExceptionCase):
        """_
        User with no rol creation failed
        """

        def __init__(self, msg: str = ""):
            status_code = 422
            msg = "Usuario debe tener un nombre de usario (username)"
            AppExceptionCase.__init__(self, status_code, msg)

    class UserWithNoValidEmailException(AppExceptionCase):
        """_
        User with no rol creation failed
        """

        def __init__(self, msg: str = ""):
            status_code = 422
            msg = "Usuario debe tener un correo valido"
            AppExceptionCase.__init__(self, status_code, msg)

    class UserWithNoValidPasswordException(AppExceptionCase):
        """_
        User with no rol creation failed
        """

        def __init__(self, msg: str = ""):
            status_code = 422
            msg = "Usuario debe tener un password valido"
            AppExceptionCase.__init__(self, status_code, msg)

    class UserWithNoUserTypeException(AppExceptionCase):
        """_
        User with no rol creation failed
        """

        def __init__(self, msg: str = ""):
            status_code = 422
            msg = "Usuario debe indicar tipo de usuario"
            AppExceptionCase.__init__(self, status_code, msg)

    class UserEmailAlreadyExistsExeption(AppExceptionCase):
        """_
        User email already exists
        """

        def __init__(self, msg: str = ""):
            status_code = 400
            msg = "Email de usuario ya existe"
            AppExceptionCase.__init__(self, status_code, msg)

    class UserUsernameAlreadyExistsExeption(AppExceptionCase):
        """_
        User email already exists
        """

        def __init__(self, msg: str = ""):
            status_code = 400
            msg = "Nombre de usuario (username) ya existe"
            AppExceptionCase.__init__(self, status_code, msg)

    class UsersListsException(AppExceptionCase):
        """
        Could not recover uasers list
        """

        def __init__(self, msg: str = ""):
            status_code = 500
            msg = "No se pudo recuperar la lista de usuarios"
            AppExceptionCase.__init__(self, status_code, msg)

    class UserNotFoundException(AppExceptionCase):
        """_
        User not found
        """

        def __init__(self, msg: str = ""):
            status_code = 404
            msg = "Id de usuario no encontrado"
            AppExceptionCase.__init__(self, status_code, msg)

    class UserInvalidUpdateParamsException(AppExceptionCase):
        """_
        User Invalid update parameters
        """

        def __init__(self, msg: str = "", e: Any = None):
            error = e
            status_code = 422
            msg = f"Parámetros de actualización inválidos: {str(error)}"
            AppExceptionCase.__init__(self, status_code, msg)

    class UserIdNoValidException(AppExceptionCase):
        """_
        User Id invalid
        """

        def __init__(self, msg: str = ""):
            status_code = 422
            msg = "Id de usuario inválido"
            AppExceptionCase.__init__(self, status_code, msg)

    class CanNotChangePswOfOtherUserException(AppExceptionCase):
        """_
        User can not chandge the password of other user
        """

        def __init__(self, msg: str = ""):
            status_code = 409
            msg = "No puede cambiar el password de otro usuario"
            AppExceptionCase.__init__(self, status_code, msg)
