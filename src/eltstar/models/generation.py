from pydantic import ConfigDict

from eltstar.base_model import BaseModel
from eltstar.testing.faker_type import FakerType


class Generation(BaseModel):
    """Generation of dummy/fake data (Faker etc.)"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    faker_type: FakerType
