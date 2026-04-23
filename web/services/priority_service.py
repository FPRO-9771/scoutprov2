from flask import current_app

from web.models.match import Match
from web.services.cache_service import CacheService
from web.services.tba_service import TBAService

CACHE_TTL = 60
CACHE_PREFIX = 'priority:event_matches:'


class PriorityService:
    """Priority highlighting for scouts based on a team's future matches.

    A team is "priority" if our team will play with or against them in a match that
    has not yet been completed (per TBA). Also identifies our next upcoming match.
    """

    @staticmethod
    def get_priority_teams(event, team_number):
        """Map of {team_number: 'A'|'O'} for teams we'll meet in future matches.

        'A' = alliance partner in at least one future match (takes precedence).
        'O' = opponent only.
        """
        if not event or not team_number:
            return {}
        completed = PriorityService.get_completed_match_keys(event)
        roles = {}
        for m in PriorityService._our_matches(event, team_number):
            if m.tba_match_key and m.tba_match_key in completed:
                continue
            red = m.red_teams or []
            blue = m.blue_teams or []
            partners = red if team_number in red else blue
            opponents = blue if team_number in red else red
            for t in partners:
                if t != team_number:
                    roles[t] = 'A'
            for t in opponents:
                if roles.get(t) != 'A':
                    roles[t] = 'O'
        return roles

    @staticmethod
    def get_next_match(event, team_number):
        """Next uncompleted match for the given team, with predicted start time.

        Returns {'match': Match, 'predicted_time': int|None} or None.
        """
        if not event or not team_number:
            return None
        return PriorityService._first_uncompleted(
            event, PriorityService._our_matches(event, team_number),
        )

    @staticmethod
    def get_next_scouting_match(event, team_number):
        """Next uncompleted match (not ours) that contains at least one priority team.

        Useful for prompting scouts to catch matches where future partners/opponents
        are on the field. Returns {match, predicted_time, priority_count} or None.
        """
        if not event or not team_number:
            return None
        priority = set(PriorityService.get_priority_teams(event, team_number).keys())
        if not priority:
            return None

        matches = (
            Match.query
            .filter_by(event_id=event.id)
            .order_by(Match.number)
            .all()
        )
        candidates = [
            m for m in matches
            if team_number not in (m.red_teams or [])
            and team_number not in (m.blue_teams or [])
            and any(t in priority for t in (m.red_teams or []) + (m.blue_teams or []))
        ]
        result = PriorityService._first_uncompleted(event, candidates)
        if result:
            match = result['match']
            result['priority_count'] = sum(
                1 for t in (match.red_teams or []) + (match.blue_teams or [])
                if t in priority
            )
        return result

    @staticmethod
    def get_completed_match_keys(event):
        """Set of TBA match keys the event has already finished playing."""
        if current_app.config.get('DEV_PRETEND_UNPLAYED'):
            return set()
        return {
            m.get('key') for m in PriorityService._tba_matches(event)
            if m.get('actual_time') or m.get('winning_alliance')
        } - {None}

    @staticmethod
    def _first_uncompleted(event, matches):
        """Return the first uncompleted match from the list, with predicted_time, or None."""
        completed = PriorityService.get_completed_match_keys(event)
        tba_by_key = {m.get('key'): m for m in PriorityService._tba_matches(event)}
        for m in matches:
            if m.tba_match_key and m.tba_match_key in completed:
                continue
            tba = tba_by_key.get(m.tba_match_key) or {}
            return {
                'match': m,
                'predicted_time': tba.get('predicted_time') or tba.get('time'),
            }
        return None

    @staticmethod
    def _our_matches(event, team_number):
        matches = (
            Match.query
            .filter_by(event_id=event.id)
            .order_by(Match.number)
            .all()
        )
        return [
            m for m in matches
            if team_number in (m.red_teams or []) or team_number in (m.blue_teams or [])
        ]

    @staticmethod
    def _tba_matches(event):
        """Cached TBA event-matches payload. Empty list if TBA unavailable."""
        if not event or not event.tba_event_key:
            return []
        cache_key = f'{CACHE_PREFIX}{event.tba_event_key}'
        cached = CacheService.get(cache_key)
        if cached is not None:
            return cached
        data = TBAService.get_event_matches(event.tba_event_key) or []
        CacheService.set(cache_key, data, ttl=CACHE_TTL)
        return data
