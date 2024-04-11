from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from app import app, db
from app.models import Recipe, User, Ingredient
from app.forms import RecipeForm

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Error handling
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    recipes = Recipe.query.paginate(page=page, per_page=per_page)
    return render_template('index.html', recipes=recipes)

@app.route('/recipe/<int:recipe_id>/delete', methods=['GET'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.created_by != current_user.id:
        flash('You are not authorized to delete this recipe.', 'danger')
        return redirect(url_for('index'))
    db.session.delete(recipe)
    db.session.commit()
    flash('Recipe deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/recipe/<int:recipe_id>')
@login_required
def recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe.html', recipe=recipe)

@app.route('/recipe/<int:recipe_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.created_by != current_user.id:
        flash('You are not authorized to edit this recipe.', 'danger')
        return redirect(url_for('index'))
    form = RecipeForm(obj=recipe)
    if form.validate_on_submit():
        form.populate_obj(recipe)
        db.session.commit()
        flash('Recipe updated successfully!', 'success')
        return redirect(url_for('recipe', recipe_id=recipe.id))
    return render_template('edit_recipe.html', form=form, recipe=recipe)

@app.route('/recipe/create', methods=['GET', 'POST'])
@login_required
def create_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        instructions = form.instructions.data
        
        # Create recipe
        new_recipe = Recipe(title=title, description=description, instructions=instructions, created_by=current_user.id)
        db.session.add(new_recipe)
        db.session.commit()
        
        # Add ingredients to the recipe
        for ingredient_data in form.ingredients.entries:
            name = ingredient_data.data['name']
            quantity = ingredient_data.data['quantity']
            if name:
                ingredient = Ingredient(name=name, quantity=quantity, recipe=new_recipe)
                db.session.add(ingredient)
        
        db.session.commit()
        flash('Recipe created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('create_recipe.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve username and password from the form
        username = request.form.get('username')
        password = request.form.get('password')

        # Query the database for the user
        user = User.query.filter_by(username=username).first()

        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password, password):
            login_user(user)  # Log in the user
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))  # Redirect to the homepage
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()  # Log out the current user
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))  # Redirect to the homepage

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if username is already taken
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username is already taken. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('register'))

        # Create a new user
        new_user = User(username=username, password=generate_password_hash(password))

        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

