from flask import Blueprint, abort, g, render_template
from sqlalchemy import select
from social_site.db import db
from social_site.models import Post, Reaction, ReactionType, Reply

bp = Blueprint('post', __name__, url_prefix='/post')

@bp.route('/<int:post_id>', methods=['GET'])
def view(post_id: int):
    post = db.session.get(Post, post_id)

    if post is None:
        abort(404)

    reaction = None

    if g.user is not None:
        reaction = db.session.scalar(
            db.select(Reaction).filter_by(
                post_id=post.id,
                user_id=g.user.id,
            )
        )

    return render_template('post.html', post=post, user_reaction=reaction)

@bp.post("/<int:post_id>/react/<string:reaction_type>")
def react(post_id: int, reaction_type: str):
    if g.user is None:
        abort(401)

    type_dict: dict[str, ReactionType] = {
        "like": ReactionType.LIKE,
        "dislike": ReactionType.DISLIKE
    }

    if reaction_type not in type_dict:
        return render_template("components/posts/reaction_buttons.html")

    post = db.session.get(Post, post_id)
    if post is None:
        return render_template("components/posts/reaction_buttons.html")

    existing = db.session.scalar(
        select(Reaction).filter_by(
            post_id=post_id,
            user_id=g.user.id,
        )
    )

    requested_type = type_dict[reaction_type]

    if existing is None:
        db.session.add(
            Reaction(
                post_id=post_id,
                user_id=g.user.id,
                type=requested_type,
            )
        )
    elif existing.type == requested_type:
        db.session.delete(existing)
    else:
        existing.type = requested_type

    db.session.commit()

    user_reaction = db.session.scalar(
        select(Reaction).filter_by(
            id=post_id,
            user_id=g.user.id,
        )
    )

    return render_template(
        "components/posts/reaction_buttons.html",
        post=post,
        user_reaction=user_reaction,
    )

@bp.get("/<int:post_id>/replies")
def get_replies(post_id: int):
    replies = db.session.execute(db.select(Reply).filter_by(post_id=post_id)).scalars()

    return render_template(
        "components/posts/replies/reply_section.html",
        replies=replies,
    )