from flask_restx import Resource, Namespace

api = Namespace('hello', description='Hello world template for building api')

@api.route('/')
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}