import os
import sys
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from app.models import User, Recipe, Ingredient

from flask_testing import TestCase
from flask_login import current_user
from werkzeug.security import generate_password_hash

class TestCreateRecipeRoute(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        db.create_all()

        # Create a test user
        self.user = User(username='test_user', password=generate_password_hash('test_password'))
        db.session.add(self.user)
        db.session.commit()

        # Log in the test user
        with self.client:
            self.client.post('/login', data=dict(
                username='test_user',
                password='test_password'
            ))

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_create_recipe_form(self):
        response = self.client.get('/recipe/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create Recipe', response.data)
        self.assertIn(b'Name', response.data)
        self.assertIn(b'Quantity', response.data)

    def test_create_recipe_with_valid_data(self):
        # Simulate form submission with valid data
        response = self.client.post('/recipe/create', data=dict(
            title='Test Recipe',
            description='Test Description',
            instructions='Test Instructions',
            ingredients=[{'name': 'Ingredient 1', 'quantity': '1 unit'}]
        ))
        self.assertEqual(response.status_code, 200)  
        recipe = Recipe.query.filter_by(title='Test Recipe').first()
        self.assertIsNotNone(recipe)
        self.assertEqual(recipe.author, current_user)

        ingredients = Ingredient.query.filter_by(recipe_id=recipe.id).all()
        self.assertEqual(len(ingredients), 1)
        self.assertEqual(ingredients[0].name, 'Ingredient 1')
        self.assertEqual(ingredients[0].quantity, '1 unit')

    def test_create_recipe_with_invalid_data(self):
        # Simulate form submission with missing title
        response = self.client.post('/recipe/create', data=dict(
            description='Test Description',
            instructions='Test Instructions',
            ingredients=[{'name': 'Ingredient 1', 'quantity': '1 unit'}]
        ))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Recipe created successfully!', response.data)

        # Check that no recipe is added to the database
        recipe = Recipe.query.filter_by(title='Test Recipe').first()
        self.assertIsNone(recipe)

        # Simulate form submission with invalid ingredient
        response = self.client.post('/recipe/create', data=dict(
            title='Test Recipe',
            description='Test Description',
            instructions='Test Instructions',
            ingredients=[{'name': '', 'quantity': '1 unit'}]
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'This field is required.', response.data)
        self.assertNotIn(b'Recipe created successfully!', response.data)
        self.assertIsNone(recipe)

if __name__ == '__main__':
    unittest.main()
