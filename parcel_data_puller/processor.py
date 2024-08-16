from .query import ParcelQuery


class ParcelProcessor:
    def __init__(self, data_loader, county_name):
        self.data_loader = data_loader
        self.county_name = county_name

    def process(self):
        url = self.data_loader.get_county_url(self.county_name)
        field_map = self.data_loader.get_field_mappings(self.county_name)

        if not url or not field_map:
            print(f"Data for {self.county_name} not available.")
            return []

        query = ParcelQuery(url, field_map)
        results = query.query()
        return results
