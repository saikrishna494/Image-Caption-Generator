from flask import Flask, render_template, request, redirect, url_for, flash

import mysql.connector

app = Flask(__name__)

mysql_config ={
    'user':'root',
    'password':'root',
    'host':'localhost',
    'database':'sai'
    
}

db = mysql.connector.connect(**mysql_config)
cursor = db.cursor()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/Sign_in",methods=["GET","POST"])
def Sign_in():
    return render_template("Sign_in.html")

@app.route('/submit_form',methods=['POST'])
def submit_form():
    username = request.form['username']
    emial = request.form['emial']
    password = request.form['password']

    
    # Insert the form data into the database
    sql = "INSERT INTO users (username, emial, password) VALUES (%s, %s, %s)"
    values = (username, emial, password )
    cursor.execute(sql, values)
    db.commit()


    
    # Redirect the user to a success page
    return render_template('success.html')

@app.route("/login",methods=["GET","POST"])
def login():
    return render_template("login.html")


@app.route('/login_test',methods=['POST'])
def login_test():
    if request.method == "POST":
        emial = request.form["emial"]
        password = request.form["password"]

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="sai"
        )

        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE emial = %s AND password = %s"
        values = (emial, password)
        cursor.execute(query, values)
        user = cursor.fetchone()

        if user:
            return "login successful...."
        else:
            return "login failed"
        return render_template("login.html")        

if __name__=="__main__":
   app.run(debug=True)