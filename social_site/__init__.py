import os
import secrets

from dotenv import load_dotenv

from social_site.models import Post
load_dotenv()

from flask import Flask, g, render_template
from social_site.db import db_session, init_db_command

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ["SECRET_KEY"], 
        SQLALCHEMY_DATABASE_URI='sqlite:///project.db',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,  # Only when using HTTPS
    )

    os.makedirs(app.instance_path, exist_ok=True)

    # CSP
    @app.before_request
    def generate_csp_nonce():
        g.csp_nonce = secrets.token_urlsafe(16)

    @app.after_request
    def set_csp_header(response):
        nonce = g.csp_nonce

        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}'; "
            f"style-src 'self' 'nonce-{nonce}'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "require-trusted-types-for 'script'; "
            "trusted-types htmx"
        )

        return response

    posts = Post.query.all()

    @app.route('/')
    def index():
        return render_template('index.html', posts=posts)

    @app.route('/api/status')
    def status():
        return { 
            "server_online": True
        }

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    app.cli.add_command(init_db_command)
    
    from .blueprints import auth, post
    app.register_blueprint(auth.bp)
    app.register_blueprint(post.bp)

    return app