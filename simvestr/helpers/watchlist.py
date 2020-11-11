from simvestr.models import User
from simvestr.helpers.search import search


def get_watchlist(user: User):
    watchlist_list = []
    for stock in user.watchlist.stocks:
        watchlist_list.append(
            {
                "symbol": stock.symbol,
                "name": stock.name,
                "quote": search(query="quote", arg=stock.symbol)["c"]
            }
        )
    return {"watchlist": watchlist_list}


def in_watchlist(symbol: str, user: User) -> bool:
    stock = [s.symbol for s in user.watchlist.stocks if s.symbol == symbol]
    if stock:
        return True
    return False
