import base64

from flask import Blueprint, g, redirect, render_template, request, session, url_for
from flask_socketio import emit, join_room, leave_room
from sqlalchemy.exc import SQLAlchemyError

from social_site.extensions import socketio

from social_site import db
from social_site.models import Chat, ChatMessage, User


bp = Blueprint('chat', __name__, url_prefix='/chat')

def get_member_chat(chat_id: int, user: User):
    chat = db.session.get(Chat, chat_id)

    if chat is None:
        return None

    if not any(member.id == user.id for member in chat.members):
        return None

    return chat

@bp.route("/")
def chat_index():
    if not g.user:
        return redirect(url_for("auth.login"))
        
    page = db.paginate(
        db.select(Chat)
        .where(Chat.members.any(User.id == g.user.id))
        .order_by(Chat.created_at.desc()),
        page=int(request.args.get("page", 1)),
        per_page=10,
        error_out=False,
    )

    return render_template("/chat/chat_index.html", page=page)

@bp.route("/<int:chat_id>")
def chatroom(chat_id: int):
    if not g.user:
        return redirect(url_for("auth.login"))

    chat = get_member_chat(chat_id, g.user) if g.user else None
    if chat is None:
        return render_template("error/404.html", hide_header=True), 404

    stmt = (
        db.select(ChatMessage)
        .where(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at.asc())
    )

    messages = db.session.execute(stmt).scalars().all()

    profile_picture = None

    if messages:
        for message in messages:
            message.user = db.session.get(User, message.user_id)
            if message.user.profile_picture:
                profile_picture = base64.b64encode(
                    message.user.profile_picture
                ).decode("ascii")
                message.profile_picture = profile_picture

    if not messages:
        messages = ""

    return render_template("/chat/chatroom.html", chat=chat, previous_messages=messages)

# WebSockets
def get_socket_user():
    user_id = session["user_id"]

    if user_id is None:
        return None

    return db.session.get(User, user_id)

@socketio.on('join', namespace='/chat')
def handle_join(data):
    user = get_socket_user()

    if user is None:
        return

    try:
        chat_id = int(data["chatId"])
    except (TypeError, ValueError, KeyError):
        return

    chat = get_member_chat(chat_id, user)
    if chat is None:
        return

    room = f"chat-{chat.id}"
    join_room(room)

    #emit(
    #    "message",
    #    {
    #        "text": f"{user.username} joined the chat"
    #    },
    #    to=room,
    #)

# Handle user messages
@socketio.on('message', namespace='/chat')
def handle_message(data):
    user = get_socket_user()

    if user is None:
        return

    if not isinstance(data, dict):
        return
    
    message = data.get("message")
    chat_id = data.get("chatId")

    if not isinstance(message, str):
        return
    if not message or len(message) > 9999:
        return

    message = message.strip()

    try:
        chat_id = int(chat_id)
    except (TypeError, ValueError):
        return

    chat = get_member_chat(chat_id, user)
    if chat is None:
        return

    room = f"chat-{chat.id}"

    try:
        message_record = ChatMessage(user_id=user.id, chat_id=chat_id, text=message)
        db.session.add(message_record)
        db.session.commit()

        emit(
            "message",
            {
                "text": f"{message}",
                "username": user.username,
                "profile_picture": user.profile_picture
            },
            to=room,
        )
    except SQLAlchemyError as e:
        print(f"[ERR] [DB] {e}")
        db.session.rollback()
        emit(
            "persist_error",
            to=room,
        )
        emit(
            "message",
            {
                "text": f"{message}",
                "username": user.username,
                "profile_picture": user.profile_picture
            },
            to=room,
        )

# Handle disconnects
@socketio.on('disconnect', namespace='/chat')
def handle_disconnect(data):
    print("handle_disconnect")
    user = get_socket_user()

    if user is None:
        return
    
    leave_room(user.username)

    # emit("message", f"{user.username} left the chat", broadcast=True)

@socketio.on_error('/chat')
def error_handler_chat(e):
    emit("chat_error")