import base64
from wave.db import db
from wave.models import Chat, Post, Topic, User
from wave.upload_image import process_and_save_image

from flask import (
    Blueprint,
    current_app,
    g,
    json,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from icecream import ic
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

bp = Blueprint("create", __name__, url_prefix="/create")


@bp.route("/post", methods=["GET", "POST"])
def create_post():
    if not g.user:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        topic_name = request.form.get("topic_name", "").strip()
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        href = request.form.get("href", "").strip()
        image = request.form.get("image", "").strip()

        error = None

        if not topic_name:
            error = "Please provide a topic."
        elif not title:
            error = "Please provide a title."

        topic = None

        try:
            topic = db.session.query(Topic).where(Topic.name == topic_name).first()
        except SQLAlchemyError as e:
            ic("[ERR] [DB] Creation of record type POST failed with error:", e)
            return render_template(
                "/components/form-message.html",
                message="Sorry. something went wrong.",
                error=True,
            )

        if not topic or topic.id is None:
            return render_template(
                "/components/form-message.html",
                message="That topic doesn't exist.",
                error=True,
            )

        if not body and not href and not image:
            error = "Please provide either a body, href or image."

        if error is None:
            post = Post(
                topic_id=topic.id,
                user_id=g.user.id,
                title=title,
                body=body,
                href=href,
                image=image,
            )
            try:
                db.session.add(post)
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                ic("[ERR] [DB] Creation of record type POST failed with error:", e)
                return render_template(
                    "/components/form-message.html",
                    message="Sorry. something went wrong.",
                    error=True,
                )

            response = make_response("")
            response.headers["HX-Location"] = url_for("post.view", post_id=post.id)
            response.headers["HX-Trigger"] = json.dumps(
                {"toast": {"text": "Post created successfully.", "type": "success"}}
            )

            return response

        return render_template(
            "/components/form-message.html", message=error, error=True
        )

    elif request.method == "GET":
        return render_template("/create/create_post.html")

    return render_template(
        "/components/form-message.html",
        message="Please specify a HTTP method of GET or POST.",
        error=True,
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
        image_file = request.files["image"]

        if not image_file:
            render_template(
                "/components/form-message.html",
                message="Please provide an image to upload.",
                error=True,
            )

        ic("image_file:", image_file)
        filename = process_and_save_image(image_file, current_app.config["UPLOAD_PATH"])

        if not filename:
            return render_template(
                "/components/form-message.html",
                message="Please provide a valid image to upload.",
                error=True,
            )

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
            return render_template(
                "/components/form-message.html",
                message="Description must be equal to or less than 200 characters.",
                error=True,
            )

        image_bytes = base64.b64decode(g.user.profile_picture)
        g.user.profile_picture = image_bytes

        try:
            topic = Topic(
                name=name,
                description=description,
                image=filename,
                members=[g.user],
            )

            db.session.add(topic)
            db.session.commit()

        except IntegrityError:
            return render_template(
                "/components/form-message.html",
                message="That name is already taken.",
                error=True,
            )

        except SQLAlchemyError as e:
            db.session.rollback()
            ic("[ERR] [DB] Creation of record type TOPIC failed:", e)
            return render_template(
                "/components/form-message.html",
                message="Sorry, something went wrong.",
                error=True,
            )

        response = make_response("")
        response.headers["HX-Trigger"] = json.dumps(
            {"toast": {"text": "Topic created successfully.", "type": "success"}}
        )

        return response

    return render_template(
        "/components/form-message.html",
        message="Please specify a HTTP method of GET or POST.",
        error=True,
    )


@bp.route("/chat", methods=["GET", "POST"])
def create_chat():
    if not g.user:
        return render_template(
            "/components/form-message.html",
            message="Cannot fetch your account details. Please try reauthenticating.",
            error=True,
        )

    if request.method == "GET":
        return render_template("/create/create_chat.html")

    if request.method == "POST":
        raw_member_ids = request.form.get("member_ids", "").strip()
        title = request.form.get("title", "").strip()

        if not raw_member_ids:
            error = "Please invite at least one member."
            return render_template(
                "/components/form-message.html", message=error, error=True
            )

        if not title:
            error = "Please provide a title."
            return render_template(
                "/components/form-message.html", message=error, error=True
            )

        if len(title) > 50:
            return render_template(
                "/components/form-message.html",
                message="Title must be equal to or less than 50 characters.",
                error=True,
            )

        try:
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
                    error=True,
                )

            if not member_ids:
                return render_template(
                    "/components/form-message.html",
                    message="Please invite at least one valid member.",
                    error=True,
                )

            users = db.session.scalars(
                db.select(User).where(User.id.in_(member_ids))
            ).all()

            if len(users) != len(member_ids):
                return render_template(
                    "/components/form-message.html",
                    message="One or more users invited do not exist.",
                    error=True,
                )

            current_user = db.session.get(User, g.user.id)
            if not current_user:
                return render_template(
                    "/components/form-message.html",
                    message="Cannot fetch your account details. Please try reauthenticating.",
                    error=True,
                )

            members_by_id = {user.id: user for user in users}
            members_by_id[current_user.id] = current_user

            chat = Chat(
                title=title,
                members=list(members_by_id.values()),
                owner_id=current_user.id,
            )

            db.session.add(chat)
            db.session.commit()

        except SQLAlchemyError as e:
            db.session.rollback()
            ic("[ERR] [DB] Creation of record type CHAT failed:", e)
            return render_template(
                "/components/form-message.html",
                message="Sorry, something went wrong.",
                error=True,
            )

        response = make_response("")
        response.headers["HX-Trigger"] = json.dumps(
            {"toast": {"text": "Chat created successfully.", "type": "success"}}
        )

        return response

    return render_template(
        "/components/form-message.html",
        message="Please specify a HTTP method of GET or POST.",
        error=True,
    )
