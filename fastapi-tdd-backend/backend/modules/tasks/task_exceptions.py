from typing import Any

from shared.utils.app_exceptions import AppExceptionCase


class TaskExceptions:
    class TaskCreateExcepton(AppExceptionCase):
        """_
        Task creation failed
        """

        def __init__(self, msg: str = ""):
            status_code = 500
            msg = "Error creando la tarea"
            AppExceptionCase.__init__(self, status_code, msg)

    class TaskNotFoundException(AppExceptionCase):
        """_
        Task's ID not found
        """

        def __init__(self, msg: str = ""):
            status_code = 404
            msg = "El ID suministrado no se encuentra en la DB"
            AppExceptionCase.__init__(self, status_code, msg)

    class TaskIdNoValidException(AppExceptionCase):
        """_
        Task Id invalid
        """

        def __init__(self, msg: str = ""):
            status_code = 422
            msg = "Id de tarea inválido"
            AppExceptionCase.__init__(self, status_code, msg)

    class TaskInvalidUpdateParamsException(AppExceptionCase):
        """_
        Task Invalid update parameters
        """

        def __init__(self, msg: str = "", e: Any = None):
            error = e
            status_code = 422
            msg = f"Parámetros de actualización inválidos: {str(error)}"
            AppExceptionCase.__init__(self, status_code, msg)
            