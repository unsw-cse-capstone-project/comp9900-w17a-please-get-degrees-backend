from simvestr.models import db
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import func, and_, join
from flask import jsonify
from flask_restx import Resource, reqparse, Namespace
from sqlalchemy.sql import select
from simvestr.models import User, Watchlist, Stock, Portfolio, PortfolioPrice
from simvestr.helpers.auth import requires_auth, get_user

api = Namespace("leader board", description="Leaderboard")

DEFAULT_LEADER_COUNT = 6

authorizations = {
    "TOKEN-BASED": {
        "name": "API-TOKEN",
        "in": "header",
        "type": "apiKey"
    }
}
api = Namespace(
    'leaderboard',
    authorizations=authorizations,
    security="TOKEN-BASED",
    description="query for leaderboard"
)


def getOrderedPortfolios():
    # returns array of {"porfolio_id","close_balance"} objects ordered by closing balance
    subq = db.session.query(PortfolioPrice.portfolio_id, func.max(PortfolioPrice.timestamp).label(
        "maxdate")).group_by(PortfolioPrice.portfolio_id).subquery("t2")
    close_balances = []
    for p in db.session.query(PortfolioPrice).join(subq, and_(
        PortfolioPrice.portfolio_id == subq.c.portfolio_id,
        PortfolioPrice.timestamp == subq.c.maxdate
    )
    ):
        close_balances.append(
            {"portfolio": p.portfolio_id, "close_balance": p.close_balance})
    return sorted(close_balances, key=lambda i: i["close_balance"], reverse=True)


def topPortfolios(num_ports, first):
    # returns array of the top <num_ports> objects {"id","position","user","value"} starting at <first>
    first -= 1  # set index start to zero
    balances_sorted = getOrderedPortfolios()
    users = []
    idAndBalance = {}
    top_portfolios = []
    # return all of them if num_port is -1 otherwise up to num_ports starting at start
    num_ports = min(len(balances_sorted)-first,
                    num_ports) if (num_ports != -1) else len(balances_sorted)
    if(num_ports > 0):
        for i in range(num_ports):
            idAndBalance.update(
                {balances_sorted[i+first]["portfolio"]: [balances_sorted[i+first]["close_balance"], i+first+1]})
            users.append(balances_sorted[i+first]["portfolio"])

        for p in db.session.query(Portfolio).join(Portfolio.user).filter(Portfolio.id.in_(users)).all():
            top_portfolios.append({"id": p.id, "position": idAndBalance[p.id][1], "user": p.user.first_name +
                                   " "+p.user.last_name, "name": p.portfolio_name, "value": idAndBalance[p.id][0]})
            first += 1
    return top_portfolios


@ api.route("/position")
class PortfolioQuery(Resource):
    @ api.response(200, "Successful")
    @ api.response(602, "PortfolioPrice doesn\'t exist")
    @ api.doc(
        description="Gets position of user's portfolio",
        security=["TOKEN-BASED"]
    )
    @requires_auth
    def get(self):
        try:
            user = get_user()
        except Exception as e:
            abort(401, e)
        portfolio_id = user.portfolio.id
        balances_sorted = getOrderedPortfolios()
        pos = 1
        while (balances_sorted[pos - 1]["portfolio"] != portfolio_id):
            pos += 1
        suffix = ["th", "st", "nd", "rd", "th"][min(pos % 10, 4)]
        if 11 <= (pos % 100) <= 13:
            suffix = "th"
        return jsonify(str(pos) + suffix)


@api.route("/top/<int:num_ports>")
class TopInvestors(Resource):
    @api.response(200, "Successful")
    @api.response(602, "PortfolioPrice doesn\'t exist")
    @api.doc(
        description="Gets <num_ports> highest value portfolios",
    )
    def get(self, num_ports: int = DEFAULT_LEADER_COUNT):
        return jsonify(topPortfolios(num_ports, 1))


@api.route("/all")
class TopInvestorsAll(Resource):
    @api.response(200, "Successful")
    @api.response(602, "PortfolioPrice doesn\'t exist")
    @api.doc(
        description="Gets all the portfolios",
    )
    def get(self):
        # -1 to indicate all portfolios should be returned
        return jsonify(topPortfolios(-1, 1))


@api.route("/range/<int:num_ports>/<int:first>")
class TopInvestorsRange(Resource):
    @api.response(200, "Successful")
    @api.response(602, "PortfolioPrice doesn\'t exist")
    @api.doc(
        description="Gets <num_ports> highest value portfolios, starting at <first> position",
    )
    def get(self, num_ports: int = DEFAULT_LEADER_COUNT, first: int = 1):
        return jsonify(topPortfolios(num_ports, first))


@api.route("/nearuser/<int:num_ports>")
class TopInvestorsAll(Resource):
    @ api.response(200, "Successful")
    @ api.response(602, "PortfolioPrice doesn\'t exist")
    @ api.doc(
        description="Gets a maximum of <num_port> portfolios with the users portfolio in the middle",
    )
    @requires_auth
    def get(self, num_ports: int = DEFAULT_LEADER_COUNT):
        try:
            user = get_user()
        except Exception as e:
            abort(401, e)
        portfolio_id = user.portfolio.id
        balances_sorted = getOrderedPortfolios()
        pos = 1
        while (balances_sorted[pos - 1]["portfolio"] != portfolio_id):
            pos += 1
        start = max(1, pos - (num_ports//2) + 1)
        return jsonify(topPortfolios(num_ports, start))


@api.route('/add/<port>/<balance>')
class PortfolioQuery(Resource):
    @api.response(200, 'Successful')
    @api.response(602, 'PortfolioPrice doesn\'t exist')
    @ api.doc(
        description="test endpoint to change portfolio balances",
    )
    def put(self, port, balance):
        portf = PortfolioPrice(
            portfolio_id=port, close_balance=balance)
        db.session.add(portf)
        db.session.commit()
