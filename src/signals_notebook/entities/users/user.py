import cgi
import logging
from datetime import datetime
from typing import cast, Optional

from pydantic import BaseModel, Field, PrivateAttr

from signals_notebook.api import SignalsNotebookApi
from signals_notebook.common_types import File, ResponseData
from signals_notebook.entities.users.profile import GroupResponse
from signals_notebook.entities.users.user_store import UserResponse

log = logging.getLogger(__name__)


class User(BaseModel):
    is_enabled: Optional[bool] = Field(alias='isEnabled', allow_mutation=False)
    id: str = Field(alias='userId', allow_mutation=False)
    username: str = Field(alias='userName', allow_mutation=False)
    email: str = Field(allow_mutation=False)
    alias: str = Field(alias='alias')
    first_name: str = Field(alias='firstName')
    last_name: str = Field(alias='lastName')
    country: str = Field(alias='country')
    organization: str = Field(alias='organization')
    created_at: datetime = Field(alias='createdAt', allow_mutation=False)
    last_login_at: datetime = Field(alias='lastLoginAt', allow_mutation=False)

    _picture: Optional[File] = PrivateAttr(default=None)

    @classmethod
    def _get_endpoint(cls) -> str:
        return 'users'

    @classmethod
    def create(cls) -> 'User':
        """Create new User

        Returns:
            User
        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Create User: %s...', cls.__name__)

        response = api.call(
            method='POST',
            path=(cls._get_endpoint(),),
            # json=request.dict(exclude_none=True),
        )
        log.debug('User: %s was created.', cls.__name__)

        result = UserResponse(**response.json())
        return cast(ResponseData, result.data).body

    def refresh(self) -> None:
        """Refresh user with new changes values

        Returns:

        """
        from signals_notebook.entities import UserStore

        UserStore.refresh(self)

    def save(self) -> None:
        """Update attributes of a specified user.

        Returns:

        """
        api = SignalsNotebookApi.get_default_api()

        request_body = []
        for field in self.__fields__.values():
            if field.field_info.allow_mutation:
                request_body.append({'attributes': {field.field_info.alias: getattr(self, field.name)}})

        api.call(
            method='PATCH',
            path=(
                self._get_endpoint(),
                self.id,
            ),
            json={
                'data': request_body,
            },
        )

    def delete(self):
        """Make specified user disabled.

        Returns:

        """
        api = SignalsNotebookApi.get_default_api()
        log.debug('Disable User: %s...', self.id)

        api.call(
            method='DELETE',
            path=(self._get_endpoint(), self.id),
        )
        log.debug('User: %s was disabled successfully', self.id)

    @property
    def picture(self) -> Optional[File]:
        if self._picture:
            return self._picture

        api = SignalsNotebookApi.get_default_api()
        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.id, 'picture'),
        )
        if response.content == b'':
            return self._picture

        content_disposition = response.headers.get('content-disposition', '')
        content_type = response.headers.get('content-type')
        _, params = cgi.parse_header(content_disposition)
        file_name = f'{self.first_name}_{self.last_name}.{content_type.split("/")[-1]}'
        self._picture = File(name=file_name, content=response.content, content_type=content_type)
        return self._picture

    def get_system_groups(self):
        api = SignalsNotebookApi.get_default_api()
        response = api.call(
            method='GET',
            path=(self._get_endpoint(), self.id, 'systemGroups'),
        )
        result = GroupResponse(**response.json())
        return [cast(ResponseData, item).body for item in result.data]
