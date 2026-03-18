from web.extensions import db


class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=True)
    tba_key = db.Column(db.String(20), unique=True, nullable=True)

    robots = db.relationship('Robot', backref='team', lazy=True)
    users = db.relationship('User', backref='team', lazy=True)

    def __repr__(self):
        return f'<Team {self.number} {self.name}>'
