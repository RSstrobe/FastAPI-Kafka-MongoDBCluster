from http import HTTPStatus
from werkzeug.exceptions import HTTPException


class TokenException(HTTPException):
    code = HTTPStatus.UNAUTHORIZED
    description = "Incorrect access token."


class ForbiddenException(HTTPException):
    code = HTTPStatus.FORBIDDEN
    description = "Insufficient privileges to use this function."


class ValidationException(HTTPException):
    code = HTTPStatus.BAD_REQUEST
    description = "Invalid request, missing required parameters"


class EvaluationCreatedException(HTTPException):
    code = HTTPStatus.CONFLICT
    description = "Evaluation already exists"


class EntityExistException(HTTPException):
    code = HTTPStatus.CONFLICT
    description = "Entiry already exist."


class EntityNotExistException(HTTPException):
    code = HTTPStatus.CONFLICT
    description = "Entiry isn't exist."
