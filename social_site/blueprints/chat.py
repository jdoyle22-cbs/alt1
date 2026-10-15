from flask import Blueprint, g, redirect, render_template, request, url_for

from social_site import db
from social_site.models import Chat


bp = Blueprint('chat', __name__, url_prefix='/chat')

@bp.route("/")
def chat_index():
    if not g.user:
        return redirect(url_for("auth.login"))
        
    page = db.paginate(
        db.select(Chat).order_by(Chat.created_at.desc()),
        page=int(request.args.get("page", 1)),
        per_page=10,
        error_out=False,
    )

    return render_template("/chat/chat_index.html", page=page)

@bp.route("/<int:chat_id>")
def chatroom(chat_id: int):
    if not g.user:
        return redirect(url_for("auth.login"))
    
    return render_template("/chat/chatroom.html")