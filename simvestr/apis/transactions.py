from flask_restx import Resource, Namespace

from simvestr.helpers.auth import get_user
from simvestr.models import Transaction

api = Namespace(
    "transactions",
    authorizations={
        "TOKEN-BASED": {"name": "API-TOKEN", "in": "header", "type": "apiKey"}
    },
    security="TOKEN-BASED",
    default="Buying and selling stocks",
    title="Simvestr",
    description="View transactions for a user",
)


@api.route("")
class TransactionsQuery(Resource):
    def get(self):
        transaction = Transaction.query.all()
        data = {
            t.id: dict(
                portfolio_id=t.portfolio_id,
                symbol=t.symbol,
                quote=t.quote,
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


@api.route("/user/")
class TransactionQuery(Resource):
    def get(self, ):
        user = get_user()
        transactions = user.portfolio.transactions
        data = {
            t.id: dict(
                user_id=user.id,
                portfolio_id=t.portfolio_id,
                symbol=t.symbol,
                quote=t.quote,
                timestamp=str(t.timestamp),
                quantity=t.quantity,
                fee=t.fee
            ) for t in transactions
        }

        return data
