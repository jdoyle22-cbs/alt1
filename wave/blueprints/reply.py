from icecream import ic
from wave.db import db
from wave.models import Post, Reply

from flask import Blueprint, g, render_template, request
from sqlalchemy.exc import SQLAlchemyError

bp = Blueprint("reply", __name__, url_prefix="/reply")


@bp.route("/create/post/<int:parent_id>", methods=["GET", "POST"])
def create_post_reply(parent_id: int):
    if request.method == "POST":
        if not g.user:
            return render_template(
                "/components/form-message.html",
                message="Failed to submit reply. Please reauthenticate.",
                error=True,
            )

        text = request.form.get(f"reply_{parent_id}_content", "").strip()
        post = db.session.get(Post, parent_id)

        if not text:
            return render_template(
                "/components/form-message.html",
                message="Please provide text for the reply.",
                error=True,
            )

        if not post:
            return render_template(
                "/components/form-message.html",
                message="Failed to find reply. It may have been deleted.",
                error=True,
            )

        try:
            reply = Reply(user_id=g.user.id, parent_id=parent_id, text=text)
            db.session.add(reply)
            db.session.commit()
        except SQLAlchemyError as e:
            ic(f"[DB] [ERR] {e}")
            db.session.rollback()
            return render_template(
                "/components/form-message.html",
                message="Failed to submit reply. Check your internet connection and try again.",
                error=True,
            )

        return render_template(
            "/components/form-message.html",
            message="Reply submitted successfully.",
        )

    if request.method == "GET":
        return render_template(
            "components/posts/replies/reply_form.html",
            parent_type="post",
            parent_id=parent_id,
        )

    return render_template(
        "/components/form-message.html",
        message="Please specify a HTTP method of GET or POST.",
        error=True,
    )


@bp.route("/create/reply/<int:parent_id>", methods=["GET", "POST"])
def create_reply_reply(parent_id: int):
    if request.method == "POST":
        if not g.user:
            return render_template(
                "/components/form-message.html",
                message="Failed to submit reply. Please reauthenticate.",
                error=True,
            )

        text = request.form.get(f"reply_{parent_id}_content", "").strip()
        reply = db.session.get(Reply, parent_id)

        if not text:
            return render_template(
                "/components/form-message.html",
                message="Please provide text for the reply.",
                error=True,
            )

        if not reply:
            return render_template(
                "/components/form-message.html",
                message="Failed to find reply. It may have been deleted.",
                error=True,
            )

        try:
            reply = Reply(user_id=g.user.id, parent_id=parent_id, text=text)
            db.session.add(reply)
            db.session.commit()
        except SQLAlchemyError as e:
            ic(f"[DB] [ERR] {e}")
            db.session.rollback()
            return render_template(
                "/components/form-message.html",
                message="Failed to submit reply. Check your internet connection and try again.",
                error=True,
            )

        return render_template(
            "/components/form-message.html",
            message="Reply submitted successfully.",
        )

    if request.method == "GET":
        return render_template(
            "components/posts/replies/reply_form.html",
            parent_type="reply",
            parent_id=parent_id,
        )

    return render_template(
        "/components/form-message.html",
        message="Please specify a HTTP method of GET or POST.",
        error=True,
    )
