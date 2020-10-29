from flask import jsonify
from flask_restx import Resource, Namespace
from sqlalchemy import func, and_

from simvestr.models import Portfolio, PortfolioPrice
from simvestr.models import db

api = Namespace("leader board", description="Leaderboard")


@api.route("/position/<int:user_id>")
class PortfolioQuery(Resource):
    @api.response(200, "Successful")
    @api.response(602, "PortfolioPrice doesn\'t exist")
    def get(self, user_id: int):
        subq = db.session.query(
            PortfolioPrice.user_id,
            func.max(PortfolioPrice.timestamp).label("maxdate")
        ).group_by(PortfolioPrice.user_id).subquery("t2")
        
        close_balances = []
        for p in db.session.query(PortfolioPrice).join(subq, and_(
                PortfolioPrice.user_id == subq.c.user_id,
                PortfolioPrice.timestamp == subq.c.maxdate
            )
        ):
            close_balances.append({"user": p.user_id, "close_balance": p.close_balance})
        balances_sorted = sorted(close_balances, key=lambda i: i["close_balance"], reverse=True)
        
        pos = 1
        while (balances_sorted[pos - 1]["user"] != user_id):
            pos += 1
        suffix = ["th", "st", "nd", "rd", "th"][min(pos % 10, 4)]
        if 11 <= (pos % 100) <= 13:
            suffix = "th"
        return jsonify(str(pos) + suffix)


@api.route("/top/<int:num_ports>")
class TopInvestors(Resource):
    @api.response(200, "Successful")
    @api.response(602, "PortfolioPrice doesn\'t exist")
    def get(self, num_ports: int = 6):
        subq = db.session.query(
            PortfolioPrice.user_id,
            func.max(PortfolioPrice.timestamp).label("maxdate")
        ).group_by(PortfolioPrice.user_id).subquery("t2")
        
        close_balances = []
        for p in db.session.query(PortfolioPrice).join(subq, and_(
            PortfolioPrice.user_id == subq.c.user_id,
            PortfolioPrice.timestamp == subq.c.maxdate)
        ):
            close_balances.append({"user": p.user_id, "close_balance": p.close_balance})
        balances_sorted = sorted(close_balances, key=lambda i: i["close_balance"], reverse=True)

        users = []
        idAndBalance = {}
        for i in range(num_ports):
            idAndBalance.update({balances_sorted[i]["user"]: balances_sorted[i]["close_balance"]})
            users.append(balances_sorted[i]["user"])
        top_portfolios = []
        for p in db.session.query(Portfolio).join(Portfolio.user).filter(Portfolio.user_id.in_(users)).all():
            top_portfolios.append({"id": p.user_id, "user": p.user.first_name +
                          " "+p.user.last_name, "name": p.portfolio_name, "value": idAndBalance[p.user_id]})

        return jsonify(top_portfolios)
