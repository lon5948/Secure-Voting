from unicodedata import category
from flask_bcrypt import Bcrypt
from flask import Flask,flash, render_template,request, redirect, url_for,jsonify,session
import cv2
import mysql.connector
import Face

app = Flask(__name__)
app.config['SECRET_KEY'] = b'zjvmolck1226341vl/vblcbvc'
bcrypt = Bcrypt(app)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="securevoting"
)
cursor = db.cursor(buffered=True)

@app.route('/')
def landing():
    uid = session.get('id', None)
    if uid is not None:
        session.pop('id')
    return render_template('login.html')

@app.route("/login",methods=["POST"])
def login():
    id = request.form.get('id')
    name = request.form.get('name')
    password = request.form.get('password')
    cursor.execute("select * from admin where id = %s and name = %s ", (id,name,))
    admin = cursor.fetchone()
    if admin is not None and bcrypt.check_password_hash(admin[2], password)==True:
        session['id'] = admin[0]
        return redirect(url_for('admin'))
    cursor.execute("select * from voter where id = %s and name = %s ", (id,name,))
    data = cursor.fetchone()
    if data is None:
        error = 'Not Registered!'
    elif name != data[1]:
        error = 'Incorrect Name!'
    elif bcrypt.check_password_hash(data[2], password)==False:
        error = 'Incorrect Password!'
    else:
        face = Face.VerifyUser(id)
        if face!="Correct":
            error = face
        else:
            session['id'] = data[0]
            session['name'] = data[1]
            return redirect('voter')
    flash(error,category='danger')
    return redirect('/')
        
@app.route('/changePW',methods=['GET','POST'])
def changePW():
    if request.method == 'GET':
        id = session.get('id')
        if id is None:
            return redirect('/')
        return render_template('changePW.html')
    if request.method == 'POST':
        id = session.get('id')
        password = request.form.get('password')
        REpassword = request.form.get('re-password')
        if password==REpassword:
            cursor.execute("update voter set password = %s where id = %s", (bcrypt.generate_password_hash(password),id,))
            db.commit()
            flash("Successfully Change PassWord",category='success')
            return redirect(url_for('voter'))
        else:
            flash("Re-type password doesn't match",category='danger')
            return(redirect(url_for('changePW')))

@app.route("/admin",methods=["GET"])
def admin():
    id = session.get('id')
    if id is None:
        return redirect('/')
    return render_template("admin.html")

@app.route('/voter',methods=["GET"])
def voter():
    id = session.get('id')
    if id is None:
        return redirect('/')
    name = session.get('name')
    return render_template('voter.html',name=name)

@app.route('/vote',methods=["GET"])
def vote():
    id = session.get('id')
    if id is None:
        return redirect('/')
    cursor.execute("select done from voter where id=%s",(id,))
    done = cursor.fetchone()[0]
    if done == 0:
        return render_template('vote.html')
    else:
        flash("Already Casted!",category='danger')
        return redirect(url_for('voter'))

@app.route('/addVoter',methods=['GET','POST'])
def addVoter(name=None):
    if request.method == 'GET':
        id = session.get('id')
        if id is None:
            return redirect('/')
        return render_template('addVoter.html')
    if request.method == 'POST':
        id = request.form.get('Id')
        name = request.form.get('Name')
        error = ""
        try:
            int(id[1:10])
            if len(id)!=10 or not id[0].isalpha():
                error="id format error"
        except:
            error="id format error"
        cursor.execute("select * from voter where id=%s",(id,))
        existid = cursor.fetchone()
        if existid is not None:
            error = "Voter already exists"
        else:
            error = Face.addUserFace(id)
        if error == 'Correct':
            password = id[6:10]
            cursor.execute("""insert into voter (id,name,password,done) values (%s,%s,%s,%s)""",(id,name,bcrypt.generate_password_hash(password),0),)
            db.commit()
            flash("Voter has been Added in the Database!",category='success')
            return redirect(url_for('admin'))
        else:
            flash(error,category='danger')
            return redirect(url_for('addVoter'))
        
@app.route("/CastVote/<party>")
def addVote(party):
    id = session.get('id')
    if id is None:
        return redirect('/')
    cursor.execute("update voter set done=1 where id=%s",(id,))
    cursor.execute("insert into result (party) values (%s)",(party,))
    db.commit()
    flash("Successfully Casted!",category='success')
    return redirect(url_for('voter'))

@app.route("/results")
def results():
    id = session.get('id')
    if id is None:
        return redirect('/')
    result = {"A":0,"B":0,"C":0,"D":0}
    cursor.execute("select * from result")
    votes = cursor.fetchall()
    if len(votes)==0:
        flash("All voters have not casted their votes yet",category='danger')
        return redirect(url_for('admin'))
    for v in votes:
        result[v[0]] += 1
    return render_template("results.html",result=result)

@app.route("/clear")
def clear():
    id = session.get('id')
    if id is None:
        return redirect('/')
    cursor.execute("truncate result")
    flash("Result Cleared!",category='success')
    return redirect('admin')

@app.route("/reset")
def reset():
    id = session.get('id')
    if id is None:
        return redirect('/')
    cursor.execute("truncate voter")
    Face.DeleteFaces()
    flash("Database Reset!",category='success')
    return redirect('admin')

if __name__ == '__main__':
    app.run(debug = True)