import pytest
from pathlib import Path
from parcel_data_puller.processor import ParcelProcessor
from parcel_data_puller.data_loader import ParcelDataLoader
from config.constants import YAML_CONFIG_PATH
from tests.constants import (
    TEST_COUNTY,
    INVALID_COUNTY,
    EMPTY_TEST_COUNTY,
    TEST_REGEX,
)


@pytest.fixture
def data_loader():
    config_path = Path(YAML_CONFIG_PATH)
    data_loader = ParcelDataLoader(config_path)
    return data_loader


@pytest.fixture
def parcel_processor(data_loader: ParcelDataLoader):
    processor = ParcelProcessor(data_loader, TEST_COUNTY)
    return processor


@pytest.fixture
def parcel_processor_invalid(data_loader: ParcelDataLoader):
    processor = ParcelProcessor(data_loader, INVALID_COUNTY)
    return processor


@pytest.fixture
def parcel_processor_empty(data_loader: ParcelDataLoader):
    processor = ParcelProcessor(
        data_loader, EMPTY_TEST_COUNTY, where_clause=f"PARCEL_ID={1234}"
    )
    return processor


def test_process(
    parcel_processor: ParcelProcessor,
    parcel_processor_invalid: ParcelProcessor,
    parcel_processor_empty: ParcelProcessor,
):
    data = parcel_processor.process()
    assert isinstance(data, list)
    assert len(data) > 0
    assert isinstance(data[0], dict)
    assert "PARCEL_ID" in data[0]

    data = parcel_processor_invalid.process()
    assert isinstance(data, list)
    assert len(data) == 0

    data = parcel_processor_empty.process()
    assert isinstance(data, list)
    assert len(data) == 0


def test_process_additional_data(
    parcel_processor: ParcelProcessor,
    parcel_processor_empty: ParcelProcessor,
    parcel_processor_invalid: ParcelProcessor,
):
    data = parcel_processor.process()
    data = parcel_processor.process_additional_data(data)
    assert isinstance(data, list)
    assert len(data) > 0
    assert isinstance(data[0], dict)
    assert "PARCEL_ID" in data[0]
    assert "OWNER_NAME" in data[0]
    assert "LEGAL_DESCRIPTION" in data[0]
    assert "STREET_NAME" in data[0]

    data = parcel_processor_empty.process()
    data = parcel_processor_empty.process_additional_data(data)
    assert isinstance(data, list)
    assert len(data) == 0

    data = parcel_processor_invalid.process()
    data = parcel_processor_invalid.process_additional_data(data)
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_regex_match(parcel_processor: ParcelProcessor):
    source = "1234 Main St."
    match = parcel_processor.get_regex_match(TEST_REGEX, source)
    assert match == "1234"
    assert isinstance(match, str)

    source = "Main St."
    match = parcel_processor.get_regex_match(TEST_REGEX, source)
    assert match == ""
    assert isinstance(match, str)

    source = "1234 Main St."
    match = parcel_processor.get_regex_match(TEST_REGEX, source)
    assert match == "1234"
    assert isinstance(match, str)
