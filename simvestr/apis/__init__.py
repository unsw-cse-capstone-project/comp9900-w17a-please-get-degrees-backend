from flask_restx import Api

#Import the api variable from each of the namespaces (api files) and alias them
from .namespace1 import api as ns1
from .user import api as ns2
from .signup import api as ns3
from .token import api as ns4

from flask import Blueprint

blueprint = Blueprint('api', __name__, url_prefix='/api/')

api = Api(blueprint,
    title='SimvestrAPI',
    version='0.01',
    description='Simvestr api',
    # All API metadatas
)

#Register each new namespace here
api.add_namespace(ns1,  path='/hello/')
api.add_namespace(ns2,  path='/user/')
api.add_namespace(ns3,  path='/signup/')
api.add_namespace(ns4,  path='/token/')
