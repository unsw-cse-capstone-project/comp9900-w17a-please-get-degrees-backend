from flask_restx import Model, fields

# field definitions here

email = fields.String(
    required=True,
    description="User email",
    example="test@test.com"
)

password = fields.String(
    required=True,
    description="User password",
    example="pass1234"
)

first_name = fields.String(
    required=True,
    description="User first name",
    example="Brett"
)

last_name = fields.String(
    required=True,
    description="User last name",
    example="Lee"
)

otp = fields.String(
    required=True,
    description="One time password",
    example="1234"
)

symbol = fields.String(
    required=True,
    description="Stock symbol",
    example="AAPL"
)

stock_type = fields.String(
    required=True,
    description="Stock type",
    example="stock",
    enum=(
        "stock",
        "crypto",
    )
)

stock_name = fields.String(
    required=True,
    description="Stock name",
    example="Apple Inc."
)

simple_quote = fields.Float(
    required=True,
    description="Quote price of the stock",
    example=100.0,
)

simple_quantity = fields.Integer(
    description="Number of stocks",
    example=5,
)

timestamp = fields.Integer(
    description="Unix timestamp",
    example=1569297600,
)

open_price = fields.Float(
            description="Open price",
            example=100.0)

high_price = fields.Float(
            description="High price",
            example=110.0)

low_price = fields.Float(
            description="Low price",
            example=95.0)

current_price = fields.Float(
            description="Current price",
            example=101.0)

close_price = fields.Float(
            description="Close price",
            example=101.0)

previous_close_price = fields.Float(
            description="Previous close price",
            example=101.0)

# Models here
forgotuser_email_model = Model(
    "Forgot User Email",
    {
        "email": email
    }
)

changepwd_model = Model(
    "Change Password",
    {
        "password": password
    },
)

changenames_model = Model(
    "Change Names",
    {
        "first_name": first_name,
        "last_name": last_name
    },
)

user_info_model = changenames_model.clone(
    "User Information",
    forgotuser_email_model
)

login_model = Model(
    "Login",
    {
        "email": email,
        "password": password,
    }
)

signup_model = login_model.clone(
    "Signup",
    changenames_model,
)



forgotuser_model = login_model.clone(
    "Forgot User",
    {
        "OTP": otp
    }
)


transaction_model = Model(
    "Transaction",
    {
        "symbol": symbol,
        "quote": simple_quote,
        "timestamp": timestamp,
        "quantity": simple_quantity,
        "fee": fields.Float(
            description="Fee of transaction",
            example=7.5,
        )
    }
)
transactions_model = Model(
    "Transactions",
    {
        "transactions": fields.List(fields.Nested(transaction_model)),
    }
)

candle_model = Model(
    "Candles",
    {
        "o": fields.List(open_price),
        "h": fields.List(high_price),
        "l": fields.List(low_price),
        "c": fields.List(close_price),
        "t": fields.List(timestamp),
    },
)
quote_model = Model(
    "Quote",
    {
        "o": open_price,
        "h": high_price,
        "l": low_price,
        "c": current_price,
        "pc": previous_close_price,
        "t": timestamp,
    },
)

watchlist_item_model = quote_model.clone(
    "Watchlist Item",
    {
        "symbol": symbol,
        "name": stock_name,
    }
)

watchlist_model = Model(
    "Watchlist",
    {
        "watchlist": fields.List(fields.Nested(watchlist_item_model)),
    }
)


market_order_model = Model(
    "Market Order",
    {
        "symbol": symbol,
        "quote": current_price,
        "trade_type": fields.String(
            required=True,
            description="Stock symbol for transaction",
            example="buy",
            enum=[
                "buy",
                "sell"
            ]
        ),
        "quantity": fields.Integer(
            required=True,
            description="Quote price per share of stock",
            example=5
        ),
    },
)

details_model = Model(
    "Stock Details",
    {
        "type": stock_type,
        "symbol": symbol,
        "name": stock_name,
        "industry": fields.String(
            description="Industry classification",
            example="Technology",
        ),
        "exchange": fields.String(
            description="Listed exchange",
            example="NASDAQ/NMS",
        ),
        "logo": fields.String(
            description="Logo image",
            example="https://static.finnhub.io/logo/87cb30d8-80df-11ea-8951-00000000092a.png",
        ),
        "marketCapitalization": fields.Float(
            description="Market capitalisation",
            example=1415993,
        ),
        "quote": fields.Nested(quote_model, skip_none=False),
    },
)

buy_sell_model = Model(
    "Buy and Sell Model",
    {
        "weighted_average": fields.Float(
            description="Weighted average of the buy or sell price",
            example=50.0,
        ),
        "weighted_average_fee": fields.Float(
            description="Weighted average of the fee's",
            example=3.5,
        ),
        "total": fields.Float(
            desciption="Total value of transactions",
            example=500.0
        )
    }
)

value_model = Model(
    "Value Model",
    {
        "symbol": symbol,
        "quantity": simple_quantity,
        "quote": simple_quote,
        "value": fields.Float(
            description="Value of the trade or stock balance",
            example=500.0,
        ),
        "return":fields.Float(
            description="Absolute profit or loss of investment",
            example=50.0
        ),
        "buy": fields.Nested(
            buy_sell_model
        ),
        "sell": fields.Nested(
            buy_sell_model
        ),
    }
)


balance_model = Model(
    "UserBalance",
    {
        "name": fields.String(
            description="Portfolio name",
            example="John Doe's Portfolio"
        ),
        "balance": fields.Float(
            description="Current cash balance",
            example=55000.0,
        ),

    },
)

portfolio_model = balance_model.clone(
    "Portfolio",
    {
        "total_value": fields.Float(
            description="The sum of the current cash balance and the value of the current holdings",
            example=55500.0
        ),
        "total_return": fields.Float(
            description="Total portfolio return",
            example=500.00
        ),
        "portfolio": fields.List(
            fields.Nested(value_model, skip_none=False)
        ),
    },
)

portfolio_historic_model = Model(
    "Historic Portfolios",
    {
        "close_balance": fields.List(close_price),
        "investment_value": fields.List(fields.Float(
            description="Closing investment value",
            example=55000.0
        )),
        "timestamp": fields.List(timestamp),

    }
)

user_model = Model(
    "User",
    {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
    }
)

user_details_model = user_model.inherit(
    "User Details",
    portfolio_model,
    watchlist_model,
    transactions_model,
)


stock_owned_model = Model(
    "Stock Owned",
    {
        "symbol": symbol,
        "quantity": simple_quantity,
    }
)

stocks_owned_model = Model(
    "Stocks Owned",
    {
        "stocksowned": fields.List(fields.Nested(stock_owned_model))
    }
)
