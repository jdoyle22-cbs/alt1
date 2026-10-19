import base64

from flask import Blueprint, g, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from social_site import db
from social_site.models import Chat, Post, Topic, User

bp = Blueprint('create', __name__, url_prefix='/create')

@bp.route("/post", methods=["GET", "POST"])
def create_post():
    if not g.user:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        topic_id = request.form.get('topic_id', '').strip()
        title = request.form.get('title', '').strip()
        body = request.form.get('body', '').strip()
        href = request.form.get('href', '').strip()
        image = request.form.get('image', '').strip()

        error = None

        if not topic_id:
            error = "Please provide a topic ID."
        elif not title:
            error = "Please provide a title."

        topic = db.session.get(Topic, topic_id)

        if not topic:
            error = "That topic doesn't exist."

        if not body and not href and not image:
            error = "Please provide either a body, href or image."

        if error is None:
            try:
                db.session.add(Post(topic_id=topic_id, user_id=g.user.id, title=title, body=body, href=href, image=image))
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                print("[ERR] [DB] Creation of record type POST failed with error:", e)
                error = "Sorry, something went wrong."
            else:
                return redirect(url_for("index"))

        return render_template("/components/form-message.html", message=error)

    elif request.method == "GET":
        return render_template("/create/create_post.html")

    return render_template(
        "/components/form-message.html",
        message="Please specify a HTTP method of GET or POST.",
        error=True
    )


@bp.route("/topic", methods=["GET", "POST"])
def create_topic():
    if not g.user:
        return redirect(url_for("auth.login"))

    if request.method == "GET":
        return render_template("/create/create_topic.html")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            error = "Please provide a name."
            return render_template(
                "/components/form-message.html", message=error, error=True
            )

        if not description:
            error = "Please provide a description."
            return render_template(
                "/components/form-message.html", message=error, error=True
            )

        if len(description) > 200:
            return render_template("/components/form-message.html", message="Description must be equal to or less than 200 characters.", error=True)

        image_bytes = base64.b64decode(g.user.profile_picture)
        g.user.profile_picture = image_bytes

        try:
            topic = Topic(
                name=name,
                description=description,
                members=[g.user],
            )

            db.session.add(topic)
            db.session.commit()

        except IntegrityError:
            return render_template(
                "/components/form-message.html",
                message="That name is already taken.",
                error=True
            )
        
        except SQLAlchemyError as e:
            db.session.rollback()
            print("[ERR] [DB] Creation of record type TOPIC failed:", e)
            return render_template(
                "/components/form-message.html",
                message="Sorry, something went wrong.",
                error=True
            )

        return render_template(
            "/components/form-message.html",
            message="Topic was created successfully.",
        )

    return render_template(
        "/components/form-message.html",
        message="Please specify a HTTP method of GET or POST.",
        error=True
    )


@bp.route("/chat", methods=["GET", "POST"])
def create_chat():
    if not g.user:
        return redirect(url_for("auth.login"))

    if request.method == "GET":
        return render_template("/create/create_chat.html")

    if request.method == "POST":
        raw_member_ids = request.form.get("member_ids", "").strip()
        title = request.form.get("title", "").strip()

        if not raw_member_ids:
            error = "Please invite at least one member."
            return render_template(
                "/components/form-message.html", message=error
            )

        if not title:
            error = "Please provide a title."
            return render_template(
                "/components/form-message.html", message=error
            )

        if len(title) > 50:
            return render_template("/components/form-message.html", message="Title must be equal to or less than 50 characters.")

        try:
            # Parse and validate the submitted IDs.
            try:
                member_ids = {
                    int(value.strip())
                    for value in raw_member_ids.split(",")
                    if value.strip()
                }
            except ValueError:
                return render_template(
                    "/components/form-message.html",
                    message="Member IDs must be integers.",
                )

            if not member_ids:
                return render_template(
                    "/components/form-message.html",
                    message="Please invite at least one valid member.",
                )

            users = db.session.scalars(
                db.select(User).where(User.id.in_(member_ids))
            ).all()

            if len(users) != len(member_ids):
                return render_template(
                    "/components/form-message.html",
                    message="One or more users invited do not exist.",
                )

            current_user = db.session.get(User, g.user.id)

            members_by_id = {user.id: user for user in users}
            members_by_id[current_user.id] = current_user

            chat = Chat(
                title=title,
                members=list(members_by_id.values()),
            )

            db.session.add(chat)
            db.session.commit()

        except SQLAlchemyError as e:
            db.session.rollback()
            print("[ERR] [DB] Creation of record type CHAT failed:", e)
            return render_template(
                "/components/form-message.html",
                message="Sorry, something went wrong.",
            )

        return redirect(url_for("index"))

    return render_template(
        "/components/form-message.html",
        message="Please specify a HTTP method of GET or POST.",
        error=True
    )