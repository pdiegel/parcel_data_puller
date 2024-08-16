from .data_loader import ParcelDataLoader
from .processor import ParcelProcessor


class ParcelDataAggregator:
    def __init__(self, config_path):
        self.data_loader = ParcelDataLoader(config_path)

    def aggregate_for_county(self, county_name):
        processor = ParcelProcessor(self.data_loader, county_name)
        results = processor.process()

        if results:
            for result in results:
                print(result)
        else:
            print("No results were returned.")
