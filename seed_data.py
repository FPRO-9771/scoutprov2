from web import create_app
from web.extensions import db
from web.models.team import Team


def seed_team_9771():
    """Seed team 9771 FPRO if it doesn't already exist."""
    team = Team.query.filter_by(number=9771).first()
    if not team:
        team = Team(number=9771, name='FPRO', tba_key='frc9771')
        db.session.add(team)
        db.session.commit()
        print('Seeded team 9771 FPRO')
    else:
        print('Team 9771 already exists')


def seed_all():
    seed_team_9771()


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_all()
