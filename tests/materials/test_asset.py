import arrow
import pytest

from signals_notebook.materials import Batch
from signals_notebook.types import MaterialType, MID, ObjectType


@pytest.fixture()
def get_response_object(mocker):
    def _f(response):
        mock = mocker.Mock()
        mock.json.return_value = response
        return mock

    return _f


def test_get_batches__one_page(api_mock, asset_factory, mid_factory):
    asset = asset_factory()
    eid1 = mid_factory(type=MaterialType.BATCH)
    eid2 = mid_factory(type=MaterialType.BATCH)
    response = {
        'links': {'self': f'https://example.com/{eid1}'},
        'data': [
            {
                'type': ObjectType.MATERIAL,
                'id': eid1,
                'links': {'self': f'https://example.com/{eid1}'},
                'attributes': {
                    'assetTypeId': asset.asset_type_id,
                    'library': asset.library_name,
                    'eid': eid1,
                    'name': 'My lot 1',
                    'description': 'test description 1',
                    'type': MaterialType.BATCH,
                    'createdAt': '2020-09-06T03:12:35.129Z',
                    'editedAt': '2020-09-06T15:22:47.309Z',
                    'digest': '53263456',
                },
            },
            {
                'type': ObjectType.MATERIAL,
                'id': eid2,
                'links': {'self': f'https://example.com/{eid2}'},
                'attributes': {
                    'assetTypeId': asset.asset_type_id,
                    'library': asset.library_name,
                    'eid': eid2,
                    'name': 'My lot 2',
                    'description': 'test description 2',
                    'type': MaterialType.BATCH,
                    'createdAt': '2021-09-06T03:12:35.129Z',
                    'editedAt': '2021-09-06T15:22:47.309Z',
                    'digest': '34563546',
                },
            },
        ],
    }
    api_mock.call.return_value.json.return_value = response

    result_generator = asset.get_batches()

    api_mock.call.assert_not_called()

    result = list(result_generator)

    api_mock.call.assert_called_once_with(
        method='GET',
        path=('materials', asset.library_name, 'assets', asset.name, 'batches'),
    )

    for item, raw_item in zip(result, response['data']):
        assert isinstance(item, Batch)
        assert item.asset_type_id == asset.asset_type_id
        assert item.library_name == asset.library_name
        assert item.eid == raw_item['id']
        assert item.digest == raw_item['attributes']['digest']
        assert item.name == raw_item['attributes']['name']
        assert item.description == raw_item['attributes']['description']
        assert item.created_at == arrow.get(raw_item['attributes']['createdAt'])
        assert item.edited_at == arrow.get(raw_item['attributes']['editedAt'])


def test_get_batches__several_pages(api_mock, mocker, get_response_object, asset_factory, mid_factory):
    asset = asset_factory()
    eid1 = mid_factory(type=MaterialType.BATCH)
    eid2 = mid_factory(type=MaterialType.BATCH)
    response1 = {
        'links': {
            'self': (
                f'https://example.com/materials/{asset.library_name}/'
                'assets/{asset.name}/batches?page[offset]=0&page[limit]=20'
            ),
            'next': (
                f'https://example.com/materials/{asset.library_name}/'
                'assets/{asset.name}/batches?page[offset]=20&page[limit]=20'
            ),
        },
        'data': [
            {
                'type': ObjectType.MATERIAL,
                'id': eid1,
                'links': {'self': f'https://example.com/{eid1}'},
                'attributes': {
                    'assetTypeId': asset.asset_type_id,
                    'library': asset.library_name,
                    'eid': eid1,
                    'name': 'My lot 1',
                    'description': 'test description 1',
                    'type': MaterialType.BATCH,
                    'createdAt': '2020-09-06T03:12:35.129Z',
                    'editedAt': '2020-09-06T15:22:47.309Z',
                    'digest': '53263456',
                },
            },
        ],
    }
    response2 = {
        'links': {
            'prev': (
                f'https://example.com/materials/{asset.library_name}/'
                'assets/{asset.name}/batches?page[offset]=0&page[limit]=20'
            ),
            'self': (
                f'https://example.com/materials/{asset.library_name}/'
                'assets/{asset.name}/batches?page[offset]=20&page[limit]=20'
            ),
        },
        'data': [
            {
                'type': ObjectType.MATERIAL,
                'id': eid2,
                'links': {'self': f'https://example.com/{eid2}'},
                'attributes': {
                    'assetTypeId': asset.asset_type_id,
                    'library': asset.library_name,
                    'eid': eid2,
                    'name': 'My lot 2',
                    'description': 'test description 2',
                    'type': MaterialType.BATCH,
                    'createdAt': '2021-09-06T03:12:35.129Z',
                    'editedAt': '2021-09-06T15:22:47.309Z',
                    'digest': '34563546',
                },
            },
        ],
    }

    api_mock.call.side_effect = [get_response_object(response1), get_response_object(response2)]

    result_generator = asset.get_batches()

    api_mock.call.assert_not_called()

    result = list(result_generator)

    api_mock.call.assert_has_calls(
        [
            mocker.call(
                method='GET',
                path=('materials', asset.library_name, 'assets', asset.name, 'batches'),
            ),
            mocker.call(
                method='GET',
                path=response1['links']['next'],
            ),
        ]
    )

    for item, raw_item in zip(result, [*response1['data'], *response2['data']]):
        assert isinstance(item, Batch)
        assert item.asset_type_id == asset.asset_type_id
        assert item.library_name == asset.library_name
        assert item.eid == raw_item['id']
        assert item.digest == raw_item['attributes']['digest']
        assert item.name == raw_item['attributes']['name']
        assert item.description == raw_item['attributes']['description']
        assert item.created_at == arrow.get(raw_item['attributes']['createdAt'])
        assert item.edited_at == arrow.get(raw_item['attributes']['editedAt'])


def test_library_property(asset_factory, library_factory, mocker):
    library = library_factory()
    asset = asset_factory()

    mock = mocker.patch('signals_notebook.materials.material_store.MaterialStore')
    mock.get.return_value = library

    result = asset.library

    assert result == library
    mock.get.assert_called_once_with(MID(f'{MaterialType.LIBRARY}:{asset.asset_type_id}'))

