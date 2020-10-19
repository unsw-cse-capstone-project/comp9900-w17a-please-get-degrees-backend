from flask_restx import Resource, Namespace
from ..models import User, Watchlist, Stock, Portfolio, PortfolioPrice
api = Namespace('view closing balance', description = 'Api for viewing closing balance for a User')

@api.route("")
class PortfolioPriceUsersQuery(Resource):
    @api.response(200, 'Successful')
    @api.response(602, 'Portfolio for this user doesn\'t exist')
    def get(self):
        
        portprice = PortfolioPrice.query.filter_by().all()
        
        if not portprice:
            return (
                {"error": True, "message": "Portfolio for this user doesn\'t exist"}, 
                602,
            )
        
        data = dict(
                    plist = [dict(portfolio_id = p.id, balance = p.close_balance, time = str(p.timestamp)) for p in portprice]
                    ) 
        payload = dict(
                        data = data
                      )
        return payload
    
@api.route('/<int:user_id>')
class PortfolioPriceQuery(Resource):
    @api.response(200, 'Successful')
    @api.response(602, 'Portfolio for this user doesn\'t exist')
    def get(self, user_id: int):
        
        
        port = Portfolio.query.filter_by(user_id = user_id).first()
        portprice = PortfolioPrice.query.filter_by(user_id = port.user_id).first()
        
        if not port:
            return (
                {"error": True, "message": "Portfolio for this user doesn\'t exist"}, 
                602,
            )
        if not portprice:
            return (
                {"error": True, "message": "Portfolio Price for this user doesn\'t exist"}, 
                602,
            )
        
        data = dict(name = port.portfolio_name,
                    portfolio_id = portprice.id, 
                    balance = portprice.close_balance, 
                    time = str(portprice.timestamp)
                    )
        payload = dict(
                        data = data
                      )
        return payload
    
    
@api.route('/<int:user_id>/<int:portfolio_id>')
class PortfolioPriceUserQuery(Resource):
    @api.response(200, 'Successful')
    @api.response(602, 'Portfolio for this user doesn\'t exist')
    def get(self, user_id: int, portfolio_id: int):
        
        
        port = Portfolio.query.filter_by(user_id = user_id, id = portfolio_id).first()
        portprice = PortfolioPrice.query.filter_by(user_id = user_id, portfolio_id = portfolio_id).first()
        
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
        
        data = dict(user_id = port.user_id, portfolio_name = port.portfolio_name, close_balance = portprice.close_balance)
        payload = { portprice.id : data }
        return payload
