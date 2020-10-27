from simvestr.models import User, Transaction, db


def all_stocks_balance(user: User):
    all_stocks = user.portfolio.transactions.with_entities(
        db.func.sum(Transaction.quantity).label("balance"),
        Transaction.symbol
    ).group_by("symbol").all()

    return {n: q for (q, n) in all_stocks if q > 0}


def stock_balance(user: User, symbol):
    return user.portfolio.transactions.with_entities(
        db.func.sum(Transaction.quantity).label("balance"),
        Transaction.symbol
    ).filter_by(
        symbol=symbol
    ).group_by("symbol").first()
