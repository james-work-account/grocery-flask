from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class ProductForm(FlaskForm):
    product = StringField('Product', validators=[DataRequired()])
    submit = SubmitField('Search')
