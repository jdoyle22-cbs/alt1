from wave.db import db
from wave.models import Post, Reaction, ReactionType, Reply

from flask import Blueprint, abort, g, json, make_response, render_template
from sqlalchemy import select

bp = Blueprint("post", __name__, url_prefix="/post")


@bp.route("/<int:post_id>", methods=["GET"])
def view(post_id: int):
    # if post is None:
    #    return render_template('error/404.html', hide_header=True), 404

    return render_template("post.html", post_id=post_id)


@bp.post("/<int:post_id>/react/<string:reaction_type>")
def react(post_id: int, reaction_type: str):
    if g.user is None:
        abort(401)

    type_dict: dict[str, ReactionType] = {
        "like": ReactionType.LIKE,
        "dislike": ReactionType.DISLIKE,
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

    success_message = ""
    if reaction_type == "like":
        if existing:
            success_message = "Unliked post."
        else:
            success_message = "Liked post."
    elif reaction_type == "dislike":
        if existing:
            success_message = "Undisliked post."
        else:
            success_message = "Disliked post."

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

    response = make_response(
        render_template(
            "components/posts/reaction_buttons.html",
            post=post,
            user_reaction=user_reaction,
        )
    )

    # Use HTMX to trigger a toast
    # Works only when HTMX handles page load (via hx-boost), but that's fine as forms are "boosted"
    response.headers["HX-Trigger"] = json.dumps(
        {"toast": {"text": success_message, "type": "success"}}
    )

    return response


@bp.get("/<int:post_id>/replies")
def get_replies(post_id: int):
    replies = db.session.execute(db.select(Reply).filter_by(post_id=post_id)).scalars()

    return render_template(
        "components/posts/replies/reply_section.html",
        replies=replies,
    )
