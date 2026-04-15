import statistics

from sqlalchemy import func

from web.extensions import db
from web.models.outcome import Outcome
from web.models.match import Match
from web.models.robot import Robot
from web.models.event import Event
from web.models.team import Team


class AnalyticsService:

    FIELDS = ['auton_balls', 'auton_climb', 'teleop_balls', 'teleop_defense', 'teleop_climb']
    CONFIDENCE_FIELDS = ['auton_balls', 'teleop_balls', 'teleop_defense']

    @staticmethod
    def _active_values(outcomes, field):
        return [
            v for o in outcomes
            if (v := o.scouting_data.get(field)) is not None and v > 0
        ]

    @staticmethod
    def _field_confidence(values, team_total_matches):
        n = len(values)
        if n == 0 or team_total_matches == 0:
            return None
        frequency = min(n / team_total_matches, 1.0)
        if n < 2:
            consistency = 0.3
        else:
            mean = sum(values) / n
            sd = statistics.stdev(values)
            if mean > 0:
                cv = sd / mean
                consistency = max(0.0, 1.0 - min(cv, 1.0))
            else:
                consistency = 1.0 if sd == 0 else 0.0
        return round(0.6 * frequency + 0.4 * consistency, 3)

    @staticmethod
    def get_team_match_averages(team_id, event_id):
        outcomes = (
            Outcome.query
            .join(Match, Outcome.match_id == Match.id)
            .filter(Match.event_id == event_id, Outcome.team_id == team_id)
            .all()
        )
        if not outcomes:
            return None

        averages = {}
        for f in AnalyticsService.FIELDS:
            values = AnalyticsService._active_values(outcomes, f)
            averages[f] = round(sum(values) / len(values), 1) if values else None

        return averages

    @staticmethod
    def get_team_match_summary(team_id, event_id):
        outcomes = (
            Outcome.query
            .join(Match, Outcome.match_id == Match.id)
            .filter(Match.event_id == event_id, Outcome.team_id == team_id)
            .all()
        )
        if not outcomes:
            return None

        result = {'count': len(outcomes)}
        for f in AnalyticsService.FIELDS:
            values = AnalyticsService._active_values(outcomes, f)
            if values:
                result[f] = {
                    'avg': round(sum(values) / len(values), 1),
                    'min': min(values),
                    'max': max(values),
                }
            else:
                result[f] = None

        defense_plays = AnalyticsService._active_values(outcomes, 'teleop_defense')
        result['defense_frequency'] = round(len(defense_plays) / len(outcomes) * 100) if outcomes else 0
        result['defense_strength'] = round(sum(defense_plays) / len(defense_plays), 1) if defense_plays else None
        result['defense_plays'] = len(defense_plays)

        return result

    @staticmethod
    def get_team_outcomes(team_id, event_id):
        return (
            Outcome.query
            .join(Match, Outcome.match_id == Match.id)
            .filter(Match.event_id == event_id, Outcome.team_id == team_id)
            .order_by(Match.number)
            .all()
        )

    @staticmethod
    def get_unscouted_robots(event_id, game_id):
        event = db.session.get(Event, event_id)
        if not event:
            return []
        scouted_ids = {r.team_id for r in Robot.query.filter_by(game_id=game_id).all()}
        return [t for t in sorted(event.teams, key=lambda t: t.number) if t.id not in scouted_ids]

    @staticmethod
    def get_unscouted_matches(event_id):
        matches = Match.query.filter_by(event_id=event_id).order_by(Match.number).all()
        result = []
        for match in matches:
            all_team_numbers = (match.red_teams or []) + (match.blue_teams or [])
            total = len(all_team_numbers)
            # Get team IDs for the numbers in this match
            teams = Team.query.filter(Team.number.in_(all_team_numbers)).all()
            team_map = {t.number: t for t in teams}
            scouted_team_ids = {
                o.team_id for o in
                Outcome.query.filter(Outcome.match_id == match.id).all()
            }
            unscouted = [team_map[n] for n in all_team_numbers if n in team_map and team_map[n].id not in scouted_team_ids]
            scouted_count = total - len(unscouted)
            if unscouted:
                result.append({
                    'match': match,
                    'scouted': scouted_count,
                    'total': total,
                    'unscouted_teams': unscouted,
                })
        return result

    @staticmethod
    def get_all_team_averages(event_id):
        event = db.session.get(Event, event_id)
        if not event:
            return []

        all_matches = Match.query.filter_by(event_id=event_id).all()
        team_total_matches = {}
        for m in all_matches:
            for n in (m.red_teams or []) + (m.blue_teams or []):
                team_total_matches[n] = team_total_matches.get(n, 0) + 1

        results = []
        for team in sorted(event.teams, key=lambda t: t.number):
            outcomes = (
                Outcome.query
                .join(Match, Outcome.match_id == Match.id)
                .filter(Match.event_id == event_id, Outcome.team_id == team.id)
                .all()
            )

            averages = {}
            confidence = {}
            total = team_total_matches.get(team.number, 0)
            for f in AnalyticsService.FIELDS:
                values = AnalyticsService._active_values(outcomes, f)
                if values:
                    averages[f] = round(sum(values) / len(values), 1)
                if f in AnalyticsService.CONFIDENCE_FIELDS:
                    confidence[f] = AnalyticsService._field_confidence(values, total)

            results.append({
                'team': team,
                'averages': averages,
                'confidence': confidence,
                'match_count': len(outcomes),
                'total_matches': total,
            })
        return results
