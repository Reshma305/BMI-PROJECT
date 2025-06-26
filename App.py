from flask import Flask, render_template, request, redirect, session, url_for
import os
import json

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

DATA_FILE = 'data.json'                             
'''
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}
'''
import json
import os

def load_data():
    file_path = "users_data.json"
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return {}
    with open(file_path, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

users_data = load_data()

def calculate_bmi(weight, height):
    return round(weight / (height ** 2), 2) if height > 0 else None

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        if username:
            session['user_id'] = username
            users_data.setdefault(username, {'weight': None, 'height': None, 'bmi': None})
            save_data(users_data)
            return redirect(url_for('user_form', user_id=username))
    return render_template('login.html')

@app.route('/user/<user_id>', methods=['GET', 'POST'])
def user_form(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login'))

    if request.method == 'POST':
        weight = float(request.form['weight'])
        height = float(request.form['height'])
        bmi = calculate_bmi(weight, height)

        users_data[user_id] = {'weight': weight, 'height': height, 'bmi': bmi}
        save_data(users_data)
        return redirect(url_for('dashboard'))

    return render_template("user_form.html", user_id=user_id)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    users_list = []
    for uid, data in users_data.items():
        users_list.append({
            'id': uid,
            'weight': data.get('weight') or '—',
            'height': data.get('height') or '—',
            'bmi': data.get('bmi') or '—'
        })

    return render_template('index.html', users=users_list)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)