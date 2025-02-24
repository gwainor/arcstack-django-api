from typing import Any

import pydantic


# isort: off


def is_accepted_pydantic_type(data: Any) -> bool:
    """Check if the data is an accepted pydantic type

    Accepted types are:
    - dict
    - list
    - pydantic.BaseModel
    """
    return (
        isinstance(data, dict)
        or isinstance(data, list)
        or isinstance(data, pydantic.BaseModel)
    )
