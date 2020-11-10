from flask_restx import Model, fields

signup_model = Model(
    "Signup",
    {
        "email": fields.String(
            required=True,
            description="User email",
            example="test@gmail.com"
        ),
        "password": fields.String(
            required=True,
            description="User password",
            example="pass1234"
        ),
        "first_name": fields.String(
            required=True,
            description="User first name",
            example="Brett"
        ),
        "last_name": fields.String(
            required=True,
            description="User last name",
            example="Lee"
        ),
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
        )
    }
)

value_model = Model(
    "Value Model",
    {
        "stock": fields.String(
            description="Stock or asset in portfolio",
            example="AAPL",
        ),
        "quantity": fields.Integer(
            description="Number of stocks",
            example=5,
        ),
        "quote": fields.Float(
            description="Quyote price of the stock",
            example=100.0,
        ),
        "value": fields.Float(
            description="Value of the trade or stock balance",
            example=500.0,
        ),
        "buy": fields.Nested(
            buy_sell_model
        ),
        "sell": fields.Nested(
            buy_sell_model
        ),
    }
)

portfolio_model = Model(
    "Portfolio",
    {
        "portfolio_name": fields.String(
            description="Portfolio name",
            example="John Doe's Portfolio"
        ),
        "balance": fields.Float(
            description="Current cash balance",
            example=55000.0
        ),
        "total_value": fields.Float(
            description="The sum of the current cash balance and the value of the current holdings",
            example=55500.0
        ),
        "portfolio": fields.List(
            fields.Nested(value_model, skip_none=False)
        ),
    },
)