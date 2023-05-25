import psycopg2 as db

class Connection():
    def __init__(self, config: dict):
        try:
            self.__connection = db.connect(**config)
            self.__cursor = self.__connection.cursor()
        except Exception as e:
            print('Connection Fail:')
            raise
            
    @property
    def connection(self):
        return self.__connection

    @property
    def cursor(self):
        return self.__cursor
    
    def __repr__(self) -> str:
        return f"Connection(config='__hide__')"

    def refresh_cursor(self) -> None:
        self.__cursor.close()
        self.__cursor = self.new_cursor()
    
    def new_cursor(self):
        return self.__connection.cursor()

    def commit(self) -> None:
        self.connection.commit()

    def rollback(self) -> None:
        self.connection.rollback()

    def close(self) -> None:
        self.cursor.close()
        self.connection.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self):
        self.close()

    def execute(self, pSQL,  params=None) -> None:
        self.cursor.execute(pSQL, params or ())

    def query(self, pSQL,  params=None) -> list:
        columns = [()]

        self.cursor.execute(pSQL, params or ())
        for desc in self.cursor.description: columns[0] = columns[0] + tuple([desc[0]])

        return columns + self.cursor.fetchall()
    
    @staticmethod
    def printQuery(query: list):
        for value in query: print(value)
