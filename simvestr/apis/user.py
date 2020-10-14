from flask_restx import Resource, Namespace
from ..models import User, Watchlist, Stock
api = Namespace('user', description='Demo api for querying users')

@api.route('/')
class UsersQuery(Resource):
    def get(self):
        user = User.query.all()
        data = {u.id:dict(email=u.email_id, role=u.role, fname=u.first_name, lname=u.last_name, validated=u.validated) for u in user}
        payload = dict(
            data=data
        )
        return payload


@api.route('/<int:user_id>')
class UserQuery(Resource):
    def get(self, user_id: int):
        user = User.query.filter_by(id=user_id).first()
        watch = Watchlist.query.filter(Watchlist.user_id==user.id).all()
        data = dict(email=user.email_id, watchlist=[s.stock_symbol for s in watch])
        payload = dict(
            data=data
        )
        return payload
