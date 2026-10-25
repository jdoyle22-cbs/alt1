import os
from wave.__init__ import create_app
from wave.db import db
from wave.models import User

app = create_app()

with app.app_context():
    image_path = "C:\\Users\\James\\Downloads\\image.png"

    if os.path.exists(image_path):
        with open(image_path, "rb") as file:
            raw_binary_bytes = file.read()

        user = db.session.execute(db.select(User).filter_by(id=1)).scalar_one_or_none()

        if user:
            user.profile_picture = raw_binary_bytes
            db.session.commit()
            print("Success! Your user now has a true binary BLOB in the database.")
        else:
            print("User not found.")
    else:
        print(f"Could not find the file at {image_path}. Please check the path!")
