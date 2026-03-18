from web.extensions import db


class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    red_teams = db.Column(db.JSON, nullable=False, default=list)
    blue_teams = db.Column(db.JSON, nullable=False, default=list)
    tba_match_key = db.Column(db.String(50), unique=True, nullable=True)

    outcomes = db.relationship('Outcome', backref='match', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('event_id', 'number', name='uq_match_event_number'),
    )

    def __repr__(self):
        return f'<Match {self.number} event={self.event_id}>'
