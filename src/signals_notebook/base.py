import inspect
from typing import no_type_check

from pydantic import BaseModel


class PatchedModel(BaseModel):
    """
    https://github.com/samuelcolvin/pydantic/issues/1577
    Adds ability to use properties with setters
    """
    @no_type_check
    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except ValueError as e:
            setters = inspect.getmembers(
                self.__class__, predicate=lambda x: isinstance(x, property) and x.fset is not None
            )
            for setter_name, func in setters:
                if setter_name == name:
                    object.__setattr__(self, name, value)
                    break
            else:
                raise e
