from flask_restx import Resource, Namespace
from ..models import User, Watchlist, Stock, Transaction


api = Namespace(
    "view transactions",
    authorizations = {
        "TOKEN-BASED": {"name": "API-TOKEN", "in": "header", "type": "apiKey"}
    },
    security = "TOKEN-BASED",
    default = "Buying and selling stocks",
    title = "Simvestr",
    description = "Demo api for querying transactions",
)

@api.route("")
class TransactionsQuery(Resource):
    def get(self):
        transaction = Transaction.query.all()
        data = {
                    t.id:dict(user_id = t.user_id, portfolio_id = t.portfolio_id, symbol = t.symbol, \
                          cost = t.cost, trade_type = t.trade_type, timestamp = str(t.timestamp), \
                          quantity = t.quantity, fee = t.fee) 
                for t in transaction
            }
            
        payload = dict(
            data = data
        )
        return payload
    

@api.route('/<int:portfolio_id>')
class TransactionQuery(Resource):
    def get(self, portfolio_id: int):
        transaction = Transaction.query.filter_by(portfolio_id = portfolio_id).all()
        data = {
                    t.id:dict(user_id = t.user_id, portfolio_id = t.portfolio_id, symbol = t.symbol, \
                          cost = t.cost, trade_type = t.trade_type, timestamp = str(t.timestamp), \
                          quantity = t.quantity, fee = t.fee) 
                for t in transaction
            }
        return data
