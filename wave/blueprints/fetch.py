from wave.db import db
from wave.models import Post, Reaction

from feedgen.feed import FeedGenerator
from flask import Blueprint, Response, g, render_template, request

bp = Blueprint("fetch", __name__, url_prefix="/fetch")


@bp.route("/htmx/feed", methods=["GET"])
def fetch_htmx_feed():
    page = db.paginate(
        db.select(Post).order_by(Post.created_at.desc()),
        page=int(request.args.get("page", 1)),
        per_page=10,
        error_out=False,
    )

    if g.user:
        for post in page.items:
            reaction = db.session.scalar(
                db.select(Reaction).filter_by(
                    post_id=post.id,
                    user_id=g.user.id,
                )
            )

            post.user_reaction = reaction

    return render_template("/components/posts/post_list.html", page=page)


@bp.route("/rss/feed", methods=["GET"])
def fetch_rss_feed() -> Response:
    page = db.paginate(
        db.select(Post).order_by(Post.created_at.desc()),
        page=int(request.args.get("page", 1)),
        per_page=10,
        error_out=False,
    )

    fg = FeedGenerator()
    fg.title("Feed")
    fg.description("Your personal feed")
    fg.link(href="https://localhost/fetch/rss/feed", rel="self")
    fg.link(href="https://localhost/", rel="alternate")

    for post in page.items:
        fe = fg.add_entry()
        fe.id(f"https://localhost/post/{post.id}")
        fe.title(post.title)
        fe.author({"name": post.user.username})
        fe.description(post.body[:50])
        fe.content(post.body, type="html")
        fe.link(href=f"https://localhost/post/{post.id}")

    rssfeed: bytes = fg.rss_str(pretty=True)

    return Response(rssfeed, mimetype="application/rss+xml")


@bp.route("/htmx/post/<int:post_id>", methods=["GET"])
def fetch_post_view(post_id: int):
    post = db.session.get(Post, post_id)

    if post is None:
        return "<p>Post was not found</p>", 404

    reaction = None

    if g.user is not None:
        reaction = db.session.scalar(
            db.select(Reaction).filter_by(
                post_id=post.id,
                user_id=g.user.id,
            )
        )

        post.user_reaction = reaction  # type: ignore This assigns anyway, it's fine

    return render_template("/components/posts/post_view.html", post=post)
