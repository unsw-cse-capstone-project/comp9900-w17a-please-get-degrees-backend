from flask import current_app

from simvestr.helpers.search import get_details


def check_price(symbol, quote):
    stock_details = get_details(symbol.upper())

    current_quote = stock_details["quote"]["c"]
    cost_diff = abs(current_quote - quote)
    allowed_cost_diff = current_app.config["SLIPPAGE"] * quote  # cost difference of 0.05%

    # if the cost hasn't changed more than 0.05% OR
    # if quote is same as current price, commit transaction
    if cost_diff <= allowed_cost_diff or current_quote == quote:
        return False, cost_diff

    return True, cost_diff
