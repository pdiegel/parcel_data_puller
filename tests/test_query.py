import pytest
from pathlib import Path
from parcel_data_puller.query import ParcelQuery
from parcel_data_puller.data_loader import ParcelDataLoader
from config.constants import YAML_CONFIG_PATH
from tests.constants import (
    TEST_COUNTY2,
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
    county_config = data_loader.get_config_for(TEST_COUNTY2)
    url = county_config.get("URL", "")
    field_mapping = data_loader.get_field_mapping_for(TEST_COUNTY2)
    query = ParcelQuery(url, field_mapping)  # type: ignore
    return query


@pytest.fixture
def parcel_query_empty(data_loader: ParcelDataLoader):
    county_config = data_loader.get_config_for(EMPTY_TEST_COUNTY)
    url = county_config.get("URL", "")
    field_mapping = data_loader.get_field_mapping_for(EMPTY_TEST_COUNTY)
    query = ParcelQuery(url, field_mapping)
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

    parcel_data = parcel_query.query()

    assert parcel_data == {}


@patch("requests.get")
def test_http_error(mock_get: MagicMock, parcel_query: ParcelQuery):
    mock_get.side_effect = requests.exceptions.HTTPError("Failed to connect")

    parcel_data = parcel_query.query()

    assert parcel_data == {}


@patch("requests.get")
def test_timeout_error(mock_get: MagicMock, parcel_query: ParcelQuery):
    mock_get.side_effect = requests.exceptions.Timeout("Failed to connect")

    parcel_data = parcel_query.query()

    assert parcel_data == {}


@patch("requests.get")
def test_request_exception(mock_get: MagicMock, parcel_query: ParcelQuery):
    mock_get.side_effect = requests.exceptions.RequestException(
        "Failed to connect"
    )

    parcel_data = parcel_query.query()

    assert parcel_data == {}


@patch("requests.get")
def test_bad_response(mock_get: MagicMock, parcel_query: ParcelQuery):
    mock_get.return_value.status_code = 400

    parcel_data = parcel_query.query()

    assert parcel_data == {}


def test_query(parcel_query: ParcelQuery, parcel_query_empty: ParcelQuery):
    parcel_data = parcel_query.query(where_clause="PARCEL_ID='0113335'")
    assert isinstance(parcel_data, dict)

    parcel_data = parcel_query.query(where_clause=f"PARCEL_ID={1234564566985}")
    assert isinstance(parcel_data, dict)

    parcel_data = parcel_query_empty.query()
    assert isinstance(parcel_data, dict)


def test_process_feature(
    parcel_query_empty: ParcelQuery, feature: Dict[str, Dict[str, str]]
):
    processed_feature = parcel_query_empty.process_feature(feature)
    assert isinstance(processed_feature, dict)
