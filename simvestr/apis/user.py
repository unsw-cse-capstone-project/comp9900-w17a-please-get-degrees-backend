from flask_restx import Resource, Namespace
from ..models import User
api = Namespace('user', description='Demo api for querying users')

@api.route('/')
class UsersQuery(Resource):
    def get(self):
        user = User.query.all()
        data = {u.id:dict(username=u.username, email=u.email) for u in user}
        payload = dict(
            data=data
        )
        return payload


@api.route('/<int:user_id>')
class UserQuery(Resource):
    def get(self, user_id: int):
        user = User.query.filter_by(id=user_id).first()
        data = {u.id:dict(username=u.username, email=u.email, watchlist=u.watchlist) for u in user}
        payload = dict(
            data=data
        )
        return payload