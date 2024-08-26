import pytest
from pathlib import Path
from parcel_data_puller.aggregator import ParcelDataAggregator
from config.constants import YAML_CONFIG_PATH
from tests.constants import (
    TEST_COUNTY,
    INVALID_COUNTY,
    TEST_PARCEL_ID,
    INVALID_PARCEL_ID,
)


@pytest.fixture
def data_aggregator():
    config_path = Path(YAML_CONFIG_PATH)
    return ParcelDataAggregator(config_path)


def test_aggregate_for_county(data_aggregator: ParcelDataAggregator):
    data = data_aggregator.aggregate_for_county(TEST_COUNTY)
    assert isinstance(data, list)
    assert len(data) > 0
    assert isinstance(data[0], dict)
    assert "PARCEL_ID" in data[0]

    try:
        data_aggregator.aggregate_for_county(INVALID_COUNTY)
    except Exception as e:
        assert f"County URL for {INVALID_COUNTY} not found" in str(e)

    data = data_aggregator.aggregate_for_county(
        TEST_COUNTY, where_clause=f"PARCEL_ID={TEST_PARCEL_ID}", num_records=5
    )
    assert isinstance(data, list)
    assert len(data) == 1
    assert isinstance(data[0], dict)
    assert "PARCEL_ID" in data[0]

    data = data_aggregator.aggregate_for_county(
        TEST_COUNTY,
        where_clause=f"PARCEL_ID={INVALID_PARCEL_ID}",
        num_records=1,
    )
    assert isinstance(data, list)
    assert len(data) == 0
    assert data == []
