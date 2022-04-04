import json
from datetime import datetime
from enum import Enum
from typing import cast, Generator, List, Union

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.entities import Entity
from signals_notebook.common_types import EID, EntityType, Response, ResponseData


class EntityStore:
    class IncludeOptions(str, Enum):
        MINE = 'mine'
        OTHER = 'other'
        SHARED = 'shared'
        TRASHED = 'trashed'
        UNTRASHED = 'untrashed'
        TRASHED_ANCESTOR = 'trashedAncestor'
        STARRED = 'starred'
        UNSTARRED = 'unstarred'
        TEMPLATE = 'template'
        NONTEMPLATE = 'nontemplate'
        SYSTEM_TEMPLATE = 'systemTemplate'
        NON_SYSTEM_TEMPLATE = 'nonSystemTemplate'

    @staticmethod
    def _get_endpoint() -> str:
        return 'entities'

    @classmethod
    def get(cls, eid: EID) -> Entity:
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(), eid),
        )

        entity_classes = (*Entity.get_subclasses(), Entity)
        result = Response[Union[entity_classes]](**response.json())  # type: ignore

        return cast(ResponseData, result.data).body

    @classmethod
    def get_list(
        cls,
        include_types: List[EntityType] = None,
        exclude_types: List[EntityType] = None,
        include_options: List[IncludeOptions] = None,
        modified_after: datetime = None,
        modified_before: datetime = None,
    ) -> Generator[Entity, None, None]:
        api = SignalsNotebookApi.get_default_api()

        params = {}
        if include_types:
            params['includeTypes'] = ','.join(include_types)
        if exclude_types:
            params['excludeTypes'] = ','.join(exclude_types)
        if include_options:
            params['includeOptions'] = ','.join(include_options)
        if modified_after:
            params['start'] = modified_after.isoformat()
        if modified_before:
            params['end'] = modified_before.isoformat()

        entity_classes = (*Entity.get_subclasses(), Entity)

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(),),
            params=params or None,
        )

        result = Response[Union[entity_classes]](**response.json())  # type: ignore
        yield from [cast(ResponseData, item).body for item in result.data]

        while result.links.next:
            response = api.call(
                method='GET',
                path=result.links.next,
            )

            result = Response[Union[entity_classes]](**response.json())  # type: ignore
            yield from [cast(ResponseData, item).body for item in result.data]

    @classmethod
    def refresh(cls, entity: Entity) -> None:
        refreshed_entity = cls.get(entity.eid)
        for field in entity.__fields__.values():
            if field.field_info.allow_mutation:
                new_value = getattr(refreshed_entity, field.name)
                setattr(entity, field.name, new_value)

    @classmethod
    def delete(cls, eid: EID, digest: str = None, force: bool = True) -> None:
        api = SignalsNotebookApi.get_default_api()

        api.call(
            method='DELETE',
            path=(cls._get_endpoint(), eid),
            params={
                'digest': digest,
                'force': json.dumps(force),
            },
        )
