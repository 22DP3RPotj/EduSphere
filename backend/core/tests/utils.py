from PIL import Image
from io import BytesIO


def create_test_image():
    file = BytesIO()
    image = Image.new('RGB', (1, 1), color='red')
    image.save(file, 'JPEG')
    file.seek(0)
    return file.read()
