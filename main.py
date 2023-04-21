from flask import Flask, make_response, jsonify
from flask_login import LoginManager
from flask_restful import Api

from data import db_session, UsersResource, ReviewsResource, ProductsResource
from data.users import User

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config["SECRET_KEY"] = "normik_very_secret_key"


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def main_page():
    pass


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def main():
    db_session.global_init("db/Normik.db")
    api.add_resource(UsersResource.UserResource, "/api/user/<int:user_id>")
    api.add_resource(UsersResource.UsersListResource, "/api/users")
    api.add_resource(ReviewsResource.ReviewResource, "/api/review/<int:review_id>")
    api.add_resource(ReviewsResource.ReviewsListResource, "/api/reviews")
    api.add_resource(ProductsResource.ProductResource, "/api/product/<int:product_id>")
    api.add_resource(ProductsResource.ProductsListResource, "/api/products")
    app.run()


if __name__ == "__main__":
    main()
