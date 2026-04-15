from web.models.robot import Robot
from web.services.analytics_service import AnalyticsService
from web.services.cache_service import CacheService
from web.services.tba_service import TBAService


class TeamSummaryService:
    """Gathers all data needed to render a team summary card."""

    @staticmethod
    def build(team, event):
        summary = {
            'averages': None,
            'robot': None,
            'rank': None,
            'past_events': [],
            'videos': [],
        }

        if not event:
            return summary

        summary['averages'] = AnalyticsService.get_team_match_summary(team.id, event.id)

        robot = Robot.query.filter_by(team_id=team.id, game_id=event.game_id).first()
        if robot and robot.scouting_data:
            summary['robot'] = robot.scouting_data

        if event.tba_event_key:
            rankings = TeamSummaryService._cached_rankings(event.tba_event_key)
            summary['rank'] = rankings.get(team.number)

            if team.tba_key:
                summary['past_events'] = TeamSummaryService._cached_past_events(
                    team.tba_key, event.tba_event_key
                )
                summary['videos'] = TeamSummaryService._cached_videos(
                    team.tba_key, event.tba_event_key
                )

        return summary

    @staticmethod
    def _cached_rankings(event_key):
        cache_key = f'rankings:{event_key}'
        cached = CacheService.get(cache_key)
        if cached is not None:
            return cached

        data = TBAService.get_event_rankings(event_key)
        rankings = {}
        if data and 'rankings' in data:
            for r in data['rankings']:
                team_num = int(r['team_key'].replace('frc', ''))
                rankings[team_num] = r['rank']

        CacheService.set(cache_key, rankings)
        return rankings

    @staticmethod
    def _cached_past_events(team_key, current_event_key):
        cache_key = f'past_events:{team_key}'
        cached = CacheService.get(cache_key)
        if cached is not None:
            return cached

        try:
            year = int(current_event_key[:4]) if current_event_key else None
        except (ValueError, TypeError):
            year = None

        past = []
        if year:
            events = TBAService.get_team_events(team_key, year)
            if events:
                for evt in events:
                    if evt.get('key') == current_event_key:
                        continue
                    status = TBAService.get_team_event_status(team_key, evt['key'])
                    rank = None
                    if status and status.get('qual') and status['qual'].get('ranking'):
                        rank = status['qual']['ranking'].get('rank')
                    past.append({
                        'name': evt.get('short_name') or evt.get('name', 'Unknown'),
                        'rank': rank or '?',
                    })

        CacheService.set(cache_key, past)
        return past

    @staticmethod
    def _cached_videos(team_key, current_event_key):
        cache_key = f'videos:{team_key}:{current_event_key}'
        cached = CacheService.get(cache_key)
        if cached is not None:
            return cached

        try:
            year = int(current_event_key[:4]) if current_event_key else None
        except (ValueError, TypeError):
            year = None

        videos = []
        if year:
            events = TBAService.get_team_events(team_key, year) or []
            events_sorted = sorted(
                events,
                key=lambda e: e.get('start_date') or '',
                reverse=True,
            )
            for evt in events_sorted:
                event_key = evt.get('key')
                if not event_key:
                    continue
                event_name = evt.get('short_name') or evt.get('name', 'Event')
                videos.extend(
                    TeamSummaryService._event_videos(team_key, event_key, event_name)
                )

        CacheService.set(cache_key, videos)
        return videos

    @staticmethod
    def _event_videos(team_key, event_key, event_name, limit=3):
        matches = TBAService.get_team_event_matches(team_key, event_key) or []
        sorted_matches = sorted(
            matches,
            key=lambda m: (
                m.get('actual_time') or m.get('time') or 0,
                TeamSummaryService._comp_level_order(m.get('comp_level')),
                m.get('match_number') or 0,
            ),
            reverse=True,
        )
        results = []
        for m in sorted_matches:
            video_key = next(
                (v.get('key') for v in (m.get('videos') or [])
                 if v.get('type') == 'youtube' and v.get('key')),
                None,
            )
            if not video_key:
                continue
            results.append({
                'label': f'{event_name} — {TeamSummaryService._match_label(m)}',
                'url': f'https://www.youtube.com/watch?v={video_key}',
            })
            if len(results) >= limit:
                break
        return results

    @staticmethod
    def _comp_level_order(comp_level):
        return {'qm': 0, 'ef': 1, 'qf': 2, 'sf': 3, 'f': 4}.get(
            (comp_level or '').lower(), 0
        )

    @staticmethod
    def _match_label(m):
        comp = (m.get('comp_level') or '').lower()
        num = m.get('match_number') or 0
        set_num = m.get('set_number') or 0
        if comp == 'qm':
            return f'Qual {num}'
        prefix = {'ef': 'EF', 'qf': 'QF', 'sf': 'SF', 'f': 'F'}.get(
            comp, comp.upper()
        )
        if set_num and num > 1:
            return f'{prefix} {set_num}-{num}'
        return f'{prefix} {set_num or num}'
