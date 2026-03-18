from flask import Flask, render_template

from config import Config
from web.extensions import db, migrate


def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static',
    )
    app.config.from_object(config_class)

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so Alembic discovers them
    import web.models  # noqa: F401

    # Blueprints
    from web.routes.main import main_bp
    from web.routes.scouting import scouting_bp
    from web.routes.teams import teams_bp
    from web.routes.matches import matches_bp
    from web.routes.admin import admin_bp
    from web.routes.analytics import analytics_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(scouting_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(matches_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(analytics_bp)

    # CLI commands
    from web.commands import seed_command, import_matches_command, seed_demo_command
    app.cli.add_command(seed_command)
    app.cli.add_command(import_matches_command)
    app.cli.add_command(seed_demo_command)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app
