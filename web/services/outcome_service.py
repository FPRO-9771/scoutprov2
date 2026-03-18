from sqlalchemy import func

from web.extensions import db
from web.models.outcome import Outcome
from web.models.match import Match


class OutcomeService:

    @staticmethod
    def save_outcome(match_id, team_id, user_id, scouting_data):
        outcome = Outcome.query.filter_by(
            match_id=match_id, team_id=team_id, user_id=user_id
        ).first()
        if outcome:
            outcome.scouting_data = scouting_data
        else:
            outcome = Outcome(
                match_id=match_id,
                team_id=team_id,
                user_id=user_id,
                scouting_data=scouting_data,
            )
            db.session.add(outcome)
        db.session.commit()
        return outcome

    @staticmethod
    def get_outcome(match_id, team_id, user_id):
        return Outcome.query.filter_by(
            match_id=match_id, team_id=team_id, user_id=user_id
        ).first()

    @staticmethod
    def get_match_scout_counts(match_id):
        rows = (
            db.session.query(Outcome.team_id, func.count(Outcome.id))
            .filter(Outcome.match_id == match_id)
            .group_by(Outcome.team_id)
            .all()
        )
        return {team_id: count for team_id, count in rows}

    @staticmethod
    def get_event_match_scout_status(event_id):
        matches = Match.query.filter_by(event_id=event_id).order_by(Match.number).all()
        result = {}
        for match in matches:
            total_teams = len(match.red_teams or []) + len(match.blue_teams or [])
            scouted_teams = (
                db.session.query(func.count(func.distinct(Outcome.team_id)))
                .filter(Outcome.match_id == match.id)
                .scalar()
            )
            if scouted_teams == 0:
                result[match.id] = 'none'
            elif scouted_teams >= total_teams:
                result[match.id] = 'all'
            else:
                result[match.id] = 'partial'
        return result
