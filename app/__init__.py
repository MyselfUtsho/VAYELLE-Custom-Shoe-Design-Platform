import os
from flask import Flask, render_template
from config import Config

def create_app(config_class=Config):
    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates'
    )
    app.config.from_object(config_class)

    # Register Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.manager import manager_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(manager_bp)

    # Template context helpers
    @app.context_processor
    def inject_helpers():
        def bdt(amount):
            try:
                return f"৳{float(amount):,.0f}"
            except (ValueError, TypeError):
                return f"৳{amount}"
        return dict(bdt=bdt)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', content="<div class='section-container' style='text-align:center;padding:80px 20px;'><h1 style='font-size:4rem;color:var(--accent);'>404</h1><h2>Page Not Found</h2><p style='color:var(--text-muted);margin:16px 0;'>The page you are looking for does not exist.</p><a href='/' class='btn btn-primary'>Return Home</a></div>"), 404

    @app.errorhandler(403)
    def access_forbidden(e):
        return render_template('base.html', content="<div class='section-container' style='text-align:center;padding:80px 20px;'><h1 style='font-size:4rem;color:var(--accent);'>403</h1><h2>Access Denied</h2><p style='color:var(--text-muted);margin:16px 0;'>You do not have permission to view this manager resource.</p><a href='/' class='btn btn-primary'>Return Home</a></div>"), 403

    return app
