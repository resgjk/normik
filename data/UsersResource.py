from flask import abort, jsonify
from flask_restful import Resource, reqparse
from data import db_session
from data.users import User

parser = reqparse.RequestParser()
parser.add_argument("surname")
parser.add_argument("name")
parser.add_argument("email")
parser.add_argument("photo")
parser.add_argument("hashed_password")

login_parser = reqparse.RequestParser()
login_parser.add_argument("email")
login_parser.add_argument("password")


def abort_if_users_not_found(users_id):
    session = db_session.create_session()
    users = session.query(User).get(users_id)
    if not users:
        abort(404, message=f"Users {users_id} not found")


class UserGetWithEmail(Resource):
    def get(self, email):
        session = db_session.create_session()
        user = session.query(User).filter(User.email == email).first()
        if user:
            return jsonify({"message": "user with this email exists"})
        return jsonify({"message": "user with this email can be created"})


class UserLoginResource(Resource):
    def post(self):
        args = login_parser.parse_args()
        session = db_session.create_session()
        user = session.query(User).filter(User.email == args["email"]).first()
        if user and user.check_password(args["password"]):
            return jsonify(user.to_dict(
                only=(
                    "id", "surname", "name", "email",
                    "photo", "hashed_password")))
        return jsonify({"message": "bad request"})


class UserResource(Resource):
    def get(self, user_id):
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify(user.to_dict(
            only=(
                "id", "surname", "name", "email",
                "photo", "hashed_password")))

    def delete(self, user_id):
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify([item.to_dict(
            only=("id", "surname", "name", "email",
                  "photo", "hashed_password")) for item in users])

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            surname=args["surname"],
            name=args["name"],
            email=args["email"],
            photo=args["photo"],
        )
        user.set_password(args["hashed_password"])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
