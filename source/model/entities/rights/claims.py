from source.core.database.postgres import Base
from source.model.mixins.rights import RightsBaseMixin


class Claims(Base, RightsBaseMixin):
    __tablename__ = "claims"
