import pytest
from unittest.mock import patch, MagicMock

from web.extensions import db
from web.models import Game, Team, Event
from web.services.tba_service import TBAService
from web.services.import_service import ImportService


def test_parse_match():
    tba_match = {
        'match_number': 1,
        'comp_level': 'qm',
        'set_number': 1,
        'key': '2025mitraverse_qm1',
        'alliances': {
            'red': {'team_keys': ['frc9771', 'frc1234', 'frc5678']},
            'blue': {'team_keys': ['frc4321', 'frc8765', 'frc2468']},
        },
    }
    parsed = TBAService.parse_match(tba_match)
    assert parsed['number'] == 1
    assert parsed['red_teams'] == [9771, 1234, 5678]
    assert parsed['blue_teams'] == [4321, 8765, 2468]
    assert parsed['tba_match_key'] == '2025mitraverse_qm1'


def test_no_api_key_returns_none(app):
    app.config['TBA_API_KEY'] = None
    with app.app_context():
        result = TBAService.get_event('2025mitraverse')
        assert result is None


@patch('web.services.tba_service.requests.get')
def test_import_event(mock_get, app):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        'name': 'Traverse City District',
        'city': 'Traverse City',
        'state_prov': 'Michigan',
        'start_date': '2025-03-15',
    }
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    with app.app_context():
        game = Game(name='Reefscape', score_config=[])
        db.session.add(game)
        db.session.commit()

        event = ImportService.import_event('2025mitraverse', game.id)
        assert event is not None
        assert event.name == 'Traverse City District'
        assert event.tba_event_key == '2025mitraverse'


@patch('web.services.tba_service.requests.get')
def test_import_event_teams(mock_get, app):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {'team_number': 9771, 'nickname': 'FPRO', 'key': 'frc9771'},
        {'team_number': 1234, 'nickname': 'TestBot', 'key': 'frc1234'},
    ]
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    with app.app_context():
        game = Game(name='Reefscape', score_config=[])
        team = Team(number=9771, name='FPRO', tba_key='frc9771')
        db.session.add_all([game, team])
        db.session.commit()

        event = Event(game_id=game.id, name='Traverse City', tba_event_key='2025mitraverse')
        db.session.add(event)
        db.session.commit()

        count = ImportService.import_event_teams(event.id)
        assert count == 2
        assert len(event.teams) == 2
        assert Team.query.filter_by(number=1234).first() is not None


@patch('web.services.tba_service.requests.get')
def test_import_event_matches(mock_get, app):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {
            'match_number': 1, 'comp_level': 'qm', 'set_number': 1,
            'key': '2025mitraverse_qm1',
            'alliances': {
                'red': {'team_keys': ['frc9771', 'frc1234', 'frc5678']},
                'blue': {'team_keys': ['frc4321', 'frc8765', 'frc2468']},
            },
        },
        {
            'match_number': 1, 'comp_level': 'sf', 'set_number': 1,
            'key': '2025mitraverse_sf1m1',
            'alliances': {
                'red': {'team_keys': ['frc9771']},
                'blue': {'team_keys': ['frc1234']},
            },
        },
    ]
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    with app.app_context():
        game = Game(name='Reefscape', score_config=[])
        db.session.add(game)
        db.session.commit()
        event = Event(game_id=game.id, name='Traverse City', tba_event_key='2025mitraverse')
        db.session.add(event)
        db.session.commit()

        count = ImportService.import_event_matches(event.id)
        assert count == 1  # Only qm matches imported
