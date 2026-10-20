from flask import Blueprint, Response, g, render_template, request

from social_site import db
from social_site.models import Post, Reaction

from feedgen.feed import FeedGenerator

bp = Blueprint('fetch', __name__, url_prefix='/fetch')

@bp.route('/htmx/feed', methods=['GET'])
def fetch_htmx_feed():
    page = db.paginate(
        db.select(Post).order_by(Post.created_at.desc()),
        page=int(request.args.get("page", 1)),
        per_page=10,
        error_out=False,
    )

    return render_template("/components/posts/post_list.html", page=page)

@bp.route('/rss/feed', methods=['GET'])
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
        fe.author( {'name': post.user.username } )
        fe.description(post.body[:50])
        fe.content(post.body, type="html")
        fe.link(href=f"https://localhost/post/{post.id}")

    rssfeed: bytes = fg.rss_str(pretty=True)

    return Response(rssfeed, mimetype='application/rss+xml')

@bp.route('/<int:post_id>', methods=['GET'])
def fetch_post_view(post_id: int):
    post = db.session.get(Post, post_id)

    reaction = None

    if g.user is not None:
        reaction = db.session.scalar(
            db.select(Reaction).filter_by(
                post_id=post.id,
                user_id=g.user.id,
            )
        )

    return render_template('/components/posts/post_card.html', post=post, user_reaction=reaction)