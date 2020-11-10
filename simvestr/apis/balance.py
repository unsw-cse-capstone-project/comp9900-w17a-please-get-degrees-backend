from flask_restx import Resource, Namespace, fields

from simvestr.helpers.auth import requires_auth, get_user
from simvestr.helpers.portfolio import calculate_all_portfolios_values

api = Namespace('balance', description='Api for viewing balance for a User')


balance_model = api.model(
    "UserBalance",
    {
        "name": fields.String(
            description="Portfolio name",
            example="John Doe's Portfolio"
        ),
        "balance": fields.Float(
            description="Current cash balance",
            example=100000.0,
        ),

    },
)


@api.route("", doc=False)
class PortfolioPriceUsersQuery(Resource):
    @api.response(200, 'Successful')
    @api.response(602, 'Portfolio for this user doesn\'t exist')
    @requires_auth
    def get(self):
        user = get_user()

        data = dict(
            plist=[dict(
                portfolio_id=p.id,
                name=user.portfolio.portfolio_name,
                close_balance=p.close_balance,
                balance=user.portfolio.balance,
                time=str(p.timestamp)
            ) for p in user.portfolio.portfolioprice]
        )
        payload = dict(
            data=data
        )
        return payload


@api.route("/user/")
@api.doc(
    description="Query user's current cash balance"
)
class PortfolioPriceQuery(Resource):
    @api.response(200, "Successful")
    @api.response(602, "Portfolio for this user doesn't exist") #needed??
    @api.doc(
        model=balance_model
    )
    @requires_auth
    def get(self, ):
        user = get_user()

        data = dict(
            name=user.portfolio.portfolio_name,
            balance=user.portfolio.balance,
        )

        return data

#TODO: Is this needed?
@api.route("/user/detailed")
class PortfolioPriceUserQuery(Resource):
    @api.response(200, "Successful")
    @api.response(404, "Portfolio for this user doesn't exist") #Needed?
    @requires_auth
    def get(self):
        user = get_user()

        data = dict(
            user_id=user.id,
            portfolio_name=user.portfolio.portfolio_name,
            close_balance=user.portfolio.portfolioprice[-1].close_balance
        )
        payload = {user.portfolio.portfolioprice[-1].id: data}
        return payload
