from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired


class AddNewReviewForm(FlaskForm):
    product_name = StringField('Название', validators=[DataRequired()])
    category = SelectField("Категория", choices=[
        ("Игры", "Игры"),
        ("Литература", "Литература"),
        ("Фильмы", "Фильмы"),
        ("Музыка", "Музыка"),
        ("Сериалы", "Сериалы"),
        ("Софт", "Софт"),
        ("Техника", "Техника"),
        ("Разное", "Разное")])
    rating = SelectField("Оценка", choices=[
        ("1/10", "1/10"),
        ("2/10", "2/10"),
        ("3/10", "3/10"),
        ("4/10", "4/10"),
        ("5/10", "5/10"),
        ("6/10", "6/10"),
        ("7/10", "7/10"),
        ("8/10", "8/10"),
        ("9/10", "9/10"),
        ("10/10", "10/10")])
    plus = TextAreaField("Достоинства", validators=[DataRequired()])
    minus = TextAreaField("Недостатки", validators=[DataRequired()])
    description = TextAreaField("Комментарий", validators=[DataRequired()])
    submit = SubmitField("Добавить")
