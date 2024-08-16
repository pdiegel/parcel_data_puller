import requests


class ParcelQuery:
    def __init__(self, url, field_map):
        self.url = url
        self.field_map = field_map
        self.result_record_count = 1000

    def query(self):
        params = {
            "where": "1=1",
            "outFields": ",".join(self.field_map.keys()),
            "f": "geojson",
            "resultRecordCount": self.result_record_count,
            "resultOffset": 0,
        }
        all_results = []

        while True:
            response = requests.get(self.url, params=params)
            if response.status_code == 200:
                data = response.json()
                features = data.get("features", [])

                for feature in features:
                    all_results.append(self.process_feature(feature))

                if len(features) < self.result_record_count:
                    break

                params["resultOffset"] += self.result_record_count
            else:
                print(f"Error: {response.status_code}, {response.text}")
                break

        return all_results

    def process_feature(self, feature):
        return {
            self.field_map[original_name]: feature["properties"][original_name]
            for original_name in self.field_map
        }
