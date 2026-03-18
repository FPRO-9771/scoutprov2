import logging

import requests
from flask import current_app

logger = logging.getLogger(__name__)


class TBAService:
    BASE_URL = 'https://www.thebluealliance.com/api/v3'

    @staticmethod
    def get_event(event_key):
        """Fetch event details from TBA."""
        return TBAService._request(f'/event/{event_key}')

    @staticmethod
    def get_event_teams(event_key):
        """List of teams at an event."""
        return TBAService._request(f'/event/{event_key}/teams')

    @staticmethod
    def get_event_matches(event_key):
        """Match schedule for an event."""
        return TBAService._request(f'/event/{event_key}/matches')

    @staticmethod
    def get_event_rankings(event_key):
        """Team rankings at an event."""
        return TBAService._request(f'/event/{event_key}/rankings')

    @staticmethod
    def get_team_events(team_key, year):
        """Events a team has attended in a given year."""
        return TBAService._request(f'/team/{team_key}/events/{year}')

    @staticmethod
    def get_team_event_status(team_key, event_key):
        """Team's rank/record at a specific event."""
        return TBAService._request(f'/team/{team_key}/event/{event_key}/status')

    @staticmethod
    def _request(endpoint):
        """Shared GET with auth header and error handling."""
        api_key = current_app.config.get('TBA_API_KEY')
        if not api_key:
            logger.warning('TBA_API_KEY not set — skipping TBA request')
            return None

        url = f'{TBAService.BASE_URL}{endpoint}'
        try:
            resp = requests.get(url, headers={'X-TBA-Auth-Key': api_key}, timeout=10)
            if resp.status_code == 304:
                return None
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.warning(f'TBA request failed: {endpoint} — {e}')
            return None

    @staticmethod
    def parse_match(tba_match):
        """Extract match number and team lists from a TBA match object."""
        alliances = tba_match.get('alliances', {})
        red_keys = alliances.get('red', {}).get('team_keys', [])
        blue_keys = alliances.get('blue', {}).get('team_keys', [])

        # Convert "frc9771" → 9771
        red_teams = [int(k.replace('frc', '')) for k in red_keys]
        blue_teams = [int(k.replace('frc', '')) for k in blue_keys]

        return {
            'number': tba_match.get('match_number'),
            'comp_level': tba_match.get('comp_level'),
            'set_number': tba_match.get('set_number'),
            'tba_match_key': tba_match.get('key'),
            'red_teams': red_teams,
            'blue_teams': blue_teams,
        }
