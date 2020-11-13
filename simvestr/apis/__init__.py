from flask_restx import Api
from flask import Blueprint

# Import the api variable from each of the namespaces (api files) and alias them
from .signup import api as ns1
from .login import api as ns2
from .logout import api as ns3
from .forgotuser import api as ns4
from .changedetails import api as ns5
from .user import api as ns6
from .search import api as ns7
from .watchlist import api as ns8
from .marketorder import api as ns9
from .portfolio import api as ns10
from .transactions import api as ns11
from .leaderboard import api as ns12
from .exportfolio import api as ns13

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")

api = Api(
    blueprint,
    title="SimvestrAPI",
    version="0.01",
    description="Simvestr api",
    # All API metadatas
)

# Register each new namespace here
api.add_namespace(ns1, path="/signup")
api.add_namespace(ns2, path="/login")
api.add_namespace(ns3, path="/logout")
api.add_namespace(ns4, path="/forgotuser")
api.add_namespace(ns5, path="/changedetails")
api.add_namespace(ns6, path="/user")
api.add_namespace(ns7, path="/search")
api.add_namespace(ns8, path="/watchlist")
api.add_namespace(ns9, path="/marketorder")
api.add_namespace(ns10, path="/portfolio")
api.add_namespace(ns11, path="/transaction")
api.add_namespace(ns12, path="/leaderboard")
api.add_namespace(ns13, path="/exportfolio")
