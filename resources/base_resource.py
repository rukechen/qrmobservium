from flask_restful import Resource

class BaseResource(Resource):
    """
    BaseResource class provides application instance access for Resource sub-class
    """

    def __init__(self, *args, **kwargs):
        self.app = kwargs['application']
