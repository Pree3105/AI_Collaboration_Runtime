class AIRuntimeException(Exception):
    """Base exception for the AI orchestration runtime."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(AIRuntimeException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class ValidationError(AIRuntimeException):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422)


class PlanningError(AIRuntimeException):
    def __init__(self, message: str = "Planning failed"):
        super().__init__(message, status_code=500)


class ExecutionError(AIRuntimeException):
    def __init__(self, message: str = "Execution failed"):
        super().__init__(message, status_code=500)


class StorageError(AIRuntimeException):
    def __init__(self, message: str = "Storage operation failed"):
        super().__init__(message, status_code=500)


class NotFoundError(AIRuntimeException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ConflictError(AIRuntimeException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=409)
