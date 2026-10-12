from flask import Blueprint, abort, g, render_template
from sqlalchemy import select
from social_site.db import db_session
from social_site.models import Post, Reaction, ReactionType, Reply

bp = Blueprint('post', __name__, url_prefix='/post')

@bp.route('/<int:post_id>', methods=['GET'])
def view(post_id: int):
    post = db_session.get(Post, post_id)

    if post is None:
        abort(404)

    reaction = None

    if g.user is not None:
        reaction = db_session.scalar(
            select(Reaction).where(
                Reaction.post_id == post.id,
                Reaction.user_id == g.user.id,
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

    post = db_session.get(Post, post_id)
    if post is None:
        return render_template("components/posts/reaction_buttons.html")

    existing = db_session.scalar(
        select(Reaction).where(
            Reaction.post_id == post_id,
            Reaction.user_id == g.user.id,
        )
    )

    requested_type = type_dict[reaction_type]

    if existing is None:
        db_session.add(
            Reaction(
                post_id=post_id,
                user_id=g.user.id,
                type=requested_type,
            )
        )
    elif existing.type == requested_type:
        db_session.delete(existing)
    else:
        existing.type = requested_type

    db_session.commit()

    user_reaction = db_session.scalar(
        select(Reaction).where(
            Reaction.post_id == post_id,
            Reaction.user_id == g.user.id,
        )
    )

    return render_template(
        "components/posts/reaction_buttons.html",
        post=post,
        user_reaction=user_reaction,
    )

@bp.get("/<int:post_id>/replies")
def get_replies(post_id: int):
    replies = db_session.query(Reply).filter(Reply.post_id == post_id).all()

    return render_template(
        "components/posts/replies/reply_section.html",
        replies=replies,
    )