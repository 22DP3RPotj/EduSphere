from PIL import Image, UnidentifiedImageError
from django.core.exceptions import ValidationError
from django.core.files import File
from django.utils.deconstruct import deconstructible


@deconstructible
class FileSizeValidator:
    """
    Validator for file size.

    Args:
        size_limit (int): Maximum allowed file size in **megabytes (MB)**.

    Raises:
        ValidationError: If the uploaded file exceeds the size limit.
    """

    code = "file_too_large"

    def __init__(self, size_limit: int):
        self.size_limit = size_limit * 1024 * 1024

    def __call__(self, file: File):
        if file.size > self.size_limit:
            raise ValidationError(
                f"File exceeds the size limit ({self.size_limit} MB).", code=self.code
            )


@deconstructible
class ImageValidator:
    """
    Validator for image files.

    Raises:
        ValidationError: If the uploaded file is not a valid image.
    """

    code = "invalid_image"

    def __call__(self, file: File):
        try:
            pos = file.tell()
        except (AttributeError, OSError):
            pos = None

        try:
            with Image.open(file) as img:
                img.verify()
        except UnidentifiedImageError:
            raise ValidationError("Provided file is not a valid image.", code=self.code)
        except OSError:
            raise ValidationError("Could not process the image file.", code=self.code)
        finally:
            try:
                if pos is not None:
                    file.seek(pos)
                else:
                    file.seek(0)
            except (AttributeError, OSError):
                pass
