from unittest.mock import patch

import pytest

from web.extensions import db
from web.models import Event, Game, Match, Team
from web.services.cache_service import CacheService
from web.services.priority_service import PriorityService


OUR = 9771


@pytest.fixture
def ctx(app):
    with app.app_context():
        CacheService.clear()
        game = Game(name='Reefscape', score_config=[])
        db.session.add(game)
        db.session.commit()

        event = Event(game_id=game.id, name='Worlds', tba_event_key='2026worlds')
        db.session.add(event)
        db.session.commit()

        # M1: already played (our alliance = 1111/2222, opponents = 3333/4444)
        m1 = Match(event_id=event.id, number=1,
                   red_teams=[OUR, 1111, 2222], blue_teams=[3333, 4444, 5555],
                   tba_match_key='2026worlds_qm1')
        # M2: future (partners = 6666/7777, opponents = 8888/9999)
        m2 = Match(event_id=event.id, number=2,
                   red_teams=[OUR, 6666, 7777], blue_teams=[8888, 9999, 1010],
                   tba_match_key='2026worlds_qm2')
        # M3: future, team 3333 re-appears but as partner this time
        m3 = Match(event_id=event.id, number=3,
                   red_teams=[2020, 3030, 4040], blue_teams=[OUR, 3333, 5050],
                   tba_match_key='2026worlds_qm3')
        # Match we aren't in
        m4 = Match(event_id=event.id, number=4,
                   red_teams=[1, 2, 3], blue_teams=[4, 5, 6],
                   tba_match_key='2026worlds_qm4')
        db.session.add_all([m1, m2, m3, m4])
        db.session.commit()
        yield {'event': event, 'm1': m1, 'm2': m2, 'm3': m3}


def _tba(completed_keys=(), times=None):
    """Build a TBA event-matches payload. completed_keys mark actual_time set; times maps key→predicted_time."""
    times = times or {}
    keys = ['2026worlds_qm1', '2026worlds_qm2', '2026worlds_qm3', '2026worlds_qm4']
    return [
        {
            'key': k,
            'actual_time': 1000 if k in completed_keys else None,
            'winning_alliance': 'red' if k in completed_keys else '',
            'predicted_time': times.get(k),
        }
        for k in keys
    ]


def test_priority_teams_excludes_completed_match(ctx):
    with patch('web.services.priority_service.TBAService.get_event_matches',
               return_value=_tba(completed_keys=['2026worlds_qm1'])):
        roles = PriorityService.get_priority_teams(ctx['event'], OUR)

    # M1 is done, so 1111/2222/3333/4444/5555 are NOT priority via M1.
    # M2 partners: 6666, 7777; opponents: 8888, 9999, 1010.
    # M3 partners: 3333, 5050; opponents: 2020, 3030, 4040.
    assert roles[6666] == 'A'
    assert roles[7777] == 'A'
    assert roles[8888] == 'O'
    assert roles[1010] == 'O'
    assert roles[3333] == 'A'  # partner in future M3, even though they played against us in past M1
    assert roles[5050] == 'A'
    assert roles[2020] == 'O'
    assert OUR not in roles
    assert 1111 not in roles  # only seen in completed M1
    assert 4444 not in roles


def test_priority_teams_partner_beats_opponent_when_both(ctx):
    # Make M3 so 8888 (opponent in M2) is also a partner
    ctx['m3'].blue_teams = [OUR, 8888, 5050]
    db.session.commit()
    with patch('web.services.priority_service.TBAService.get_event_matches',
               return_value=_tba()):
        roles = PriorityService.get_priority_teams(ctx['event'], OUR)
    assert roles[8888] == 'A'


def test_priority_teams_empty_when_no_team_number(ctx):
    with patch('web.services.priority_service.TBAService.get_event_matches',
               return_value=_tba()):
        assert PriorityService.get_priority_teams(ctx['event'], None) == {}


def test_priority_teams_without_tba_treats_all_as_future(ctx):
    # No TBA event key → no completed info → every match of ours contributes
    ctx['event'].tba_event_key = None
    db.session.commit()
    roles = PriorityService.get_priority_teams(ctx['event'], OUR)
    # Now M1 partners (1111, 2222) and opponents (3333, 4444, 5555) are all in
    assert roles[1111] == 'A'
    assert roles[4444] == 'O'
    assert roles[3333] == 'A'  # partner in M3 overrides opponent in M1


def test_next_match_skips_completed(ctx):
    with patch('web.services.priority_service.TBAService.get_event_matches',
               return_value=_tba(
                   completed_keys=['2026worlds_qm1'],
                   times={'2026worlds_qm2': 1234567890},
               )):
        result = PriorityService.get_next_match(ctx['event'], OUR)
    assert result['match'].number == 2
    assert result['predicted_time'] == 1234567890


def test_next_match_none_when_all_done(ctx):
    done = ['2026worlds_qm1', '2026worlds_qm2', '2026worlds_qm3']
    with patch('web.services.priority_service.TBAService.get_event_matches',
               return_value=_tba(completed_keys=done)):
        assert PriorityService.get_next_match(ctx['event'], OUR) is None


def test_completed_keys_empty_when_tba_fails(ctx):
    with patch('web.services.priority_service.TBAService.get_event_matches', return_value=None):
        assert PriorityService.get_completed_match_keys(ctx['event']) == set()


def test_next_scouting_match_finds_priority_match_we_are_not_in(ctx):
    # Add a match we're not in, containing a priority team (8888 is an opponent in M2)
    m5 = Match(event_id=ctx['event'].id, number=5,
               red_teams=[8888, 111, 222], blue_teams=[333, 444, 555],
               tba_match_key='2026worlds_qm5')
    db.session.add(m5)
    db.session.commit()

    with patch('web.services.priority_service.TBAService.get_event_matches',
               return_value=_tba()):
        result = PriorityService.get_next_scouting_match(ctx['event'], OUR)

    assert result['match'].number == 5  # M4 has no priority teams, M5 has 8888
    assert result['priority_count'] == 1


def test_next_scouting_match_skips_our_own_matches(ctx):
    with patch('web.services.priority_service.TBAService.get_event_matches',
               return_value=_tba()):
        result = PriorityService.get_next_scouting_match(ctx['event'], OUR)
    # M2/M3 are ours; M4 has no priority teams; no other match exists
    assert result is None


def test_next_scouting_match_none_when_no_priority(ctx):
    # No team_number means no priority set
    with patch('web.services.priority_service.TBAService.get_event_matches',
               return_value=_tba()):
        assert PriorityService.get_next_scouting_match(ctx['event'], None) is None


def test_tba_result_is_cached(ctx):
    with patch('web.services.priority_service.TBAService.get_event_matches',
               return_value=_tba()) as mock:
        PriorityService.get_completed_match_keys(ctx['event'])
        PriorityService.get_priority_teams(ctx['event'], OUR)
        PriorityService.get_next_match(ctx['event'], OUR)
    assert mock.call_count == 1
