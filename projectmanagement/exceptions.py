from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class CustomException(APIException):
    detail = None
    status_code = None

    def __init__(self, status, message, e=None):
        CustomException.status_code = status
        CustomException.detail = message
        CustomException.e = e


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if "detail" in response.data:
            response.data["error"] = response.data["detail"]
            del response.data["detail"]

    return response
