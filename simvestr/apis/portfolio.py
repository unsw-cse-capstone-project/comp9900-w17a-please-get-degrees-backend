from flask_restx import Resource, Namespace, reqparse, fields

from simvestr.helpers.auth import get_user, requires_auth
from simvestr.helpers.portfolio import portfolio_value
from simvestr.models import Portfolio
from simvestr.helpers.api_models import portfolio_model, value_model, buy_sell_model

api = Namespace("portfolios", description="Api for viewing Portfolios")

api.models[value_model.name] = value_model
api.models[buy_sell_model.name] = buy_sell_model
api.models[portfolio_model.name] = portfolio_model

# TODO: Need to protect this endpoint from non-users
@api.route("")
class PortfoliosQuery(Resource):
    @api.response(200, "Successful")
    @api.response(601, "Portfolio doesn't exist")
    def get(self):
        portfolio_users = Portfolio.query.all()
        if not portfolio_users:
            return (
                {"error": True, "message": "Portfolio doesn't exist"},
                601,
            )

        data = {
            p.id: dict(id=p.id, user_id=p.user.id, portfolio_name=p.portfolio_name)
            for p in portfolio_users
        }
        payload = dict(data=data)
        return payload, 200


portfolio_query_parser = reqparse.RequestParser()
portfolio_query_parser.add_argument(
    "averagemode",
    type=str,
    help="Type of averaging for portfolio query. Options are 'alltime' or 'moving'.",
    default="moving"
)

@api.route("/user")
class PortfolioQuery(Resource):
    @api.response(200, "Successful")
    @api.response(601, "Portfolio doesn't exist")
    @api.expect(portfolio_query_parser)
    @api.doc(
        description="Show the user's current portfolio holdings and value",
        model=portfolio_model,

    )
    @requires_auth
    def get(self):
        user = get_user()
        args = portfolio_query_parser.parse_args()
        portfolio = portfolio_value(user, average_mode=args["averagemode"].lower())

        payload = dict(
            portfolio_name=user.portfolio.portfolio_name,
            balance=user.portfolio.balance,
            total_value=sum([x["value"] for x in portfolio]),
            portfolio=portfolio,
        )
        return payload, 200
