from backend.account.models import User
from backend.graphql.dataloaders import BaseModelLoader


class UserLoader(BaseModelLoader):
    model = User
