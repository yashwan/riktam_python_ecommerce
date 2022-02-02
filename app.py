
from flask import Flask, redirect, render_template, request
import requests
import json
import pyrebase

#from app import app
from flask_sqlalchemy import SQLAlchemy
import os

config = {
    "apiKey": "AIzaSyARpFvvyemKckP8jGDdNskWtFd4ou9Iq3k",
  "authDomain": "whatsapp-mern-b8487.firebaseapp.com",
  "databaseURL": "https://whatsapp-mern-b8487-default-rtdb.firebaseio.com",
  "projectId": "whatsapp-mern-b8487",
  "storageBucket": "whatsapp-mern-b8487.appspot.com",
  "messagingSenderId": "821717612470",
  "appId": "1:821717612470:web:9ab05e1d2750220aeb7317"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

project_dir=os.path.dirname(os.path.abspath(__file__))
database_file="sqlite:///{}".format(
    os.path.join(project_dir,"mydatabase.db")
)

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]=database_file
db=SQLAlchemy(app)

class EmailPassword(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50),nullable=False)
    password=db.Column(db.String(50),nullable=False)


class CCart(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    filmid=db.Column(db.Integer,nullable=False)
    uid=db.Column(db.String(300),nullable=False)
    posterpath=db.Column(db.String(300),nullable=False)
    filmname=db.Column(db.String(300),nullable=False)
    cost=db.Column(db.Integer,nullable=False)

class Buy(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    filmid=db.Column(db.Integer,nullable=False)
    uid=db.Column(db.String(300),nullable=False)
    posterpath=db.Column(db.String(300),nullable=False)
    filmname=db.Column(db.String(300),nullable=False)
    cost=db.Column(db.Integer,nullable=False)

@app.route('/')
@app.route('/signin', methods=['GET', 'POST'])
def index():
    if (request.method == 'POST'):
            email = request.form['name']
            password = request.form['password']
            try:
                auth.sign_in_with_email_and_password(email, password)
                user = auth.sign_in_with_email_and_password(email,password)
                print(user['localId'])
                
                return redirect("/Home/"+user['localId'])
            except:
                unsuccessful = 'Please check your credentials'
                return render_template('signin.html', umessage=unsuccessful)
    return render_template('signin.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if (request.method == 'POST'):
            email = request.form['name']
            password = request.form['password']
            auth.create_user_with_email_and_password(email, password)
            emailpassword=EmailPassword(email=email,password=password)
            db.session.add(emailpassword)
            db.session.commit()
            return render_template('signin.html')
    return render_template('create.html')
@app.route("/Home/<id>")
def Home(id):
    req=requests.get("https://api.themoviedb.org/3/trending/all/day?api_key=360a9b5e0dea438bac3f653b0e73af47&language=en-US")
    data=json.loads(req.content)
    
    return render_template('index.html',datas=data['results'],id=id)

@app.route('/view/<id>/<uid>', methods=["GET"])
def View(id,uid):
    req=requests.get("https://api.themoviedb.org/3/movie/{}?api_key=360a9b5e0dea438bac3f653b0e73af47&language=en-US".format(id))
    data=json.loads(req.content)
    recreq=requests.get("https://api.themoviedb.org/3/movie/{}/recommendations?api_key=360a9b5e0dea438bac3f653b0e73af47&language=en-US&page=1".format(id))
    rec=json.loads(recreq.content)
   
    return render_template('view.html',data=data,recs=rec['results'],id=uid)

@app.route('/addtocart/<uid>/<id>/<posterpath>/<filmname>/<cost>', methods=["GET"])
def Addcart(uid,id,posterpath,filmname,cost):
    
    cart=CCart(filmid=id,uid=uid,posterpath=posterpath,filmname=filmname,cost=cost)
    db.session.add(cart)
    db.session.commit()
    
    
    return redirect('/cart/'+uid)

@app.route('/cart/<uid>')
def cart(uid):
    cart=CCart.query.filter_by(uid=uid).all()
    
    return render_template('cart.html',cart=cart,id=uid)

@app.route('/buy/<uid>/<cid>/<id>/<posterpath>/<filmname>/<cost>', methods=["GET"])
def buy(cid,uid,id,posterpath,filmname,cost):
    
    buy=Buy(filmid=id,uid=uid,posterpath=posterpath,filmname=filmname,cost=cost)
    db.session.add(buy)
    db.session.commit()
    cart=CCart.query.filter_by(id=cid).first()
    db.session.delete(cart)
    db.session.commit()
    return redirect('/buy/'+uid)

@app.route('/buy/<uid>')
def buyitem(uid):
    buy=Buy.query.filter_by(uid=uid).all()
    
    return render_template('buy.html',buy=buy,id=uid)
@app.route('/del/<id>/<uid>')
def delete(id,uid):
    buy=Buy.query.filter_by(id=id).first()
    db.session.delete(buy)
    db.session.commit()
    return redirect('/buy/'+uid)
@app.route('/delete/<id>/<uid>')
def delete_cart(id,uid):
    buy=CCart.query.filter_by(id=id).first()
    db.session.delete(buy)
    db.session.commit()
    return redirect('/cart/'+uid)
@app.route("/about")
def About():
    return render_template('about.html')
@app.route("/Contact")
def Contact():
    return render_template('contact.html')
if __name__=="__main__":
    app.run(debug=True)