import os

import requests
from flask import Flask, make_response, jsonify, redirect, render_template, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
from werkzeug.utils import secure_filename

from data import db_session, UsersResource, ReviewsResource, ProductsResource
from data.users import User
from forms.products import AddNewProductForm
from forms.reviews import AddNewReviewForm
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


@app.route("/add_new_product", methods=['GET', 'POST'])
def add_new_product():
    form = AddNewProductForm()
    if form.validate_on_submit():
        print(form.name.data)
        print(form.category.data)
        prodcut = requests.get(
            f"http://127.0.0.1:5000/api/product/{form.name.data}/{form.category.data}").json()
        if "message" in prodcut:
            f = form.photo.data
            if form.category.data == "Игры":
                direct = "game"
            elif form.category.data == "Литература":
                direct = "literature"
            elif form.category.data == "Фильмы":
                direct = "movies"
            elif form.category.data == "Сериалы":
                direct = "series"
            elif form.category.data == "Музыка":
                direct = "music"
            elif form.category.data == "Разное":
                direct = "other"
            elif form.category.data == "Техника":
                direct = "technique"
            elif form.category.data == "Софт":
                direct = "soft"
            way = os.path.join("static", "photos", "reviews", direct, f"{form.name.data}.jpeg")
            f.save(way)
            requests.post("http://127.0.0.1:5000/api/products", json={
                "name": form.name.data,
                "category": form.category.data,
                "photo": way
            })
            return redirect("/add_new_review")
        return render_template('add_new_product.html', title='Добавление продукта', form=form,
                               message="Продукт с таким названием и категорией уже существует.")
    #else:
    #    if request.method == "POST":
    #        return redirect(f"/product/{request.form['search']}")
    return render_template('add_new_product.html', title='Добавление продукта', form=form)


@app.route("/add_new_review", methods=['GET', 'POST'])
def add_new_review():
    form = AddNewReviewForm()
    if form.validate_on_submit():
        prodcut = requests.get(
            f"http://127.0.0.1:5000/api/product/{form.product_name.data}/{form.category.data}").json()
        if "message" not in prodcut:
            requests.post("http://127.0.0.1:5000/api/reviews", json={
                "product_name": form.product_name.data,
                "plus": form.plus.data,
                "rating": form.rating.data,
                "minus": form.minus.data,
                "description": form.description.data,
                "user_id": current_user.id
            })
            return redirect(f"/product/{form.product_name.data}")
        return render_template('add_new_review.html', title='Добавление отзыва', form=form,
                               message="Продукта с таким названием и категорией нет.")
    if request.method == "POST":
        return redirect(f"/product/{request.form['search']}")
    return render_template('add_new_review.html', title='Добавление отзыва', form=form)


@app.route("/user/<int:id>", methods=['GET', 'POST'])
def reviews_by_user_id(id):
    if request.method == "POST":
        return redirect(f"/product/{request.form['search']}")
    reviews = requests.get(f"http://127.0.0.1:5000/api/user/id/{id}").json()[::-1]
    user = requests.get(f"http://127.0.0.1:5000/api/user/{id}").json()
    return render_template("reviews_by_user_id.html", lst=reviews, user_name=f"{user['name']} {user['surname']}",
                           sess=db_session.create_session(),
                           user_model=User, title=f"{user['name']} {user['surname']}")


@app.route("/product/<product_name>", methods=['GET', 'POST'])
def reviews_by_product_name(product_name):
    if request.method == "POST":
        return redirect(f"/product/{request.form['search']}")
    reviews = requests.get(f"http://127.0.0.1:5000/api/product/{product_name}").json()[::-1]
    return render_template("reviews_by_product_name.html", lst=reviews, product=product_name,
                           sess=db_session.create_session(),
                           user_model=User, title=product_name)


@app.route("/category/<category>", methods=['GET', 'POST'])
def reviews_by_category(category):
    if request.method == "POST":
        return redirect(f"/product/{request.form['search']}")
    reviews = requests.get(f"http://127.0.0.1:5000/api/category/{category}").json()[::-1]
    return render_template("reviews_by_category.html", lst=reviews, category=category,
                           sess=db_session.create_session(),
                           user_model=User, title=category)


@app.route("/", methods=['GET', 'POST'])
def main_page():
    if request.method == "POST":
        return redirect(f"/product/{request.form['search']}")
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
    api.add_resource(ReviewsResource.ReviewsWithCategory, "/api/category/<category>")
    api.add_resource(ReviewsResource.ReviewsWithProductName, "/api/product/<product_name>")
    api.add_resource(ReviewsResource.ReviewsWithUserId, "/api/user/id/<int:id>")
    api.add_resource(ProductsResource.ProductWithNameAndCategory, "/api/product/<name>/<category>")
    app.run()


if __name__ == "__main__":
    main()
