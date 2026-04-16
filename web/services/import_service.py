import logging
from datetime import datetime

from web.extensions import db
from web.models.event import Event, event_teams
from web.models.match import Match
from web.models.team import Team
from web.services.tba_service import TBAService

logger = logging.getLogger(__name__)


class ImportService:

    @staticmethod
    def import_event(tba_event_key, game_id):
        """Create or update an Event from TBA data. Returns the Event."""
        tba_data = TBAService.get_event(tba_event_key)
        if not tba_data:
            logger.warning(f'No TBA data for event {tba_event_key}')
            return None

        event = Event.query.filter_by(tba_event_key=tba_event_key).first()
        if not event:
            event = Event(tba_event_key=tba_event_key, game_id=game_id)
            db.session.add(event)

        event.name = tba_data.get('name', tba_event_key)
        event.location = f"{tba_data.get('city', '')}, {tba_data.get('state_prov', '')}"

        start_date = tba_data.get('start_date')
        if start_date:
            event.date = datetime.strptime(start_date, '%Y-%m-%d').date()

        db.session.commit()
        logger.info(f'Imported event: {event.name}')
        return event

    @staticmethod
    def import_team_events(team_key, year, game_id):
        """Create Event rows for all events a team is attending in a year.

        Skips any event whose tba_event_key is already in the DB so existing
        events are never overwritten. Returns (created, skipped) lists of names.
        """
        tba_events = TBAService.get_team_events(team_key, year)
        if not tba_events:
            return [], []

        created, skipped = [], []
        for tba_event in tba_events:
            event_key = tba_event.get('key')
            if not event_key:
                continue

            if Event.query.filter_by(tba_event_key=event_key).first():
                skipped.append(tba_event.get('name', event_key))
                continue

            date = None
            start_date = tba_event.get('start_date')
            if start_date:
                try:
                    date = datetime.strptime(start_date, '%Y-%m-%d').date()
                except ValueError:
                    pass

            city = tba_event.get('city') or ''
            state = tba_event.get('state_prov') or ''
            location = ', '.join(p for p in [city, state] if p) or None

            event = Event(
                tba_event_key=event_key,
                game_id=game_id,
                name=tba_event.get('name', event_key),
                location=location,
                date=date,
            )
            db.session.add(event)
            created.append(event.name)

        db.session.commit()
        logger.info(f'Imported {len(created)} new events for {team_key} {year} (skipped {len(skipped)})')
        return created, skipped

    @staticmethod
    def import_event_teams(event_id):
        """Fetch teams for an event from TBA, upsert into DB, link to event."""
        event = db.session.get(Event, event_id)
        if not event or not event.tba_event_key:
            return 0

        tba_teams = TBAService.get_event_teams(event.tba_event_key)
        if not tba_teams:
            return 0

        count = 0
        for tba_team in tba_teams:
            team_number = tba_team.get('team_number')
            if not team_number:
                continue

            team = Team.query.filter_by(number=team_number).first()
            if not team:
                team = Team(
                    number=team_number,
                    name=tba_team.get('nickname', ''),
                    tba_key=tba_team.get('key', f'frc{team_number}'),
                )
                db.session.add(team)

            if team not in event.teams:
                event.teams.append(team)
                count += 1

        db.session.commit()
        logger.info(f'Imported {count} teams for {event.name}')
        return count

    @staticmethod
    def import_event_matches(event_id):
        """Fetch matches from TBA, upsert into DB."""
        event = db.session.get(Event, event_id)
        if not event or not event.tba_event_key:
            return 0

        tba_matches = TBAService.get_event_matches(event.tba_event_key)
        if not tba_matches:
            return 0

        count = 0
        for tba_match in tba_matches:
            parsed = TBAService.parse_match(tba_match)

            # Only import qualification matches for now
            if parsed['comp_level'] != 'qm':
                continue

            match = Match.query.filter_by(
                event_id=event.id, number=parsed['number']
            ).first()

            if not match:
                match = Match(event_id=event.id, number=parsed['number'])
                db.session.add(match)

            match.red_teams = parsed['red_teams']
            match.blue_teams = parsed['blue_teams']
            match.tba_match_key = parsed['tba_match_key']
            count += 1

        db.session.commit()
        logger.info(f'Imported {count} matches for {event.name}')
        return count
