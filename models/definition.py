from app import db


class Definition(db.Model):
    """table with definition"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    definition = db.Column(db.String())
    link = db.Column(db.String())

    def __init__(self, title, definition, link):
        self.title = title
        self.definition = definition
        self.link = link

    def __repr__(self):
        return '<Definition %r>' % self.title

    def __str__(self):
        return self.title