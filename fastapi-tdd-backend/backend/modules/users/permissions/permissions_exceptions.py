from shared.utils.app_exceptions import AppExceptionCase


class PermissionsExceptions:
    class PermissionsListException(AppExceptionCase):
        """_
        Permissions list failed
        """

        def __init__(self, msg: str = ""):  # context: dict = None):
            status_code = 500
            msg = "No tiene permiso para ver esta lista"
            AppExceptionCase.__init__(self, status_code, msg)

    class PermissionsEmptyListException(AppExceptionCase):
        """_
        Permissions list failed
        """

        def __init__(self, msg: str = ""):  # context: dict = None):
            status_code = 204
            msg = "Lista vacía"
            AppExceptionCase.__init__(self, status_code, msg)
