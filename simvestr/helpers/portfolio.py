from simvestr.models import Transaction, db



def balance(user):
    stocks = user.portfolio.stocks

    # stocks = [t.symbol for t in Transaction.query.with_entities(Transaction.symbol).distinct()] # all distinct symbols

# get disctinct stocks from transaction for user
stocks = Transaction.query.with_entities((Transaction.symbol).distinct())\
        .filter_by(trade_type = "settled", user_id = user_id).all()

get disctinct portfolios for user
portfolios = Transaction.query.with_entities((Transaction.portfolio_id).distinct())\
        .filter_by(trade_type = "settled", user_id = user_id).all()


for p in portfolios_list:
            for s in stocks_list:
                check_stock = Transaction.query.filter_by(
                    user_id = user_id, \
                    portfolio_id = p, \
                    symbol = s, \
                    trade_type = "settled" \
                ).all()
                if check_stock:
                    owned_stock = check_stock[-1]
                    if owned_stock.quantity >= 1:
                        data[owned_stock.id] = dict(
                                        user_id = owned_stock.user_id,
                                        portfolio_id = owned_stock.portfolio_id,
                                        symbol = owned_stock.symbol,
                                        quote = owned_stock.quote,
                                        # trade_type = owned_stock.trade_type,
                                        # timestamp = str(owned_stock.timestamp),
                                        quantity = owned_stock.quantity
                                        # fee = owned_stock.fee
                                    )
                else:
                    pass