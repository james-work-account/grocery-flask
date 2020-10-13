from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ProductForm(FlaskForm):
    product = StringField('Product', validators=[DataRequired(), Length(min=3, max=60)])
    submit = SubmitField('Search')
