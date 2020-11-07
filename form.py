from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

arr = list(range(1, 26))


class ProductForm(FlaskForm):
    product = StringField('Product', validators=[DataRequired(), Length(min=3, max=60)])
    max_returned = SelectField('Max Returned Items', choices=[(el, el) for el in arr], default=10)
    submit = SubmitField('Search')
