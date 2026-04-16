from web import create_app
from web.extensions import db
from web.models.game import Game
from web.models.team import Team

GAMES = ['Reefscape', 'Rebuilt']


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


def seed_games():
    """Seed FRC games if they don't already exist."""
    for name in GAMES:
        if not Game.query.filter_by(name=name).first():
            db.session.add(Game(name=name, score_config=[]))
            print(f'Seeded game {name}')
        else:
            print(f'Game {name} already exists')
    db.session.commit()


def seed_all():
    seed_team_9771()
    seed_games()


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_all()
