import os
import secrets
from PIL import Image


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    basedir = os.path.abspath(os.path.dirname(__file__))
    picture_path = os.path.join(basedir, 'static/img', picture_fn)
    print(picture_path)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
