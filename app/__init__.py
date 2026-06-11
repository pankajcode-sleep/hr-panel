from flask import Flask
from app.config import config_map
from app.extensions import db, migrate, login_manager, bcrypt


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    from app.controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.controllers.dashboard_controller import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    from app.controllers.employee_controller import employee_bp
    app.register_blueprint(employee_bp, url_prefix='/employees')

    from app.controllers.leave_controller import leave_bp
    app.register_blueprint(leave_bp, url_prefix='/leave')

    from app.controllers.attendance_controller import attendance_bp
    app.register_blueprint(attendance_bp, url_prefix='/attendance')

    from app.controllers.employee_self_service import self_service_bp
    app.register_blueprint(self_service_bp, url_prefix='/portal')

    from app.controllers.mood_controller import mood_bp
    app.register_blueprint(mood_bp, url_prefix='/mood')

    from app.controllers.announcement_controller import announcement_bp
    app.register_blueprint(announcement_bp, url_prefix='/announcements')

    from app.errors.handlers import register_error_handlers
    register_error_handlers(app)

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    return app