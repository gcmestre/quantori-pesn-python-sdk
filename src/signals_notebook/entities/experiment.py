from enum import Enum
from functools import cached_property
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field

from signals_notebook.common_types import Ancestors, EntityCreationRequestPayload, EntityType, Template
from signals_notebook.entities.container import Container
from signals_notebook.entities.notebook import Notebook
from signals_notebook.entities.stoichiometry.stoichiometry import Stoichiometry


class _Attributes(BaseModel):
    name: str
    description: Optional[str] = None


class _Relationships(BaseModel):
    template: Optional[Template] = None
    ancestors: Optional[Ancestors] = None


class _RequestBody(BaseModel):
    type: EntityType
    attributes: _Attributes
    relationships: Optional[_Relationships] = None


class _RequestPayload(EntityCreationRequestPayload[_RequestBody]):
    pass


class ExperimentState(str, Enum):
    OPEN = 'open'
    CLOSED = 'closed'


class Experiment(Container):
    type: Literal[EntityType.EXPERIMENT] = Field(allow_mutation=False)
    state: Optional[ExperimentState] = Field(allow_mutation=False, default=None)

    class Config:
        keep_untouched = (cached_property,)

    @classmethod
    def _get_entity_type(cls) -> EntityType:
        return EntityType.EXPERIMENT

    @classmethod
    def create(
        cls,
        *,
        name: str,
        description: Optional[str] = None,
        template: Optional['Experiment'] = None,
        notebook: Optional[Notebook] = None,
        digest: str = None,
        force: bool = True,
    ) -> 'Notebook':

        relationships = None
        if template or notebook:
            relationships = _Relationships(
                ancestors=Ancestors(data=[notebook.short_description]) if notebook else None,
                template=Template(data=template.short_description) if template else None,
            )

        request = _RequestPayload(
            data=_RequestBody(
                type=cls._get_entity_type(),
                attributes=_Attributes(
                    name=name,
                    description=description,
                ),
                relationships=relationships,
            )
        )

        return super()._create(
            digest=digest,
            force=force,
            request=request,
        )

    @cached_property
    def stoichiometry(self) -> Union[Stoichiometry, list[Stoichiometry]]:
        return Stoichiometry.fetch_data(self.eid)
