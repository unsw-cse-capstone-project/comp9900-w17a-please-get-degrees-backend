from flask_restx import Resource, Namespace, abort
from simvestr.models import User, Watchlist, Stock, Transaction
from simvestr.helpers.auth import get_email

api = Namespace(
    "view transactions",
    authorizations={
        "TOKEN-BASED": {"name": "API-TOKEN", "in": "header", "type": "apiKey"}
    },
    security="TOKEN-BASED",
    default="Buying and selling stocks",
    title="Simvestr",
    description="Demo api for querying transactions",
)


@api.route("")
class TransactionsQuery(Resource):
    def get(self):
        transaction = Transaction.query.all()
        data = {
            t.id: dict(
                user_id=t.user.id,
                portfolio_id=t.portfolio_id,
                symbol=t.symbol,
                quote=t.quote,
                trade_type=t.trade_type,
                timestamp=str(t.timestamp),
                quantity=t.quantity,
                fee=t.fee
            )
            for t in transaction
        }

        payload = dict(
            data=data
        )
        return payload


@api.route('/user/')
class TransactionQuery(Resource):
    def get(self, ):
        try:
            email = get_email()
        except Exception as e:
            abort(401, e)
        user = User.query.filter_by(email_id=email).first()
        transactions = user.portfolio.transactions
        data = {
            t.id: dict(
                user_id=user.id,
                portfolio_id=t.portfolio_id,
                symbol=t.symbol,
                quote=t.quote,
                trade_type=t.trade_type,
                timestamp=str(t.timestamp),
                quantity=t.quantity,
                fee=t.fee
            ) for t in transactions
        }

        return data
