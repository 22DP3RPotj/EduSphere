import os
import uuid
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from backend.account.models import User


def avatar_upload_path(instance: "User", filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return f"avatars/{instance.id}/{uuid.uuid4()}{ext}"
