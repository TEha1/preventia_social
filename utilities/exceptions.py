from rest_framework.exceptions import APIException


class Http400(APIException):
    status_code = 400


class Http404(APIException):
    status_code = 404
