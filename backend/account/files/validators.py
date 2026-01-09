from PIL import Image, UnidentifiedImageError
from django.forms import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class ImageValidator:
    message = "Uploaded file is not a valid image."
    code = "invalid_image"

    def __call__(self, file):
        try:
            Image.open(file).verify()
        except (UnidentifiedImageError, OSError):
            raise ValidationError(self.message, code=self.code)
