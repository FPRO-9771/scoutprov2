from datetime import datetime, UTC

from web.extensions import db


class Outcome(db.Model):
    __tablename__ = 'outcomes'

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scouting_data = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))

    __table_args__ = (
        db.UniqueConstraint('match_id', 'team_id', 'user_id', name='uq_outcome_match_team_user'),
    )

    def __repr__(self):
        return f'<Outcome match={self.match_id} team={self.team_id}>'
