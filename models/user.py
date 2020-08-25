from app import db


class User(db.Model):
    """table with users"""
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    token = db.Column(db.String(120), unique=True)

    def __init__(self, login, password, token):
        self.login = login
        self.password = password
        self.token = token

    def __repr__(self):
        return '<User %r>' % self.login

    def __str__(self):
        return self.login
