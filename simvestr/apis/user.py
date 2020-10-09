from flask_restx import Resource, Namespace
from ..models import User
api = Namespace('user', description='Demo api for querying users')

@api.route('/')
class UserQuery(Resource):
    def get(self):
        user = User.query.all()
        data = {u.id:dict(username=u.username, email=u.email_id) for u in user}
        payload = dict(
            data=data
        )
        return payload
