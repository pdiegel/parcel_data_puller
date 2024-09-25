import pytest
from pathlib import Path
from parcel_data_puller.processor import ParcelProcessor
from parcel_data_puller.data_loader import ParcelDataLoader
from config.constants import YAML_CONFIG_PATH
from tests.constants import (
    TEST_COUNTY,
    TEST_COUNTY2,
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
    processor = ParcelProcessor(data_loader, TEST_COUNTY2)
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


def test_process_step(
    parcel_processor: ParcelProcessor,
    parcel_processor_invalid: ParcelProcessor,
):
    parcel_data = {}
    step_details = parcel_processor.data_loader.get_step_order_for(
        TEST_COUNTY2
    )[0]
    parcel_data = parcel_processor.process_step(
        step_details,
        parcel_data,  # type: ignore
    )

    assert isinstance(parcel_data, dict)
    assert "PARCEL_ID" in parcel_data

    step_details = parcel_processor_invalid.data_loader.get_step_order_for(
        INVALID_COUNTY
    )[0]
    parcel_data = parcel_processor_invalid.process_step(
        step_details,
        parcel_data,  # type: ignore
    )

    assert isinstance(parcel_data, dict)
    assert "PARCEL_ID" not in parcel_data


def test_scrape_gis_api(
    parcel_processor: ParcelProcessor,
):
    parcel_data = {}
    step_details = parcel_processor.data_loader.get_step_order_for(
        INVALID_COUNTY
    )[0]
    parcel_data = parcel_processor.scrape_gis_api(
        step_details,
        parcel_data,  # type: ignore
    )
    assert isinstance(parcel_data, dict)
    assert "PARCEL_ID" not in parcel_data


def test_extract_regex(
    parcel_processor: ParcelProcessor,
):
    parcel_data = {}
    step_details = parcel_processor.data_loader.get_step_order_for(TEST_COUNTY)[
        2
    ]
    parcel_data = parcel_processor.extract_regex(
        step_details,
        parcel_data,  # type: ignore
    )
    assert isinstance(parcel_data, dict)

    parcel_data = {}
    for step_details in parcel_processor.data_loader.get_step_order_for(
        TEST_COUNTY2
    ):
        parcel_data = parcel_processor.process_step(step_details, parcel_data)

    assert isinstance(parcel_data, dict)
    assert "PLAT_BOOK" in parcel_data


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
