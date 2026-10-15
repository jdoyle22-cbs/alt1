from flask import Blueprint, abort, g, render_template, request

from social_site import db
from social_site.models import Post, Reply


bp = Blueprint('reply', __name__, url_prefix='/reply')

@bp.route('/create/<int:parent_id>', methods=['GET', 'POST'])
def create(parent_id: int):
    if request.method == 'POST':
        if g.user is None:
            abort(401)

        post = db.session.get(Post, parent_id)
        reply = db.session.get(Reply, parent_id)

        if post is None and reply is None:
            abort(404)

        print("reached post")

        return render_template('components/posts/replies/reply_form.html', parent_id=parent_id, message="Reply submitted successfully.")

    if request.method == 'GET':
        return render_template('components/posts/replies/reply_form.html', parent_id=parent_id)