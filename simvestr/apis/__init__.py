from flask_restx import Api

# Import the api variable from each of the namespaces (api files) and alias them
from .user import api as ns1
from .signup import api as ns2
from .token import api as ns3
from .verifytoken import api as ns4
from .forgotuser import api as ns5
from .search import api as ns6
from .marketorder import api as ns7
from .viewstocksowned import api as ns8
from .viewportfolio import api as ns9
from .viewbalance import api as ns10
from .viewtransaction import api as ns11
from .changedetails import api as ns12
from .watchlist import api as ns13
from .leaderboard import api as ns14
from .logout import api as ns15

from flask import Blueprint

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")

api = Api(
    blueprint,
    title="SimvestrAPI",
    version="0.01",
    description="Simvestr api",
    # All API metadatas
)

# Register each new namespace here
api.add_namespace(ns1, path="/user")
api.add_namespace(ns2, path="/signup")
api.add_namespace(ns3, path="/token")
api.add_namespace(ns4, path="/verifytoken")
api.add_namespace(ns5, path="/forgotuser")
api.add_namespace(ns6, path="/search")
api.add_namespace(ns7, path="/marketorder")
api.add_namespace(ns8, path="/viewstocksowned")
api.add_namespace(ns9, path="/viewportfolio")
api.add_namespace(ns10, path="/viewbalance")
api.add_namespace(ns11, path="/viewtransaction")
api.add_namespace(ns12, path="/changedetails")
api.add_namespace(ns13, path="/watchlist")
api.add_namespace(ns14, path="/leaderboard")
api.add_namespace(ns15, path="/logout")
