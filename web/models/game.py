from web.extensions import db


class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo = db.Column(db.String(255), nullable=True)
    score_config = db.Column(db.JSON, nullable=False, default=list)

    events = db.relationship('Event', backref='game', lazy=True)
    robots = db.relationship('Robot', backref='game', lazy=True)

    def __repr__(self):
        return f'<Game {self.name}>'
