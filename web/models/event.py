from web.extensions import db

# Association table for many-to-many Event <-> Team
event_teams = db.Table(
    'event_teams',
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('teams.id'), primary_key=True),
)


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    date = db.Column(db.Date, nullable=True)
    tba_event_key = db.Column(db.String(50), unique=True, nullable=True)

    teams = db.relationship('Team', secondary=event_teams, backref='events', lazy=True)
    matches = db.relationship('Match', backref='event', lazy=True)

    def __repr__(self):
        return f'<Event {self.name}>'
