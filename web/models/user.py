from web.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)

    outcomes = db.relationship('Outcome', backref='user', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('team_id', 'username', name='uq_user_team_username'),
    )

    def __repr__(self):
        return f'<User {self.username}>'
