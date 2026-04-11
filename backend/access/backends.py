from rules.permissions import ObjectPermissionBackend
from backend.account import actions as AccountActions


class SecureRulesBackend(ObjectPermissionBackend):
    def has_perm(self, user_obj, perm, obj=None):
        # Check for Anonymous
        if not user_obj.is_authenticated:
            return super().has_perm(user_obj, perm, obj)

        # Check for Deactivation
        if not user_obj.is_active:
            return False

        # TODO:Use Redis/Memcached for a shared cache backend.
        # Check for Active Bans
        if AccountActions.is_user_banned(user_obj):
            return False

        # Superuser
        if user_obj.is_superuser:
            return True

        return super().has_perm(user_obj, perm, obj)
