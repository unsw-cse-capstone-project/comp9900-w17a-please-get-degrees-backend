from flask_restx import Resource, Namespace, abort
from simvestr.models import User, Watchlist, Stock, Portfolio, PortfolioPrice
from simvestr.helpers.auth import requires_auth, get_user

api = Namespace('view closing balance', description='Api for viewing closing balance for a User')


@api.route("")
class PortfolioPriceUsersQuery(Resource):
    @api.response(200, 'Successful')
    @api.response(602, 'Portfolio for this user doesn\'t exist')
    @requires_auth
    def get(self):

        user = get_user()

        data = dict(
            plist=[dict(
                portfolio_id=p.id,
                balance=p.close_balance,
                time=str(p.timestamp)
            ) for p in user.portfolio.portfolioprice]
        )
        payload = dict(
            data=data
        )
        return payload



@api.route('/user/')
class PortfolioPriceQuery(Resource):
    @api.response(200, 'Successful')
    @api.response(602, 'Portfolio for this user doesn\'t exist')
    @requires_auth
    def get(self, ):
        user = get_user()

        data = dict(
            name=user.portfolio.portfolio_name,
            portfolio_id=user.portfolio.portfolioprice[-1].id,
            balance=user.portfolio.portfolioprice[-1].close_balance,
            time=str(user.portfolio.portfolioprice[-1].timestamp),

        )
        payload = dict(
            data=data
        )
        return payload


@api.route('/user/detailed')
class PortfolioPriceUserQuery(Resource):
    @api.response(200, 'Successful')
    @api.response(602, 'Portfolio for this user doesn\'t exist')
    @requires_auth
    def get(self):
        try:
            email = get_email()
        except Exception as e:
            abort(401, e)

        user = User.query.filter_by(email_id=email).first()
        port = Portfolio.query.filter_by(user_id=user_id, id=portfolio_id).first()
        portprice = PortfolioPrice.query.filter_by(user_id=user_id, portfolio_id=portfolio_id).first()

        if not port:
            return (
                {"error": True, "message": "Portfolio for this user doesn\'t exist"},
                602,
            )
        if not portprice:
            return (
                {"error": True, "message": "Portfolio for this user doesn\'t exist"},
                602,
            )

        data = dict(user_id=port.user_id, portfolio_name=port.portfolio_name, close_balance=portprice.close_balance)
        payload = {portprice.id: data}
        return payload
