from web.extensions import db
from web.models.robot import Robot
from web.models.event import Event


class RobotService:

    @staticmethod
    def get_robot(team_id, game_id):
        return Robot.query.filter_by(team_id=team_id, game_id=game_id).first()

    @staticmethod
    def save_robot(team_id, game_id, scouting_data):
        robot = Robot.query.filter_by(team_id=team_id, game_id=game_id).first()
        if robot:
            robot.scouting_data = scouting_data
        else:
            robot = Robot(team_id=team_id, game_id=game_id, scouting_data=scouting_data)
            db.session.add(robot)
        db.session.commit()
        return robot

    @staticmethod
    def get_scouted_status(event_id, game_id):
        event = db.session.get(Event, event_id)
        if not event:
            return {}
        team_ids = [t.id for t in event.teams]
        robots = Robot.query.filter(
            Robot.team_id.in_(team_ids),
            Robot.game_id == game_id,
        ).all()
        scouted_ids = {r.team_id for r in robots}
        return {tid: tid in scouted_ids for tid in team_ids}
