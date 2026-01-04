from io import BytesIO
from PIL import Image


def create_test_image() -> bytes:
    file = BytesIO()
    image = Image.new("RGB", (1, 1), color="red")
    image.save(file, "JPEG")
    file.seek(0)
    return file.read()
