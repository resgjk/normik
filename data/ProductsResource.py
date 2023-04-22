from io import BytesIO

from PIL import Image
from flask import abort, jsonify
from flask_restful import Resource, reqparse
from data import db_session
from data.products import Product

parser = reqparse.RequestParser()
parser.add_argument("name")
parser.add_argument("category")
parser.add_argument("photo")


def abort_if_product_not_found(product_id):
    session = db_session.create_session()
    product = session.query(Product).get(product_id)
    if not product:
        abort(404, message=f"Product {product_id} not found")


class ProductResource(Resource):
    def get(self, product_id):
        abort_if_product_not_found(product_id)
        session = db_session.create_session()
        product = session.query(Product).get(product_id)
        return jsonify(product.to_dict(
            only=("id", "name", "category", "photo")))

    def delete(self, product_id):
        abort_if_product_not_found(product_id)
        session = db_session.create_session()
        product = session.query(Product).get(product_id)
        session.delete(product)
        session.commit()
        return jsonify({'success': 'OK'})


class ProductsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        products = session.query(Product).all()
        return jsonify([item.to_dict(
            only=("id", "name", "category", "photo")) for item in products])

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        product = Product(
            name=args["name"],
            category=args["category"]
        )
        photo_bt = args["photo"]
        if product.category == "Игры":
            direct = "game"
        elif product.category == "Литература":
            direct = "literature"
        elif product.category == "Фильмы":
            direct = "movies"
        elif product.category == "Сериалы":
            direct = "series"
        elif product.category == "Музыка":
            direct = "music"
        elif product.category == "Разное":
            direct = "other"
        elif product.category == "Техника":
            direct = "technique"
        elif product.category == "Софт":
            direct = "soft"
        photo_dir = f"/static/photos/reviews/{direct}/{product.name}.jpeg"
        Image.open(BytesIO(photo_bt)).save(photo_dir)
        product.photo = photo_dir
        session.add(product)
        session.commit()
        return jsonify({'success': 'OK'})
