from simvestr.models import User


def get_transactions(user: User):
    transactions = user.portfolio.transactions.all()
    transaction_list = [
            dict(
                symbol=t.symbol,
                quote=t.quote,
                timestamp=t.timestamp.timestamp(),
                quantity=t.quantity,
                fee=t.fee
            ) for t in transactions
        ]
    return {"transactions": transaction_list}

