from web.extensions import db
from web.models.team import Team
from web.models.user import User


class UserService:

    @staticmethod
    def get(user_id):
        return db.session.get(User, user_id)

    @staticmethod
    def get_all():
        """Get all users for team 9771 (v1: single team)."""
        team = Team.query.filter_by(number=9771).first()
        if not team:
            return []
        return User.query.filter_by(team_id=team.id).order_by(User.username).all()

    @staticmethod
    def create(username):
        """Create a new user for team 9771. Returns None if username taken."""
        team = Team.query.filter_by(number=9771).first()
        if not team:
            return None

        existing = User.query.filter_by(team_id=team.id, username=username).first()
        if existing:
            return None

        user = User(team_id=team.id, username=username)
        db.session.add(user)
        db.session.commit()
        return user
