from flask_restx import Resource, Namespace
from ..models import User, Watchlist, Stock, Portfolio, PortfolioPrice
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
    
@api.route('/<int:portfolio_id>')
class PortfolioQuery(Resource):
    @api.response(200, 'Successful')
    @api.response(601, 'Portfolio doesn\'t exist')
    def get(self, portfolio_id: int):
        portfolio_users = Portfolio.query.filter_by(id = portfolio_id).first()
        p = portfolio_users
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
                    )
                }
        payload = dict(
            data=data
        )
        return payload
