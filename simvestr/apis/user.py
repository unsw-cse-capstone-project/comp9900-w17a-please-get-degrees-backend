from flask_restx import Resource, Namespace, fields

from simvestr.helpers.auth import get_user, requires_auth
from simvestr.helpers.portfolio import all_stocks_balance
from simvestr.models import User

api = Namespace('view user details', description='Demo api for querying users')

user_details_model = api.model(
    "Signup",
    {
        "email": fields.String(
            required=True,
            description="User email",
            example="test@gmail.com"
        ),
        "password": fields.String(
            required=True,
            description="User password",
            example="pass1234"
        ),
        "first_name": fields.String(
            required=True,
            description="User first name",
            example="Brett"
        ),
        "last_name": fields.String(
            required=True,
            description="User last name",
            example="Lee"
        ),
    },
)

@api.route('/all')
class UsersQuery(Resource):
    @requires_auth
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
    @requires_auth
    def get(self, ):
        user = get_user()
        watch = user.watchlist
        port = user.portfolio
        transact = user.portfolio.transactions.all()
        data = dict(
            email=user.email_id,
            watchlist=[s.symbol for s in watch.stocks],
            portfolio={
                "name": port.portfolio_name,
                "portfolio": all_stocks_balance(user)
            },
            transaction={
                t.symbol: {
                    "quantity": t.quantity,
                    "quote": t.quote,
                    "date": str(t.timestamp),
                } for t in transact
            }
        )

        return data
