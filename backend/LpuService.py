from pathlib import Path
import json
from Database import Database


class LpuService:
    def __init__(self):
        self._db = Database()

    def get_data(self):
        query = "select id, name from lpudata"
        try:
            data = self._db.run(query)
            if isinstance(data, list):
                return data, True
            else:
                return str(data), False
        except Exception as e:
            return str(e), False

    def get_lpu_data(self, id):
        query = f"select * from lpudata where id = {id}"
        titles = ["id", "name", "host", "port", "user", "password", "dbhost", "dbport", "dbuser", "dbpassword"]
        try:
            data = self._db.run(query)
            if isinstance(data, list):
                if len(data) == 1:
                    data = dict([(titles[i], data[0][i]) for i in range(1, len(titles))])
                    return data, True
                elif len(data) == 0:
                    return "По данному id не найдено ЛПУ", False
            else:
                return str(data), False
        except Exception as e:
            return str(e), False


