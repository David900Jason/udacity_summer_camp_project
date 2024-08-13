from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your own secret key

# Database setup
def init_db():
    with sqlite3.connect('bmi_meals.db') as conn:
        cursor = conn.cursor()

        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')

        # Create meals table if not exists (reuse the previous code)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_name TEXT NOT NULL,
            calories INTEGER NOT NULL,
            protein REAL NOT NULL,
            carbohydrates REAL NOT NULL,
            fats REAL NOT NULL
        )
        ''')

        conn.commit()

# Calculate BMI function
def calculate_bmi(weight, height):
    return round(weight / (height / 100) ** 2, 2)

# Calculate nutritional information for a meal
def calculate_nutritional_info(meal_name, amount):
    conn = sqlite3.connect('bmi_meals.db')
    cursor = conn.cursor()

    cursor.execute('''
    SELECT calories, protein, carbohydrates, fats
    FROM meals
    WHERE meal_name = ?
    ''', (meal_name,))
    
    meal = cursor.fetchone()
    
    conn.close()

    if meal:
        calories, protein, carbohydrates, fats = meal
        calculated_nutrition = {
            'calories': calories * (amount / 100),
            'protein': protein * (amount / 100),
            'carbohydrates': carbohydrates * (amount / 100),
            'fats': fats * (amount / 100)
        }
        return calculated_nutrition
    else:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        with sqlite3.connect('bmi_meals.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                INSERT INTO users (username, password)
                VALUES (?, ?)
                ''', (username, hashed_password))
                conn.commit()
                flash('Signup successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Username already exists. Please choose another one.', 'danger')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('bmi_meals.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user[2], password):  # Assuming password is stored hashed
                session['user_id'] = user[0]
                session['username'] = user[1]
                flash('Login successful!', 'success')
                
                # Pass user data to the index template
                return redirect(url_for('index', username=user[1]))  # Redirect to index with username
            else:
                flash('Invalid username or password', 'danger')

    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))  # or redirect to a dedicated logout page





@app.route('/bmi', methods=['GET', 'POST'])
def bmi_calculator():
    if request.method == 'POST':
        weight = float(request.form['weight'])
        height = float(request.form['height'])
        bmi = calculate_bmi(weight, height)
        return render_template('result.html', result=f'Your BMI is {bmi}')
    return render_template('bmi_calculator.html')

@app.route('/calories', methods=['GET', 'POST'])
def calories_calculator():
    if request.method == 'POST':
        meal_name = request.form['meal_name']
        amount = float(request.form['amount'])
        nutritional_info = calculate_nutritional_info(meal_name, amount)

        if nutritional_info:
            return render_template('result.html', result=f"Nutritional info for {amount} grams of {meal_name}: "
                                                         f"Calories: {nutritional_info['calories']} kcal, "
                                                         f"Protein: {nutritional_info['protein']} g, "
                                                         f"Carbohydrates: {nutritional_info['carbohydrates']} g, "
                                                         f"Fats: {nutritional_info['fats']} g")
        else:
            return render_template('result.html', result=f"Meal '{meal_name}' not found in the database.")
    return render_template('calories_calculator.html')

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
