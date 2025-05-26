from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy             # To make changes in database through python we use --> flask-sqlalchemy module
from datetime import datetime, timezone

app = Flask(__name__)

#Setting up the DataBase
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///expenseTracker.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False            # To suppress a deprecation warning
db = SQLAlchemy(app)                                            # Initialize SQLAlchemy

class Expense(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False,  default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self) -> str:
        return f"{self.sno} - {self.category}"                     # Show this in return --> in print(allData) in the terminal only


@app.route("/")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/profile", methods=['GET', 'POST'])
def profile():
    #handling method requests
    if request.method == 'POST':
        amount1 = request.form['amount']
        category1 = request.form['category']
        desc1 = request.form['description']
        entry = Expense(amount=amount1,category=category1, description=desc1)
        db.session.add(entry)
        db.session.commit()
    
    allData = Expense.query.all()
    return render_template("profile.html", allData=allData) 
   

@app.route("/delete/<int:sno>")
def delete(sno):
    del_todo = Expense.query.filter_by(sno=sno).first()
    db.session.delete(del_todo)
    db.session.commit()
    return redirect("/profile")

@app.route("/update/<int:sno>", methods=['GET', 'POST'])
def update(sno):
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        desc = request.form['description']
        data = Expense.query.filter_by(sno=sno).first()
        data.amount = amount
        data.category = category
        data.description = desc
        db.session.add(data)
        db.session.commit()
        return redirect("/profile")
        
    data = Expense.query.filter_by(sno=sno).first()
    return render_template('update.html', allData=data)


        
@app.route("/dashboard")
def dashboard():
    all_expenses = Expense.query.all()
    total_expenses = sum([expense.amount for expense in all_expenses])
    
    categories = {}
    for expense in all_expenses:
        categories[expense.category] = categories.get(expense.category, 0) + expense.amount

    chart_labels = list(categories.keys())
    chart_data = list(categories.values())
    top_categories = ", ".join(sorted(categories, key=categories.get, reverse=True)[:])
    return render_template(
        "dashboard.html",
        total_expenses=total_expenses,
        top_categories=top_categories,
        chart_labels=chart_labels,
        chart_data=chart_data
    )


if __name__ == "__main__":
    app.run(debug=True, port=8080)

