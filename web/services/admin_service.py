from web.extensions import db
from web.models.game import Game
from web.models.event import Event
from web.models.team import Team
from web.models.match import Match


class AdminService:

    @staticmethod
    def create_game(name, logo=None, score_config=None):
        game = Game(name=name, logo=logo, score_config=score_config or [])
        db.session.add(game)
        db.session.commit()
        return game

    @staticmethod
    def update_game(game_id, name=None, logo=None, score_config=None):
        game = db.session.get(Game, game_id)
        if not game:
            return None
        if name is not None:
            game.name = name
        if logo is not None:
            game.logo = logo
        if score_config is not None:
            game.score_config = score_config
        db.session.commit()
        return game

    @staticmethod
    def create_event(name, game_id, location=None, date=None, tba_event_key=None):
        event = Event(
            name=name, game_id=game_id, location=location,
            date=date, tba_event_key=tba_event_key,
        )
        db.session.add(event)
        db.session.commit()
        return event

    @staticmethod
    def update_event(event_id, **kwargs):
        event = db.session.get(Event, event_id)
        if not event:
            return None
        for key, value in kwargs.items():
            if hasattr(event, key) and value is not None:
                setattr(event, key, value)
        db.session.commit()
        return event

    @staticmethod
    def add_team(number, name=None):
        team = Team.query.filter_by(number=number).first()
        if team:
            return team
        team = Team(number=number, name=name, tba_key=f'frc{number}')
        db.session.add(team)
        db.session.commit()
        return team

    @staticmethod
    def link_team_to_event(team_number, event_id):
        team = Team.query.filter_by(number=team_number).first()
        event = db.session.get(Event, event_id)
        if not team or not event:
            return False
        if team not in event.teams:
            event.teams.append(team)
            db.session.commit()
        return True

    @staticmethod
    def unlink_team_from_event(team_number, event_id):
        team = Team.query.filter_by(number=team_number).first()
        event = db.session.get(Event, event_id)
        if not team or not event:
            return False
        if team in event.teams:
            event.teams.remove(team)
            db.session.commit()
        return True

    @staticmethod
    def create_match(event_id, number, red_teams, blue_teams):
        match = Match.query.filter_by(event_id=event_id, number=number).first()
        if match:
            match.red_teams = red_teams
            match.blue_teams = blue_teams
        else:
            match = Match(
                event_id=event_id, number=number,
                red_teams=red_teams, blue_teams=blue_teams,
            )
            db.session.add(match)
        db.session.commit()
        return match

    @staticmethod
    def update_match(match_id, red_teams=None, blue_teams=None):
        match = db.session.get(Match, match_id)
        if not match:
            return None
        if red_teams is not None:
            match.red_teams = red_teams
        if blue_teams is not None:
            match.blue_teams = blue_teams
        db.session.commit()
        return match
