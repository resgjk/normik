from flask import abort, jsonify
from flask_login import current_user
from flask_restful import Resource, reqparse
from data import db_session
from data.products import Product
from data.reviews import Review

parser = reqparse.RequestParser()
parser.add_argument("product_name")
parser.add_argument("photo", type=bytes)
parser.add_argument("plus")
parser.add_argument("minus")
parser.add_argument("description")


def abort_if_review_not_found(review_id):
    session = db_session.create_session()
    review = session.query(Review).get(review_id)
    if not review:
        abort(404, message=f"Review {review_id} not found")


class ReviewResource(Resource):
    def get(self, review_id):
        abort_if_review_not_found(review_id)
        session = db_session.create_session()
        review = session.query(Review).get(review_id)
        return jsonify(review.to_dict(
            only=(
                "id", "product_name", "photo", "date", "category",
                "plus", "minus", "description", "user_id")))

    def delete(self, review_id):
        abort_if_review_not_found(review_id)
        session = db_session.create_session()
        review = session.query(Review).get(review_id)
        session.delete(review)
        session.commit()
        return jsonify({'success': 'OK'})


class ReviewsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        reviews = session.query(Review).all()
        return jsonify([item.to_dict(
            only=("id", "product_name", "photo", "date", "category",
                "plus", "minus", "description", "user_id")) for item in reviews])

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        product = session.query(Product).filter(Product.name == args["product_name"]).first()
        if not product:
            return jsonify({"succes": "product not found"})
        review = Review(
            product_name=args["product_name"],
            photo=product.photo,
            plus=args["plus"],
            minus=args["minus"],
            description=args["description"],
            user_id=current_user.id,
            product_id=product.id,
            category=product.category
        )
        session.add(review)
        session.commit()
        return jsonify({'success': 'OK'})
