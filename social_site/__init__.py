import argparse
from datetime import datetime, timedelta
import os
import secrets

from dotenv import load_dotenv
import humanize
from social_site.extensions import socketio, compress

from social_site.db import db, init_db_command
from social_site.models import Post
load_dotenv()

from flask import Flask, g, render_template, request, Response, send_from_directory
from werkzeug.exceptions import NotFound, Unauthorized
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ["SECRET_KEY"], 
        SQLALCHEMY_DATABASE_URI='sqlite:///project.db',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,  # Only when using HTTPS
        COMPRESS_ALGORITHM=["br", "gzip", "deflate"],
        COMPRESS_ALGORITHM_STREAMING=["br", "deflate"],
        COMPRESS_BR_LEVEL=5
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
            "style-src-attr 'unsafe-inline'; "
            "connect-src 'self' https://localhost ws://localhost wss://localhost; "
            "object-src 'self' https://youtube.com https://imgur.com; "
            "base-uri 'self'; "
            "img-src 'self' data:; "
            "require-trusted-types-for 'script'; "
            "trusted-types htmx"
        )

        response.headers["Cross-Origin-Resource-Policy"] = "same-site"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Embedder-Policy"] = "credentialless"
        response.headers["Vary"] = "HX-Request"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), usb=()"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Frame-Options"] = "DENY"

        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000",
            "includeSubDomains",
            "preload"
        )

        return response

    @app.route('/robots.txt')
    def robots_txt():
        return send_from_directory("static", 'robots.txt')

    @app.route('/')
    def index():
        return render_template('index.html')

    # Error handlers
    @app.errorhandler(NotFound)
    def not_found(error: NotFound):
        return render_template('error/404.html', hide_header=True), 404

    @app.errorhandler(Unauthorized)
    def unauthorized(error: Unauthorized):
        return render_template('error/401.html', hide_header=True), 401

    # Template Filters
    @app.template_filter("naturaltime")
    def naturaltime_filter(value: datetime | timedelta | float)-> str:
        return humanize.naturaltime(value)

    # CLI
    app.cli.add_command(init_db_command)

    # Blueprints
    from .blueprints import auth, post, reply, create, chat, fetch
    app.register_blueprint(auth.bp)
    app.register_blueprint(post.bp)
    app.register_blueprint(reply.bp)
    app.register_blueprint(create.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(fetch.bp)

    # Init
    db.init_app(app)
    socketio.init_app(app)
    compress.init_app(app)

    # Proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    return app

if __name__ == '__main__':
    app = create_app()
    
    parser = argparse.ArgumentParser(description="Run the Flask-SocketIO Social App Server")
    parser.add_argument("--debug", action="store_true", help="Run server in Debug mode")
    parser.add_argument("--host", default="127.0.0.1", help="Server host binding address")
    parser.add_argument("--port", type=int, default=5000, help="Server port")
    parser.add_argument("--cert", help="Path to your SSL certificate (.pem)")
    parser.add_argument("--key", help="Path to your SSL certificate private key (.pem)")
    
    args = parser.parse_args()

    ssl_context = None
    if args.cert and args.key:
        ssl_context = (args.cert, args.key)

    socketio.run(
        app, 
        debug=args.debug, 
        log_output=True,         
        host=args.host,
        port=args.port,
        certfile=args.cert,
        keyfile=args.key
    )