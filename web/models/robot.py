from web.extensions import db


class Robot(db.Model):
    __tablename__ = 'robots'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    scouting_data = db.Column(db.JSON, nullable=False, default=dict)

    __table_args__ = (
        db.UniqueConstraint('team_id', 'game_id', name='uq_robot_team_game'),
    )

    def __repr__(self):
        return f'<Robot team={self.team_id} game={self.game_id}>'
