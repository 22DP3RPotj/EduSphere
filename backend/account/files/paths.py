import os
import uuid


def avatar_upload_path(instance, filename: str) -> str:
    ext = os.path.splitext(filename)[1]
    return f"avatars/{instance.id}/{uuid.uuid4()}{ext}"
