import sqlite3


class Database:
    def __init__(self):
        database_filepath = "db/database.db"

        self._connection = sqlite3.connect(database_filepath)

        self._cursor = self._connection.cursor()

    def close(self):
        self._connection.close()

    def commit(self):
        self._connection.commit()

    def run(self, query, params=[]):
        try:
            self._cursor.execute(query, params)
            answer = self._cursor.fetchall()
            return answer
        except Exception as e:
            return e


if __name__ == "__main__":
    # query = """ALTER TABLE lpudata_new RENAME TO lpudata;
    # """
    query = "select * from lpudata"
    # query = "ALTER TABLE lpudata ADD COLUMN database VARCHAR(16)"
    # query = "PRAGMA table_info(lpudata);"
    # query = "DROP TABLE lpudata"
    # query = "delete from lpudata where id = 24"
    db = Database()
    print(*db.run(query), sep="\n")
    db.commit()
    db.close()