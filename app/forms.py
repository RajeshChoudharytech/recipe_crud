from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FieldList, FormField
from wtforms.validators import DataRequired

class IngredientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    quantity = StringField('Quantity')

class RecipeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    instructions = TextAreaField('Instructions', validators=[DataRequired()])
    ingredients = FieldList(FormField(IngredientForm), min_entries=1)
