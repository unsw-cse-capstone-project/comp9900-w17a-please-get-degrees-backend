from flask_restx import Resource, Namespace, fields

from simvestr.helpers.user import get_user_details
from simvestr.models import User
from simvestr.helpers.auth import get_user, requires_auth
from simvestr.models.api_models import user_details_model, user_model

api = Namespace('view user details', description='Demo api for querying users')
api.models[user_model.name] = user_model
api.models[user_details_model.name] = user_details_model
#TODO: Fix user details swagger model

@api.route('/all')
class UsersQuery(Resource):
    @requires_auth
    def get(self):
        user = User.query.all()
        data = {u.id: dict
                (
                 email=u.email_id,
                 role=u.role,
                 fname=u.first_name,
                 lname=u.last_name,
                 validated=u.validated,
                ) for u in user}
        payload = dict(
            data=data
        )
        return payload


@api.route('/details')
class UserQuery(Resource):
    @api.response(200, "Success")
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
    @requires_auth
    def get(self, ):
        user = get_user()
        return (
                {"first_name": user.first_name,
                 "last_name": user.last_name,
                 "email_id": user.email_id,
                 "message": "Authenticated with cookie set in browser"},
                200,
            )
