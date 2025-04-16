from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import time
import threading
from utils.model_utils import generate_decision_tree, get_feature_importance

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy credentials
USERNAME = 'admin'
PASSWORD = 'password'

# Load data for dashboard
data = pd.read_csv("data/KQuestoStudentDataKID.csv")
data_buffer = []
index_pointer = [0]

# Simulate real-time data
def data_stream():
    while index_pointer[0] < len(data):
        data_buffer.append(data.iloc[index_pointer[0]])
        index_pointer[0] += 1
        time.sleep(0.3 if index_pointer[0] < 10 else 1)

threading.Thread(target=data_stream, daemon=True).start()

# ---------- ROUTES ----------

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        entered_username = request.form['username']
        entered_password = request.form['password']

        if entered_username == USERNAME and entered_password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('navigation'))
        else:
            error = 'Invalid username or password'

    return render_template('login.html', error=error)

@app.route('/navigation')
def navigation():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('navigation.html')

@app.route('/project_info')
def project_info():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('project_info.html')

@app.route('/project_outputs')
def project_outputs():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('project_outputs.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------- DASHBOARD API ----------

@app.route("/api/data")
def get_data():
    return jsonify([row.to_dict() for row in data_buffer])

@app.route("/api/tree")
def tree():
    return jsonify(generate_decision_tree(pd.DataFrame(data_buffer)))

@app.route("/api/feature_importance")
def feature_importance():
    return jsonify(get_feature_importance(pd.DataFrame(data_buffer)))

# -----------------------

if __name__ == '__main__':
    app.run(debug=True)