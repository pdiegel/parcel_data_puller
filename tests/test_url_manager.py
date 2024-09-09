import pytest
from pathlib import Path
from parcel_data_puller.url_manager import CountyURLManager
from parcel_data_puller.data_loader import ParcelDataLoader
from parcel_data_puller.processor import ParcelProcessor
from config.constants import YAML_CONFIG_PATH
from tests.constants import (
    TEST_COUNTY,
    TEST_COUNTY2,
    INVALID_COUNTY,
    EMPTY_TEST_COUNTY,
)


@pytest.fixture
def data_loader():
    config_path = Path(YAML_CONFIG_PATH)
    data_loader = ParcelDataLoader(config_path)
    return data_loader


@pytest.fixture
def url_manager(data_loader: ParcelDataLoader):
    url_manager = CountyURLManager(data_loader)
    return url_manager


@pytest.fixture
def parcel_processor(data_loader: ParcelDataLoader):
    parcel_processor = ParcelProcessor(data_loader, TEST_COUNTY)
    return parcel_processor


@pytest.fixture
def parcel_processor2(data_loader: ParcelDataLoader):
    parcel_processor = ParcelProcessor(data_loader, TEST_COUNTY2)
    return parcel_processor


def test_get_urls_for_county(
    parcel_processor: ParcelProcessor,
    parcel_processor2: ParcelProcessor,
    url_manager: CountyURLManager,
):
    parcel_data = parcel_processor.process()[0]
    urls = url_manager.get_urls_for_county(
        TEST_COUNTY,
        parcel_data,  # type: ignore
    )
    assert isinstance(urls, dict)
    assert len(urls) > 0

    parcel_data2 = parcel_processor2.process()[0]
    urls = url_manager.get_urls_for_county(
        TEST_COUNTY2,
        parcel_data2,  # type: ignore
    )
    assert isinstance(urls, dict)
    assert len(urls) > 0

    urls = url_manager.get_urls_for_county(
        INVALID_COUNTY,
        parcel_data,  # type: ignore
    )
    assert isinstance(urls, dict)
    assert len(urls) == 0

    urls = url_manager.get_urls_for_county(
        EMPTY_TEST_COUNTY,
        parcel_data,  # type: ignore
    )
    assert isinstance(urls, dict)
    assert len(urls) == 1
