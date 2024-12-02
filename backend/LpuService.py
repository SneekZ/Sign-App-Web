from pathlib import Path
import json


class LpuService:
    def __init__(self):
        self._default_folder_path = "lpu_data/"
        self._lpu_data_folder = Path(self._default_folder_path)

    def get_names(self):
        data = []
        for filepath in self._lpu_data_folder.iterdir():
            if filepath.is_file():
                with open(filepath, 'r') as file:
                    lpu_data = json.load(file)
                    host, name = lpu_data["host"], lpu_data["name"]
                    data.append({host: name})
        return data

    def get_lpu_data(self, host):
        data = []
        for filepath in self._lpu_data_folder.iterdir():
            if filepath.is_file():
                with open(filepath, 'r') as file:
                    lpu_data = json.load(file)
                    if lpu_data["host"] == host:
                        break
        return data

