from wave.upload_image import process_and_save_image

from flask import (
    Blueprint,
    abort,
    current_app,
    g,
    jsonify,
    request,
    send_from_directory,
)

bp = Blueprint("upload", __name__, url_prefix="/upload")


@bp.route("/image", methods=["POST"])
def upload_image():
    if not g.user:
        abort(401)

    if "image" not in request.files:
        return jsonify({"error": "No image part in the request"}), 400

    image_file = request.files["image"]

    if image_file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = process_and_save_image(image_file, current_app.config["UPLOAD_FOLDER"])

    if not filename:
        return jsonify({"error": "Invalid file type or extension"}), 400

    return jsonify({"success": True, "filename": filename}), 200


@bp.route("/<name>")
def download_file(name):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], name)
