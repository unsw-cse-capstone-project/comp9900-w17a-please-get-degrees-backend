from flask_restx import Resource, Namespace, reqparse

from simvestr.helpers.auth import get_user, requires_auth
from simvestr.helpers.portfolio import get_portfolio, all_stocks_balance, get_stocks_owned, get_close_balance
from simvestr.models import Portfolio
from simvestr.models.api_models import portfolio_model, value_model, buy_sell_model, stocks_owned_model, \
    stock_owned_model, portfolio_historic_model

api = Namespace("portfolios", description="Api for viewing Portfolios")

api.models[value_model.name] = value_model
api.models[buy_sell_model.name] = buy_sell_model
api.models[portfolio_model.name] = portfolio_model
api.models[portfolio_historic_model.name] = portfolio_historic_model
api.models[stock_owned_model.name] = stock_owned_model
api.models[stocks_owned_model.name] = stocks_owned_model


# TODO: Need to protect this endpoint from non-users
@api.route("")
class PortfoliosQuery(Resource):
    @api.response(200, "Successful")
    @api.response(404, "Portfolio not found")
    def get(self):
        portfolio_users = Portfolio.query.all()
        if not portfolio_users:
            return (
                {"error": True, "message": "Portfolio not found"},
                404,
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
    default="moving",
    choices=("moving", "alltime"),
    required=True,
)


@api.route("/user")
class PortfolioQuery(Resource):
    @requires_auth
    @api.response(200, "Successful")
    @api.expect(portfolio_query_parser)
    @api.doc(
        description="Show the user's current portfolio holdings and value",
        model=portfolio_model,
    )
    @api.marshal_with(portfolio_model)
    def get(self):
        user = get_user()
        args = portfolio_query_parser.parse_args()
        payload = get_portfolio(user, args["averagemode"])
        return payload, 200

portfolio_history_parser = reqparse.RequestParser()
portfolio_history_parser.add_argument(
    "number_of_days",
    type=int,
    help="The max number of days to retrieve for historic portfolio",
    default=7,
)

@api.route("/user/historic")
class PortfolioHistory(Resource):
    @requires_auth
    @api.response(200, "Successful")
    @api.expect(portfolio_history_parser)
    @api.doc(
        description="Show the user's current portfolio holdings and value",
        model=portfolio_historic_model, #TODO
    )
    def get(self):
        user = get_user()
        args = portfolio_history_parser.parse_args()
        history = get_close_balance(user, **args)
        return history, 200


@api.route("/user/stocksowned")
class StocksOwned(Resource):
    @api.response(200, "Successful")
    @api.doc(
        description="List of the current stock holdings",
        model=stocks_owned_model,
    )
    @api.marshal_with(stocks_owned_model)
    @requires_auth
    def get(self):
        user = get_user()
        stocks_owned = get_stocks_owned(user)
        # return only stocks greater than zero
        return stocks_owned, 200
