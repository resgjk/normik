from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired


class AddNewProductForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    category = SelectField("Категория", choices=[
        ("Игры", "Игры"),
        ("Литература", "Литература"),
        ("Фильмы", "Фильмы"),
        ("Музыка", "Музыка"),
        ("Сериалы", "Сериалы"),
        ("Софт", "Софт"),
        ("Техника", "Техника"),
        ("Разное", "Разное")])
    photo = FileField("Фотография", validators=[FileRequired()])
    submit = SubmitField("Добавить продукт")
