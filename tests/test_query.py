import pytest
from pathlib import Path
from parcel_data_puller.query import ParcelQuery
from parcel_data_puller.data_loader import ParcelDataLoader
from config.constants import YAML_CONFIG_PATH
from tests.constants import (
    TEST_COUNTY,
    EMPTY_TEST_COUNTY,
)
from typing import Dict
from unittest.mock import patch, MagicMock
import requests


@pytest.fixture
def data_loader():
    config_path = Path(YAML_CONFIG_PATH)
    return ParcelDataLoader(config_path)


@pytest.fixture
def parcel_query(data_loader: ParcelDataLoader):
    url = data_loader.get_county_url(TEST_COUNTY)
    field_mappings = data_loader.get_field_mappings(TEST_COUNTY)
    query = ParcelQuery(url, field_mappings)
    return query


@pytest.fixture
def parcel_query_empty(data_loader: ParcelDataLoader):
    url = data_loader.get_county_url(EMPTY_TEST_COUNTY)
    field_mappings = data_loader.get_field_mappings(EMPTY_TEST_COUNTY)
    query = ParcelQuery(url, field_mappings)
    return query


@pytest.fixture
def feature():
    return {
        "properties": {
            "REID": 1234,
        },
    }


@patch("requests.get")
def test_fetch_data_connection_error(
    mock_get: MagicMock, parcel_query: ParcelQuery
):
    mock_get.side_effect = requests.exceptions.ConnectionError(
        "Failed to connect"
    )

    result = parcel_query.query()

    assert result == []


@patch("requests.get")
def test_http_error(mock_get: MagicMock, parcel_query: ParcelQuery):
    mock_get.side_effect = requests.exceptions.HTTPError("Failed to connect")

    result = parcel_query.query()

    assert result == []


@patch("requests.get")
def test_timeout_error(mock_get: MagicMock, parcel_query: ParcelQuery):
    mock_get.side_effect = requests.exceptions.Timeout("Failed to connect")

    result = parcel_query.query()

    assert result == []


@patch("requests.get")
def test_request_exception(mock_get: MagicMock, parcel_query: ParcelQuery):
    mock_get.side_effect = requests.exceptions.RequestException(
        "Failed to connect"
    )

    result = parcel_query.query()

    assert result == []


@patch("requests.get")
def test_bad_response(mock_get: MagicMock, parcel_query: ParcelQuery):
    mock_get.return_value.status_code = 400

    result = parcel_query.query()

    assert result == []


def test_query(parcel_query: ParcelQuery, parcel_query_empty: ParcelQuery):
    data = parcel_query.query()
    assert isinstance(data, list)
    assert len(data) > 0
    assert isinstance(data[0], dict)
    assert "PARCEL_ID" in data[0]

    data = parcel_query.query(where_clause=f"PARCEL_ID={1234564566985}")
    assert isinstance(data, list)
    assert len(data) == 0

    data = parcel_query_empty.query()
    assert isinstance(data, list)
    assert len(data) == 0


def test_process_feature(
    parcel_query_empty: ParcelQuery, feature: Dict[str, Dict[str, str]]
):
    processed_feature = parcel_query_empty.process_feature(feature)
    assert isinstance(processed_feature, dict)
    assert "PARCEL_ID" in processed_feature
