import os
from flask import render_template, redirect, flash, request,session, url_for
from application import app
from application.utils import *
import pandas as pd
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
 
app.secret_key = 'your secret key'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '219011@np'
app.config['MYSQL_DB'] = 'trackerlogin'
 
mysql = MySQL(app)

@app.route('/', methods=['GET'])
def disp():
    return render_template('display.html')

@app.route('/calculator', methods=['GET', 'POST'])
def home():
    if not session.get('logged_in'):
        return redirect('/login')
    if request.method == "POST":
        if not 'file' in request.files:
            flash('No file part in request')
            return redirect(request.url)

        files = request.files.getlist('file')
        for file in files:
            if file.filename == '':
                flash('No file uploaded')
                return redirect(request.url)
            if file_valid(file.filename):
                filename = "overriden.jpg"
                file.save(os.path.join(app.config['UPLOADS_FOLDER'], filename))
            else:
                flash('Invalid file type')
                return redirect(request.url)
        # flash('We have recived your submission . And will contact you after few Days.')
        result = predictor()
        result[0] = fruit_dict[str(result[0])]
        return render_template('predict.html', prediction_text=result)

    else:
        return render_template('home.html')

@app.route('/detection', methods=['GET', 'POST'])
def detection():
    if not session.get('logged_in'):
        return redirect('/login')
    if request.method == "POST":
        list_names = attendance()
        length = len(list_names[0])
        flash('Attendance Recorded')
        return render_template('detection_result.html',list_names=list_names,length=length)
    return render_template('detection.html')

@app.route('/monitoring', methods=['GET', 'POST'])
def monitoring():
    if not session.get('logged_in'):
        return redirect('/login')
    df = pd.read_csv('Student_sih.csv')
    print(list(df['Name']))
    return render_template('monitoring.html',labels=list(df['Name']),values=list(df.BMI))

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('home.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)
 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('disp'))
 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)