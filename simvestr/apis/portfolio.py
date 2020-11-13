from flask_restx import Resource, Namespace, reqparse, abort

from simvestr.helpers.auth import get_user, requires_auth
from simvestr.helpers.portfolio import (
    get_portfolio,
    all_stocks_balance,
    get_stocks_owned,
    get_close_balance,
)
from simvestr.models import Portfolio
from simvestr.models.api_models import (
    portfolio_model,
    value_model,
    buy_sell_model,
    stocks_owned_model,
    stock_owned_model,
    portfolio_historic_model,
    portfolios_historic_model,
)

api = Namespace("portfolios", description="Api for viewing Portfolios")

api.models[value_model.name] = value_model
api.models[buy_sell_model.name] = buy_sell_model
api.models[portfolio_model.name] = portfolio_model
api.models[portfolio_historic_model.name] = portfolio_historic_model
api.models[portfolios_historic_model.name] = portfolios_historic_model
api.models[stock_owned_model.name] = stock_owned_model
api.models[stocks_owned_model.name] = stocks_owned_model

portfolio_query_parser = reqparse.RequestParser()
portfolio_query_parser.add_argument(
    "averagemode",
    type=str,
    help="Type of averaging for portfolio query. Options are 'alltime' or 'moving'.",
    default="moving",
    choices=("moving", "alltime"),
    required=True,
)


@api.route("")
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


@api.route("/historic")
class PortfolioHistory(Resource):
    @requires_auth
    @api.response(200, "Successful")
    @api.response(400, "Invalid Input")
    @api.expect(portfolio_history_parser)
    @api.doc(
        description="Show the user's current portfolio holdings and value",
        model=portfolios_historic_model,
    )
    # @api.marshal_with(portfolios_historic_model)
    def get(self):
        user = get_user()
        args = portfolio_history_parser.parse_args()
        if args["number_of_days"] < 1:
            return abort(400, "Number of days must be a non zero positive integer")
        history = get_close_balance(user, **args)
        return history, 200
