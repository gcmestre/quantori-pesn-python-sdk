import logging
from typing import cast, Generator, Optional

from pydantic import BaseModel
from pydantic.fields import PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import AttrID, ObjectType, Response, ResponseData

log = logging.getLogger(__name__)


class AttributeOption(BaseModel):
    id: Optional[str]
    key: str
    value: str


class AttributeOptionResponse(Response[AttributeOption]):
    pass


class Attribute(BaseModel):
    type: str
    id: AttrID
    name: str
    _options: list[AttributeOption] = PrivateAttr(default=[])

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'attributes'

    @classmethod
    def get(cls, id: AttrID) -> 'Attribute':
        """Get Attribute object by id

        Args:
            id: AttrID

        Returns:
            Attribute
        """
        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(), id),
        )

        result = AttributeResponse(**response.json())
        log.debug('Get Attribute with ID: %s', id)

        return cast(ResponseData, result.data).body

    @classmethod
    def get_list(
        cls,
    ) -> Generator['Attribute', None, None]:
        """Get all Attributes.

        Returns:
           list of available Attributes
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Get List of Attributes')

        response = api.call(
            method='GET',
            path=(cls._get_endpoint(),),
        )
        result = AttributeResponse(**response.json())

        yield from [cast(ResponseData, item).body for item in result.data]

        while result.links and result.links.next:
            response = api.call(
                method='GET',
                path=result.links.next,
            )

            result = AttributeResponse(**response.json())
            yield from [cast(ResponseData, item).body for item in result.data]

        log.debug('List of Attributes was got successfully.')

    @classmethod
    def create(
        cls,
        name: str,
        type: str,
        description: str,
        options: Optional[list[AttributeOption]] = None,
    ) -> 'Attribute':
        """Create new Attribute

        Args:
            name: name of new Attribute
            type: type of new Attribute
            description: description of new Attribute
            options: list of available options for created Attribute

        Returns:
            Attribute
        """
        api = SignalsNotebookApi.get_default_api()

        log.debug('Create Attribute: %s...', cls.__name__)

        response = api.call(
            method='POST',
            path=(cls._get_endpoint(),),
            json={
                'data': {
                    'type': ObjectType.ATTRIBUTE,
                    'attributes': {
                        'name': name,
                        'type': type,
                        'description': description,
                        'options': [option.id for option in options] if options else [],
                    },
                }
            },
        )
        log.debug('User: %s was created.', cls.__name__)

        result = AttributeResponse(**response.json())
        return cast(ResponseData, result.data).body

    def save(self) -> None:
        """Update content of Attribute by id.

        Returns:

        """
        # TODO: Update options doesn't work. Check the reason of second api to update options
        api = SignalsNotebookApi.get_default_api()
        api.call(
            method='PATCH',
            path=(
                self._get_endpoint(),
                self.id,
            ),
            json={
                'data': {
                    'type': ObjectType.ATTRIBUTE,
                    'id': self.id,
                    'attributes': self.dict(
                        by_alias=True,
                        include={
                            'options',
                        },
                    )
                },
            },
        )
        log.debug('Attribute: %s was saved successfully', self.id)

    def delete(self) -> None:
        """Delete an Attribute by id.

        Returns:

        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Disable Attributes: %s...', self.id)

        api.call(
            method='DELETE',
            path=(self._get_endpoint(), self.id),
        )
        log.debug('Attribute: %s was disabled successfully', self.id)

    @property
    def options(self) -> list[AttributeOption]:
        """Get Attribute options

        Returns:
            list[AttributeOption]
        """
        if self._options:
            return self._options

        api = SignalsNotebookApi.get_default_api()

        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.id, 'options'),
        )

        result = AttributeOptionResponse(**response.json())
        log.debug('Get Attribute with ID: %s', id)

        return [cast(ResponseData, item).body for item in result.data]

    def __call__(self, value: str) -> str:
        if value not in self.options:
            log.exception('Incorrect attribute value')
            raise ValueError('Incorrect attribute value')

        return value


class AttributeResponse(Response[Attribute]):
    pass
