import os
import secrets

from dotenv import load_dotenv

from social_site.db import db, init_db_command
from social_site.models import Post
load_dotenv()

from flask import Flask, g, render_template, request, Response
from werkzeug.exceptions import NotFound, Unauthorized

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
    def set_csp_header(response: Response) -> Response:
        nonce = g.csp_nonce

        # Content Security Policy, prevents many types of attacks by verifying scripts are legitimate
        # See MDN Web Docs: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}'; "
            f"style-src 'self' 'nonce-{nonce}'; "
            "object-src 'self' https://youtube.com https://imgur.com; "
            "base-uri 'self'; "
            "img-src 'self' data:; "
            "require-trusted-types-for 'script'; "
            "trusted-types htmx"
        )

        return response

    @app.route('/')
    def index():
        page = db.paginate(
            db.select(Post).order_by(Post.created_at.desc()),
            page=int(request.args.get("page", 1)),
            per_page=10,
            error_out=False,
        )
            
        return render_template('index.html', page=page)

    # Error handlers
    @app.errorhandler(NotFound)
    def not_found(error: NotFound):
        return render_template('error/404.html', hide_header=True), 404

    @app.errorhandler(Unauthorized)
    def unauthorized(error: Unauthorized):
        return render_template('error/401.html', hide_header=True), 401

    # CLI
    app.cli.add_command(init_db_command)

    # Blueprints
    from .blueprints import auth, post, reply, create, chat
    app.register_blueprint(auth.bp)
    app.register_blueprint(post.bp)
    app.register_blueprint(reply.bp)
    app.register_blueprint(create.bp)
    app.register_blueprint(chat.bp)

    # DB
    db.init_app(app)

    return app