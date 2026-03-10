from django.db import models


class InviteStatusChoices(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"
    DECLINED = "DECLINED", "Declined"
    EXPIRED = "EXPIRED", "Expired"
    REVOKED = "REVOKED", "Revoked"

    @classmethod
    def resolved(cls) -> tuple[str, ...]:
        return (InviteStatusChoices.ACCEPTED, InviteStatusChoices.DECLINED)
