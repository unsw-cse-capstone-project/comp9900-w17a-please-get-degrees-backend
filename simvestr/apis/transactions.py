from flask_restx import Resource, Namespace

from simvestr.helpers.transactions import get_transactions
from simvestr.helpers.auth import get_user, requires_auth
from simvestr.models.api_models import transactions_model, transaction_model

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

api.models[transaction_model.name] = transaction_model
api.models[transactions_model.name] = transactions_model


@api.route("")
class TransactionQuery(Resource):
    @api.response(200, "Success")
    @api.doc(
        model=transactions_model,
        description="All transactions for a user"
    )
    @api.marshal_with(transactions_model)
    @requires_auth
    def get(self, ):
        user = get_user()
        data = get_transactions(user)
        return data, 200
