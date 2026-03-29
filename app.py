from flask import Flask, render_template, request, redirect, session, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

app = Flask(__name__)
app.secret_key = "secret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# USER MODEL
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

# EXPENSE MODEL
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    amount = db.Column(db.Float)
    category = db.Column(db.String(50))
    date = db.Column(db.String(20))
    user_id = db.Column(db.Integer)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            return redirect("/")
        flash("Invalid credentials")
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect("/register")

        db.session.add(User(username=username, password=password))
        db.session.commit()
        return redirect("/login")

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def index():
    if 'user_id' not in session:
        return redirect("/login")

    expenses = Expense.query.filter_by(user_id=session['user_id']).all()
    total = sum(e.amount for e in expenses)
    count = len(expenses)

    categories = {}
    for e in expenses:
        categories[e.category] = categories.get(e.category,0) + e.amount

    return render_template("dashboard.html",
                           expenses=expenses,
                           total=total,
                           count=count,
                           categories=categories)

@app.route("/add", methods=["GET","POST"])
def add():
    if request.method == "POST":
        expense = Expense(
            title=request.form['title'],
            amount=request.form['amount'],
            category=request.form['category'],
            date=request.form['date'],
            user_id=session['user_id']
        )
        db.session.add(expense)
        db.session.commit()
        return redirect("/")
    return render_template("add.html")

@app.route("/delete/<int:id>")
def delete(id):
    db.session.delete(Expense.query.get(id))
    db.session.commit()
    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):
    expense = Expense.query.get(id)
    if request.method == "POST":
        expense.title = request.form['title']
        expense.amount = request.form['amount']
        expense.category = request.form['category']
        expense.date = request.form['date']
        db.session.commit()
        return redirect("/")
    return render_template("edit.html", expense=expense)

@app.route("/export")
def export():
    expenses = Expense.query.filter_by(user_id=session['user_id']).all()

    df = pd.DataFrame([[e.title,e.amount,e.category,e.date] for e in expenses],
                      columns=["Title","Amount","Category","Date"])
    df.to_csv("expenses.csv", index=False)

    return send_file("expenses.csv", as_attachment=True)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)