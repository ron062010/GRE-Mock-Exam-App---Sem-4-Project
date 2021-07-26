from flask import Flask, render_template, request
import random, copy
from flask import Flask, render_template, request, redirect, url_for, session
import re
import pickle
from flask_mysqldb import MySQL
import MySQLdb.cursors
import time
import matplotlib.pyplot as plt
import io
import base64
from datetime import date
from datetime import datetime
from matplotlib.ticker import MaxNLocator

from sqlalchemy.sql.functions import now

app = Flask(__name__)

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'gre_app'

mysql = MySQL(app)
app.secret_key = 'key12'
# VERBAL
with app.app_context():
    Cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    Cursor.execute('SELECT * FROM verbal1')
    result = Cursor.fetchall()

result = list(result)
list21 = []
for i in range(len(result)):
    x = result[i]
    list1a = []
    for key in x.values():
        print(key)
        print("djgs")
        list1a.append(key)
    list21.append(list1a)
# print(list2)
dict1 = {}
for i in range(len(result)):
    x = list21[i][1]

    dict1[x] = [list21[i][2], list21[i][3], list21[i][4], list21[i][5], list21[i][6]]
original_questions1 = dict1
questions1 = copy.deepcopy(original_questions1)

# QUANT
with app.app_context():
    Cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    Cursor.execute('SELECT * FROM quant1')
    result = Cursor.fetchall()

result = list(result)
list22 = []
for i in range(len(result)):
    x = result[i]
    list1b = []
    for key in x.values():
        list1b.append(key)
    list22.append(list1b)
# print(list2)
dict2 = {}
for i in range(len(result)):
    x = list22[i][1]
    print(x)
    dict2[x] = [list22[i][2], list22[i][3], list22[i][4], list22[i][5], list22[i][6]]
original_questions2 = dict2
print(original_questions2)
questions2 = copy.deepcopy(original_questions2)


def shuffle(q):
    selected_keys = []
    i = 0
    while i < len(q):
        current_selection = random.choice(list(q.keys()))
        if current_selection not in selected_keys:
            selected_keys.append(current_selection)
            i = i + 1
    return selected_keys


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("register.html")


@app.route('/section2', methods=['GET', 'POST'])
def quiz():
    questions_shuffled = shuffle(questions1)
    for i in questions1.keys():
        random.shuffle(questions1[i])
    # now = datetime.now()
    # Start_time = now.strftime("%H:%M:%S")
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # cursor.execute('INSERT INTO scores VALUES(%s)', [Start_time])
    # mysql.connection.commit()
    return render_template('section2.html', q=questions_shuffled, o=questions1)


@app.route('/result', methods=['GET', 'POST'])
def quiz_answers():
    correct = 0
    correct1 = 0
    correct2 = 0
    # print(Start_time)
    test_type = "verbal"
    test_no = ''
    Date = date.today()
    # now = datetime.now()
    # End_time = now.strftime("%H:%M:%S")

    for i in questions1.keys():
        answered = request.form.get(i, False)
        if original_questions1[i][0] == answered:
            correct1 = correct1 + 1

    # for i in questions2.keys():
    #     answered = request.form.get(i, False)
    #     if original_questions2[i][0] == answered:
    #         correct2 = correct2 + 1
    #         # test_no += 1
    score = correct1
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO scores VALUES(%s,%s,%s,%s)', [test_no, test_type, Date, score])
    mysql.connection.commit()
    return render_template('result.html', correct=correct1)


@app.route("/login", methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM userdetails WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template("login.html", msg=msg)


@app.route("/register", methods=['GET', 'POST'])
def register():
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM userdetails WHERE username = %s AND password=%s', [username, password])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO userdetails VALUES(%s,%s,%s)', [username, password, email])
            mysql.connection.commit()
            msg = 'Successfully registered! Please Sign-In'
            return render_template('login.html', msg=msg)
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template("register.html", msg=msg)


@app.route("/home", methods=['GET', 'POST'])
def home():
    return render_template("home.html", username=session['username'])


@app.route("/take-a-test", methods=['GET', 'POST'])
def takeatest():
    return render_template('take-a-test.html', username=session['username'])


@app.route("/section3", methods=['GET', 'POST'])
def section3():
    Cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    Cursor.execute('SELECT * FROM analytical')
    question3 = Cursor.fetchall()

    question3 = list(question3)
    list31 = []
    for i in range(len(question3)):
        x = question3[i]
        list32 = []
        for key in x.values():
            list32.append(key)
        list31.append(list32)
    return render_template('section3.html', username=session['username'], list31=list31)


@app.route("/test-history", methods=['GET', 'POST'])
def testhistory():
    Cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    Cursor.execute('SELECT * FROM scores')
    history = Cursor.fetchall()
    history = list(history)
    print(history)
    list_H = []

    for i in range(len(history)):
        x = history[i]
        list_h = []
        for key in x.values():
            list_h.append(key)
        list_H.append(list_h)
        print(list_H)
    return render_template('test-history.html', username=session['username'], list_H=list_H)


@app.route("/forgot-password", methods=['GET', 'POST'])
def forgotpassword():
    return render_template('forgot-password.html', username=session['username'])


@app.route("/about-us", methods=['GET', 'POST'])
def aboutus():
    return render_template('about-us.html', username=session['username'])


@app.route("/instruction-section1", methods=['GET', 'POST'])
def instruction_section1():
    return render_template('instruction-section1.html', username=session['username'])


@app.route("/instruction-section2", methods=['GET', 'POST'])
def instruction_section2():
    return render_template('instruction-section2.html', username=session['username'])


@app.route("/instruction-section3", methods=['GET', 'POST'])
def instruction_section3():
    return render_template('instruction-section3.html', username=session['username'])


@app.route("/instruction-section4", methods=['GET', 'POST'])
def instruction_section4():
    return render_template('instruction-section4.html', username=session['username'])


# @app.route("/result", methods=['GET', 'POST'])
# def result():
#     return render_template('result.html', username=session['username'])


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# @app.route("/score", methods=['GET', 'POST'])
# def score():
#     return render_template('score.html', username=session['username'])


@app.route('/analysis')
def analysis():
    img = io.BytesIO()

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM scores')

    score1 = cursor.fetchall()

    score1 = list(score1)
    list4 = []
    for i in range(len(score1)):
        x = score1[i]
        list3 = []
        for key in x.values():
            list3.append(key)
        list4.append(list3)
    x = [list4[i][0] for i in range(len(list4))]
    # x = [j for j in range(len(list4))]
    y = [list4[i][3] for i in range(len(list4))]
    # ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xlabel('TEST NUMBER')
    plt.ylabel('SCORE')

    print(x)
    print(y)

    fig = plt.plot(x, y)
    # fig.xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.savefig(img, format='png')
    img.seek(0)

    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('analysis.html', plot_url=plot_url)


if __name__ == '__main__':
    app.run(debug=True)
