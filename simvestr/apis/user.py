from flask_restx import Resource, Namespace, fields

from simvestr.helpers.user import get_user_details, get_info
from simvestr.models import User
from simvestr.helpers.auth import get_user, requires_auth
from simvestr.models.api_models import user_details_model, user_model, user_info_model

api = Namespace('view user details', description='Demo api for querying users')
api.models[user_model.name] = user_model
api.models[user_info_model.name] = user_info_model
api.models[user_details_model.name] = user_details_model


@api.route('/details')
class UserQuery(Resource):
    @api.response(200, "Success")
    @api.response(401, "Unauthorised")
    @requires_auth
    @api.doc(
        model=user_details_model,
        description="User details endpoint"
    )
    @api.marshal_with(user_details_model)
    def get(self, ):
        user = get_user()
        data = get_user_details(user)
        return data, 200


@api.route('/info')
class UserInfoQuery(Resource):
    @api.response(200, "Success")
    @api.response(401, "Unauthorised")
    @api.doc(
        description="Basic user details",
        model=user_info_model
    )
    @api.marshal_with(user_info_model)
    @requires_auth
    def get(self, ):
        user = get_user()
        info = get_info(user)
        return info, 200
