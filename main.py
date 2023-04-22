import os

import requests
from flask import Flask, make_response, jsonify, redirect, render_template, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
from werkzeug.utils import secure_filename

from data import db_session, UsersResource, ReviewsResource, ProductsResource
from data.products import Product
from data.reviews import Review
from data.users import User
from forms.users import LoginForm, RegisterForm

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config["SECRET_KEY"] = "normik_very_secret_key"


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def main_page():
    lst_rev = requests.get("http://127.0.0.1:5000/api/reviews").json()[::-1]
    return render_template("index.html", title="Недавние отзывы", lst=lst_rev, sess=db_session.create_session(),
                           user_model=User)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        res = requests.post("http://127.0.0.1:5000/api/login", json={
            "email": form.email.data,
            "password": form.password.data
        }).json()
        try:
            db_sess = db_session.create_session()
            user = db_sess.query(User).get(res["id"])
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        except Exception:
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form, title="Авторизация")
    return render_template("login.html", form=form, title="Авторизация")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if requests.get(f"http://127.0.0.1:5000/api/email/{form.email.data}").json()[
            "message"] == "user with this email exists":
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        f = form.photo.data
        filename = secure_filename(f.filename)
        way = os.path.join("static", "photos", "users", f"{form.email.data}.jpeg")
        f.save(way)
        requests.post("http://127.0.0.1:5000/api/users", json={
            "surname": form.surname.data,
            "name": form.name.data,
            "email": form.email.data,
            "photo": way,
            "hashed_password": form.password.data
        })
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


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
    api.add_resource(UsersResource.UserLoginResource, "/api/login")
    api.add_resource(UsersResource.UserGetWithEmail, "/api/email/<email>")
    app.run()


if __name__ == "__main__":
    main()
