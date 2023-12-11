import dataclasses
import uuid


@dataclasses.dataclass
class User:
    display_name: str
    token: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
