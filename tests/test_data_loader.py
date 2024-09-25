import pytest
from pathlib import Path
from parcel_data_puller.data_loader import ParcelDataLoader
from config.constants import YAML_CONFIG_PATH
from tests.constants import (
    TEST_COUNTY,
    SOME_COUNTIES,
    EMPTY_TEST_COUNTY,
)


@pytest.fixture
def data_loader():
    config_path = Path(YAML_CONFIG_PATH)
    return ParcelDataLoader(config_path)


@pytest.fixture
def empty_data_loader():
    config_path = Path("tests/empty.yaml")
    return ParcelDataLoader(config_path)


def test_load_config(data_loader: ParcelDataLoader):
    config = data_loader.load_config()
    assert isinstance(config, dict)
    assert "COUNTY_PROCESSING_ORDER" in config


def test_get_county_names(data_loader: ParcelDataLoader):
    county_names = data_loader.get_county_names()
    for county in SOME_COUNTIES:
        assert county in county_names

    assert "NULL" not in county_names


def test_get_config_for(data_loader: ParcelDataLoader):
    county_config = data_loader.get_config_for(TEST_COUNTY)
    assert isinstance(county_config, dict)
    assert "COUNTY" in county_config
    assert "ORDER" in county_config
    assert "FIELD_MAPPING" in county_config

    county_config = data_loader.get_config_for("NULL")


def test_get_field_mapping_for(
    data_loader: ParcelDataLoader, empty_data_loader: ParcelDataLoader
):
    field_mapping = data_loader.get_field_mapping_for(TEST_COUNTY)
    assert isinstance(field_mapping, dict)
    assert "PARCEL_ID" in field_mapping

    field_mapping = empty_data_loader.get_field_mapping_for(TEST_COUNTY)


def test_get_step_order_for(data_loader: ParcelDataLoader):
    step_order = data_loader.get_step_order_for(TEST_COUNTY)
    assert isinstance(step_order, list)
    assert len(step_order) == 3
    assert "STEP" in step_order[0]
    assert "METHOD" in step_order[0]
    assert "URL" in step_order[0]
    assert "PARAMETERS" in step_order[0]

    missing_step_order = data_loader.get_step_order_for(EMPTY_TEST_COUNTY)
    assert isinstance(missing_step_order, list)
    assert len(missing_step_order) == 0
