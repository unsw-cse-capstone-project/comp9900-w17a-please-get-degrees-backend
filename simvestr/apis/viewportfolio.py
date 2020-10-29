from flask_restx import Resource, Namespace

from simvestr.helpers.auth import get_user
from simvestr.helpers.portfolio import all_stocks_balance
from simvestr.models import Portfolio

api = Namespace('view portfolios', description = 'Api for viewing Portfolios')

#TODO: Need to protect this endpoint from non-users
@api.route("")
class PortfoliosQuery(Resource):
    @api.response(200, 'Successful')
    @api.response(601, 'Portfolio doesn\'t exist')
    def get(self):
        portfolio_users = Portfolio.query.all()
        if not portfolio_users:
            return (
                {"error": True, "message": "Portfolio doesn\'t exist"}, 
                601,
            )

        data = {
                    p.id:dict(
                        id=p.id,
                        user_id=p.user.id,
                        portfolio_name=p.portfolio_name
                    ) for p in portfolio_users
                }
        payload = dict(
            data=data
        )
        return payload, 200
    
@api.route('/user')
class PortfolioQuery(Resource):
    @api.response(200, 'Successful')
    @api.response(601, 'Portfolio doesn\'t exist')
    def get(self, portfolio_id: int):
        user = get_user()
        # if not portfolio_users: #redundant
        #     return (
        #         {"error": True, "message": "Portfolio doesn\'t exist"},
        #         601,
        #     )
        data = {
            user.id: dict(
                portfolio_name=user.portfolio.portfolio_name,
                balance=user.portfolio.portfolioprice[-1].close_balance,
                portfolio=all_stocks_balance(user)
            )
        }
        payload = dict(
            data=data
        )
        return payload
