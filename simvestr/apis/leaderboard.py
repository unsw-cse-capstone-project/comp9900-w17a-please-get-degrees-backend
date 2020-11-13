from simvestr.models import db
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import func, and_, join, desc
from flask import jsonify
from flask_restx import Resource, reqparse, Namespace
from sqlalchemy.sql import select
from simvestr.models import User, Watchlist, Stock, Portfolio, PortfolioPrice
from simvestr.helpers.auth import requires_auth, get_user
from simvestr.models.api_models import leaderboard_all_model, leaderboard_position_model
api = Namespace("leader board", description="Leaderboard")

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

api.models[leaderboard_all_model.name] = leaderboard_all_model
api.models[leaderboard_position_model.name] = leaderboard_position_model

ORDINAL_SUFFIXES = ["th", "st", "nd", "rd", "th"]

def get_ordered_portfolios():
    # returns array of {"porfolio_id","value"} objects ordered by value of the portfolio (closing_balance + investment value)
    subq = db.session.query(PortfolioPrice.portfolio_id, func.max(PortfolioPrice.timestamp).label(
        "maxdate")).group_by(PortfolioPrice.portfolio_id).subquery("t2")
    close_balances = []
    for p in db.session.query(PortfolioPrice).join(subq, and_(
        PortfolioPrice.portfolio_id == subq.c.portfolio_id,
        PortfolioPrice.timestamp == subq.c.maxdate
    )
    ):
        value = p.close_balance + p.investment_value
        close_balances.append(
            {"portfolio": p.portfolio_id, "value": value})
    return sorted(close_balances, key=lambda i: (i["value"],i['portfolio']), reverse=True)


@ api.route("/position")
class PortfolioQuery(Resource):
    @ api.response(200, "Successful")
    @ api.response(602, "PortfolioPrice doesn\'t exist")
    @api.doc(
        model=leaderboard_position_model,
        description="users positions in leaderboard"
    )
    #@api.marshal_with(leaderboard_position_model)
    @requires_auth
    def get(self):
        user = get_user()
        portfolio_id = user.portfolio.id
        
        # get the balances of all the portfolios
        balances_sorted = get_ordered_portfolios()
        
        # get the value of the users portfolio
        p = PortfolioPrice.query.filter(PortfolioPrice.portfolio_id == portfolio_id).order_by(PortfolioPrice.timestamp.desc()).first()
        my_value = p.close_balance + p.investment_value
        
        # find the position on the screen
        pos_screen = 1
        while (balances_sorted[pos_screen - 1]["portfolio"] != portfolio_id):
            pos_screen += 1
        
        # find actual position in the leaderboard - maybe higher than displayed position if duplicate portfolio balances
        pos_actual = pos_screen
        while( (pos_actual > 0) and (my_value == balances_sorted[pos_actual-1]["value"]) ) :
            pos_actual -= 1
        pos_actual += 1

        # add the ordinal suffix to the actual position
        suffix = ORDINAL_SUFFIXES[min(pos_actual % 10, 4)]
        if 11 <= (pos_actual % 100) <= 13:
            suffix = "th"
        return jsonify({"nominal": pos_screen, "ordinal": str(pos_actual) + suffix})

@api.route("/all")
class TopInvestorsAll(Resource):
    @api.response(200, "Successful")
    @api.response(602, "PortfolioPrice doesn\'t exist")
    @api.doc(
        model=leaderboard_all_model,
        description="returns basic detail of all portfolios"
    )
    #@api.marshal_with(leaderboard_all_model)
    def get(self):
        balances_sorted = get_ordered_portfolios()
        users = []
        id_value_pos = {}
        portfolios = []
        num_ports = len(balances_sorted) # number of portfolios in the database
        if(num_ports > 0):
            portfolio_position = 1
            previous_value = -1 # store the previous portfolio value to check for same value portfolios
            for i in range(num_ports):
                if (previous_value != balances_sorted[i]["value"]) :
                    portfolio_position = i+1
                previous_value = balances_sorted[i]["value"]
                id_value_pos.update(
                    {balances_sorted[i]["portfolio"]: [balances_sorted[i]["value"], portfolio_position]})
                users.append(balances_sorted[i]["portfolio"])
            for p in db.session.query(Portfolio).join(Portfolio.user).filter(Portfolio.id.in_(users)).all():
                portfolios.append({"id": p.id, "position": id_value_pos[p.id][1], "user": p.user.first_name +
                                   " "+p.user.last_name, "name": p.portfolio_name, "value": id_value_pos[p.id][0]})
        return jsonify(portfolios)
