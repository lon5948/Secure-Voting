from flask_bcrypt import Bcrypt
from flask import Flask,flash, render_template,request, redirect, url_for,jsonify,session
import cv2
import mysql.connector
import AddUser as db

app = Flask(__name__)
app.config['SECRET_KEY'] = b'zjvmolck1226341vl/vblcbvc'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="secure_voting"
)
cursor = db.cursor(buffered=True)


@app.route('/')
def landing():
    return render_template('login.html')

@app.route("/login",methods=["POST"])
def login():
    account = request.form.get('account')
    password = request.form.get('password')
    cursor.execute("select id,password from Voter where name = %s", (account))
    data = cursor.fetchone()
    id = data[0]
    if id is None:
        error = 'Account not registered !'
        return render_template("Error.html",erroe=error)
    elif bcrypt.check_password_hash(data[1], password)==False:
        error = 'Incorrect password !'
        return render_template("Error.html",erroe=error)
    elif id=="0000":
        return render_template("admin.html",name="Admin")
    else:
        session.clear()
        session['uid'] = data[0]
        return redirect("/vote/"+"/"+account)
        

@app.route("/admin")
def admin():
    return render_template("admin.html",name="Admin")
    
@app.route('/vote/<id>/<name>',methods=["GET"])
def vote(id,name):
    return render_template('vote.html',name=name,id=id)


@app.route('/addVoter',methods=['GET','POST'])
def addVoter(name=None):
    if request.method == 'GET':
        return render_template('addVoter.html')
    if request.method == 'POST':
        status = db.addVoter(request.form['Name'],request.form['Password'],request.form['Id'])
        if(status!="Done"):
            return "Voter already exists"
        if(request.form['Name'].lower=="admin"):
            return render_template("admin.html")
        else:
            return redirect('/admin')

@app.route("/CastVote/<party>/<id>")
def addVote(party,id):
    status = db.AddVote(id,party)
    return render_template("Error.html",status=status,link="/")

@app.route("/results")
def results():
    result = db.result() 
    print(result)
    if(result=="0"):
        return render_template("Error.html",status="All voters have not casted their votes yet",link="/admin")
    
    return render_template("results.html",d=result)

@app.route("/clear")
def clear():
    status = db.clearDb()
    return render_template("Error.html",status=status,link="/addVoter")

if __name__ == '__main__':
    app.run(debug = True)