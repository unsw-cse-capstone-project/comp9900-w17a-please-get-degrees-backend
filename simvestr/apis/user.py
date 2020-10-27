from flask_restx import Resource, Namespace

from simvestr.helpers.auth import get_user
from simvestr.models import User

api = Namespace('view user details', description='Demo api for querying users')


@api.route('/all')
class UsersQuery(Resource):
    def get(self):
        user = User.query.all()
        data = {u.id: dict
        (email=u.email_id,
         role=u.role,
         fname=u.first_name,
         lname=u.last_name,
         validated=u.validated,
         ) for u in user}
        payload = dict(
            data=data
        )
        return payload


@api.route('/details')
class UserQuery(Resource):
    def get(self,):
        user = get_user()
        watch = user.watchlist
        port = user.portfolio
        transact = user.portfolio.transactions.all()
        data = dict(email=user.email_id,
                    watchlist=[s.stock_symbol for s in watch],
                    portfolio=[p.portfolio_name for p in port],
                    transaction=[(t.symbol, t.trade_type, t.quantity) for t in transact])
        payload = dict(
            data=data
        )
        return payload
