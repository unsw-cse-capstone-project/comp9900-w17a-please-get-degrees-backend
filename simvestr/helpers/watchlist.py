from simvestr.models import User
from simvestr.helpers.search import search


def get_watchlist(user: User):
    watchlist_list = []
    for item in user.watchlist.watchlist_items:
        watchlist_list.append(
            {
                "symbol": item.stock.symbol,
                "name": item.stock.name,
                "date_added": item.date_added.timestamp(),
                **search(query="quote", arg=item.stock.symbol)
            }
        )
    return {"watchlist": watchlist_list}


def in_watchlist(symbol: str, user: User) -> bool:
    stock = [s.symbol for s in user.watchlist.stocks if s.symbol == symbol]
    if stock:
        return True
    return False
