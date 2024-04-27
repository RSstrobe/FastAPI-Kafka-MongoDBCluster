from fastapi import status
from fastapi import HTTPException


class AuthException(Exception):
    def __init__(self, message: str, status_code=status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status = status_code


class AuthRoleNotVerifyException(HTTPException):
    def __init__(
        self, detail: str = "Role is not verify", status_code=status.HTTP_409_CONFLICT
    ):
        self.detail = detail
        self.status_code = status_code


class AuthRoleIsAlreadySetException(HTTPException):
    def __init__(
        self, detail: str = "This is actual role", status_code=status.HTTP_409_CONFLICT
    ):
        self.detail = detail
        self.status_code = status_code


class AuthRoleIsNotExistException(HTTPException):
    def __init__(
        self, detail: str = "Role is not exist", status_code=status.HTTP_409_CONFLICT
    ):
        self.detail = detail
        self.status_code = status_code


class AuthRoleIsExistException(HTTPException):
    def __init__(
        self,
        detail: str = "Role is already exist",
        status_code=status.HTTP_409_CONFLICT,
    ):
        self.detail = detail
        self.status_code = status_code
