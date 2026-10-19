from flask import Blueprint, g, render_template, request
from sqlalchemy.exc import SQLAlchemyError

from social_site import db
from social_site.models import Post, Reply


bp = Blueprint('reply', __name__, url_prefix='/reply')

@bp.route('/create/post/<int:parent_id>', methods=['GET', 'POST'])
def create_post_reply(post_id: int):
    if request.method == 'POST':
        if g.user is None:
            return render_template(
                "/components/form-message.html",
                message="Failed to submit reply. Please reauthenticate.",
                error=True
            )

        text = request.form.get(f'reply_{post_id}_content', '').strip()
        post = db.session.get(Post, post_id)

        if post is None:
            return render_template(
                "/components/form-message.html",
                message="Failed to find reply. It may have been deleted.",
                error=True
            )

        try:
            reply = Reply(user_id=g.user.id, post_id=post_id, text=text)
            db.session.add(reply)
        except SQLAlchemyError as e:
            print(f"[DB] [ERR] {e}")
            db.session.rollback()
            return render_template(
                "/components/form-message.html",
                message="Failed to submit reply. Check your internet connection and try again.",
                error=True
            )

        return render_template(
            "/components/form-message.html",
            message="Reply submitted successfully.",
        )

    if request.method == 'GET':
        return render_template('components/posts/replies/reply_form.html', parent_type="post", parent_id=post_id)

    return render_template(
        "/components/form-message.html",
        message="Please specify a HTTP method of GET or POST.",
        error=True
    )

@bp.route('/create/reply/<int:parent_id>', methods=['GET', 'POST'])
def create_reply_reply(reply_id: int):
    if request.method == 'POST':
        if g.user is None:
            return render_template(
                "/components/form-message.html",
                message="Failed to submit reply. Please reauthenticate.",
                error=True
            )

        text = request.form.get(f'reply_{reply_id}_content', '').strip()
        reply = db.session.get(Reply, reply_id)

        if reply is None:
            return render_template(
                "/components/form-message.html",
                message="Failed to find reply. It may have been deleted.",
                error=True
            )

        try:
            reply = Reply(user_id=g.user.id, parent_id=reply_id, text=text)
            db.session.add(reply)
        except SQLAlchemyError as e:
            print(f"[DB] [ERR] {e}")
            db.session.rollback()
            return render_template(
                "/components/form-message.html",
                message="Failed to submit reply. Check your internet connection and try again.",
                error=True
            )

        return render_template(
            "/components/form-message.html",
            message="Reply submitted successfully.",
        )

    if request.method == 'GET':
        return render_template('components/posts/replies/reply_form.html', parent_type="reply", parent_id=reply_id)

    return render_template(
        "/components/form-message.html",
        message="Please specify a HTTP method of GET or POST.",
        error=True
    )

    