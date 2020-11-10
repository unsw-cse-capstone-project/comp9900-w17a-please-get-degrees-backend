from flask_restx import Resource, Namespace

from simvestr.helpers.auth import requires_auth, get_user
from simvestr.helpers.api_models import balance_model

api = Namespace('balance', description='Api for viewing balance for a User')

api.models[balance_model.name] = balance_model

@api.route("", doc=False)
class PortfolioPriceUsersQuery(Resource):
    @api.response(200, 'Successful')
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
    @api.doc(
        id="user_balance", 
        model=balance_model, 
        descriptions="User cash balance"
    )
    @requires_auth
    def get(self, ):
        user = get_user()

        data = dict(
            name=user.portfolio.portfolio_name,
            balance=user.portfolio.balance,
        )

        return data
