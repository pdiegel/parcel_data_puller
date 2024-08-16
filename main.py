from parcel_data_puller.aggregator import ParcelDataAggregator

if __name__ == "__main__":
    aggregator = ParcelDataAggregator("config/field_mappings.yaml")
    aggregator.aggregate_for_county("Raleigh")
