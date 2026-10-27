from icecream import ic
from PIL import Image
import uuid
import os

import filetype
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

ALLOWED_IMG_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "avif", "webp", "tiff"}


def validate_image_filetype(file_bytes: bytes) -> bool:
    kind = filetype.guess(file_bytes)
    if not kind:
        return False

    return "image" in kind.mime


def allowed_image_file(filename: str) -> bool:
    return (
        "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMG_EXTENSIONS
    )


def process_and_save_image(image_file: FileStorage, upload_path: str) -> str | None:
    if not image_file.filename or not allowed_image_file(image_file.filename):
        return None

    header = image_file.read(2048)
    image_file.seek(0)

    if not validate_image_filetype(header):
        return None

    try:
        with Image.open(image_file.stream) as img:
            max_size = (1200, 1200)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            base_name, _ = os.path.splitext(secure_filename(image_file.filename))
            unique_filename = f"{base_name}_{uuid.uuid4()}.webp"

            os.makedirs(upload_path, exist_ok=True)
            full_path = os.path.join(upload_path, unique_filename)

            img.save(full_path, "WEBP", quality=82, optimize=True)

            return unique_filename

    except Exception as e:  # noqa: BLE001
        ic(f"[ERR] Image processing/upload error: \n{e}")
        return None
