from flask_restful import HTTPException

import status_codes

def get_errors_defined():
    return {
        'NoContentError':{
            'message':'No content',
            'status':status_codes.HTTP_204_NO_CONTENT
        },
        'UnauthorizedUserError':{
            'message':'The server could not verify that you are authorized to access the URL requested.',
            'status':status_codes.HTTP_401_UNAUTHORIZED
        },
        'NotFoundError':{
            'message':'Not found',
            'status':status_codes.HTTP_404_NOT_FOUND
        },
        'DeviceNotExistError':{
            'message':'specific device not found',
            'error_code':101301,
            'status':status_codes.HTTP_404_NOT_FOUND
        },
        'AccessDatabaseError':{
            'message':'Access database failed',
            'error_code':101302,
            'status':status_codes.HTTP_503_SERVICE_UNAVAILABLE
        },
    }

class NoContentError(HTTPException):
    pass

class UnauthorizedUserError(HTTPException):
    pass

class DeviceNotExistError(HTTPException):
    pass

class LakeOfParametersError(HTTPException):
    pass

class InvalidParametersError(HTTPException):
    pass

class NotFoundError(HTTPException):
    pass

class AccessDatabaseError(HTTPException):
    pass

class AccessCacheError(HTTPException):
    pass

class AccessConfigError(HTTPException):
    pass

class UnauthorizedError(HTTPException):
    pass

class PermissionError(HTTPException):
    pass

class UnknowExceptionError(HTTPException):
    pass

