import pytest
from pathlib import Path
from parcel_data_puller.data_loader import ParcelDataLoader
from config.constants import YAML_CONFIG_PATH

TEST_COUNTY = "WAKE"
INVALID_COUNTY = "INVALID"


@pytest.fixture
def data_loader():
    config_path = Path(YAML_CONFIG_PATH)
    return ParcelDataLoader(config_path)


def test_load_config(data_loader: ParcelDataLoader):
    config = data_loader.load_config()
    assert isinstance(config, dict)
    assert "COUNTY_URLS" in config


def test_get_county_url(data_loader: ParcelDataLoader):
    url = data_loader.get_county_url(TEST_COUNTY)
    assert (
        url
        == "https://services.arcgis.com/v400IkDOw1ad7Yad/arcgis/rest/services/\
Raleigh_Parcels_Nash_Square/FeatureServer/0/query"
    )

    try:
        url = data_loader.get_county_url(INVALID_COUNTY)
    except ValueError as e:
        assert str(e) == f"County URL for {INVALID_COUNTY} not found."


def test_get_field_mappings(data_loader: ParcelDataLoader):
    field_mappings = data_loader.get_field_mappings(TEST_COUNTY)
    assert isinstance(field_mappings, dict)
    assert "PARCEL_ID" in field_mappings
    assert "OWNER_NAME" in field_mappings

    try:
        field_mappings = data_loader.get_field_mappings(INVALID_COUNTY)
    except ValueError as e:
        assert str(e) == f"Field mappings for {INVALID_COUNTY} not found."


def test_get_county_url_config(data_loader: ParcelDataLoader):
    county_config = data_loader.get_county_url_config(TEST_COUNTY)
    assert isinstance(county_config, dict)
    assert "DEED" in county_config
    # Accessing the first value in the dictionary and checking if it has the
    # key "TEMPLATE" in it
    assert "TEMPLATE" in list(county_config.values())[0]

    try:
        county_config = data_loader.get_county_url_config(INVALID_COUNTY)
    except ValueError as e:
        assert str(e) == f"County config for {INVALID_COUNTY} not found."


def test_get_county_additional_processing_config(data_loader: ParcelDataLoader):
    additional_processing_config = (
        data_loader.get_county_additional_processing_config(TEST_COUNTY)
    )
    assert isinstance(additional_processing_config, dict)
    assert "PLAT_BOOK" in additional_processing_config
    # Accessing the first value in the dictionary and checking if it has the
    # key "REGEX" and "SOURCE" in it
    assert "REGEX" in list(additional_processing_config.values())[0]
    assert "SOURCE" in list(additional_processing_config.values())[0]

    try:
        additional_processing_config = (
            data_loader.get_county_additional_processing_config(INVALID_COUNTY)
        )
    except ValueError as e:
        assert str(e) == f"County config for {INVALID_COUNTY} not found."
