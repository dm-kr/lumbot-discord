import aiosqlite
import sqlite3


class DBConnect:
    def __init__(self, db: str = 'DLumBot.db') -> None:
        self.db = db
        self.db_info = {
            'Vasserman': [
                'user_id',
                'exp',
                'vsm_points',
            ]
        }

    def insert(self, table: str, values: tuple[any]) -> None:
        with sqlite3.connect(self.db) as connection:
            if not connection:
                raise ConnectionError('Connection error!')
            if not table in self.db_info.keys():
                raise ValueError('Cannot find table name!')
            if len(values) != len(self.db_info[table]):
                raise ValueError('Incorrect values!')
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO {table} ({", ".join(self.db_info[table])}) \
                              VALUES ({"?" + ", ?" * (len(self.db_info[table]) - 1)})', values)
            connection.commit()

    def update(self, table: str, to_set: str, key: int) -> None:
        with sqlite3.connect(self.db) as connection:
            if not connection:
                raise ConnectionError('Connection error!')
            cursor = connection.cursor()
            cursor.execute(f'UPDATE {table} SET {to_set}\
                              WHERE {self.db_info[table][0]}={key};')
            connection.commit()

    def select(self, request: str) -> sqlite3.Cursor:
        with sqlite3.connect(self.db) as connection:
            if not connection:
                raise ConnectionError('Connection error!')
            cursor = connection.cursor()
            return cursor.execute(request)

