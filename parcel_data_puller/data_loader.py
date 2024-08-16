import yaml


class ParcelDataLoader:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_path, "r") as file:
            return yaml.safe_load(file)

    def get_county_url(self, county_name):
        return self.config.get("county_urls", {}).get(county_name)

    def get_field_mappings(self, county_name):
        return self.config.get("field_mappings", {}).get(county_name)
