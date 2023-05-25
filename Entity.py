from psycopg2.sql import SQL, Identifier
from warnings import warn
from typing import Union, List

from PgConnection import Connection


class Entity():
    def __init__(self, name: str, connection: Connection):  
        self.__connection = connection
        self.__name = str(name)

        # Checking if Entity Exists
        pSQL = "SELECT %s IN (SELECT table_name FROM information_schema.tables)"
        entity_exist = self.__connection.query(pSQL, (self.__name, ))[1][0]
        if not entity_exist:
            info = f"Entity '{self.name}' does not exist for this connection in the database"
            raise NameError(info)

        # Getting Information About Columns and Data Types
        pSQL = "SELECT column_name, data_type FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N%s"
        self.__info = self.__connection.query(pSQL, (self.__name, ))
        self.__info = dict(self.__info)

        if 'column_name' in self.__info.keys(): del self.__info['column_name']
        self.__connection.refresh_cursor()

    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def columns(self) -> list:
        return list(self.__info.keys())

    @property
    def info(self) -> dict:
        return self.__info
    
    @property
    def connection(self):
        return self.__connection
    
    @property
    def last_execute_len(self) -> int:
        """ Specifies the number of rows that the last execute() produced """
        return self.__connection.cursor.rowcount
        
    @property
    def len(self) -> int:
        """ Specifies the number of rows that the last execute() produced.
            Same as last_execute_len """
        return self.__connection.cursor.rowcount

    def __len__(self) -> int:
        pSQL = f"SELECT * FROM {self.name}"
        new_cursor = self.connection.new_cursor()
        new_cursor.execute(pSQL)
        output = new_cursor.rowcount
        
        new_cursor.close()
        del new_cursor
        
        return output
    
    def __str__(self) -> str:
        columns = str(self.columns).replace('[', '').replace(']', '')
        columns = columns.replace("'","")
        return f"{self.name}({columns})"
    
    def __repr__(self) -> str:
        return f"Entity(name={self.__name}, connection='__hide__')"

    def __iter__(self):
        pSQL = f"SELECT * FROM {self.name}"
        self.__rowcount = len(self)
        self.__allRows = self.connection.new_cursor()
        self.__allRows.execute(pSQL)
        return self

    def __next__(self):
        output = self.__allRows.fetchone()
        if output != None: return output
        else:
            del self.__rowcount, self.__allRows
            raise StopIteration
        
    def get_table(self) -> List[tuple]:
        """ Return a list of tuples.
            The first one is the column names """
        
        pSQL = f"SELECT * FROM {self.name}"
        return self.query(pSQL)

    def insert(self, args: dict) -> bool:
        fields = {}
        for key in args.keys():
            fields[key] = Identifier(key)
        
        values = len(args) * '%s,'
        values = values[:-1]
        
        pSQL = SQL("INSERT INTO {table} ({fields}) VALUES (" + values + ")").format(
            table=Identifier(self.name),
            fields=SQL(',').join(list(fields.values()))
        )
        
        try:
            self.connection.execute(pSQL, list(args.values()))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print("Record Insert Error:", e)
            info = "Record not inserted. The transaction has been rolled back"
            warn(info, stacklevel=2)
            return False
        
        return True

    def delete(self, identifier: dict) -> bool:
        pk_name = list(identifier.keys())[0]
        pk = list(identifier.values())[0]

        if len(identifier) != 1: pk_name = ''

        pSQL = f"DELETE FROM {self.name} WHERE {pk_name} = %s"
        
        try:
            # Checking if the record exists in the entity
            sql = f'SELECT %s IN (SELECT {pk_name} FROM {self.name})'
            recodExist = self.connection.query(sql, (pk, ))[0][0]
            if not recodExist:
                info = "Record not found to delete"
                raise Exception(info)
            
            # Deleting the record
            self.connection.execute(pSQL, (pk,))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print("Record Delete Error:", e)
            info = "Record not deleted. The transaction has been rolled back"
            warn(info, stacklevel=2)
            return False
        
        return True
            
    def update(self, identifier: dict, args: dict) -> bool:
        pk_name = list(identifier.keys())[0]
        pk = list(identifier.values())[0]

        if len(identifier) != 1: pk_name = ''

        values = ''
        for key in args.keys():
            values += str(key) + " = %s, "
        values = values[:-2]
        
        pSQL = f"UPDATE {self.name} SET {values} WHERE {pk_name} = %s"
        try:
            self.connection.execute(pSQL, list(args.values()) + [pk])
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print("Record Update Error:", e)
            info = "Record not updated. The transaction has been rolled back"
            warn(info, stacklevel=2)
            return False
    
        return True

    def query(self, SQL: str) -> Union[List[tuple], bool]:
        """ Return a list of tuples.
            The first one is the column names """
        
        if self.name not in SQL:
            info = f"Entity '{self.name}' does not influence the query"
            raise Exception(info)
        try:
            return self.connection.query(SQL)
        except Exception as e:
            self.connection.rollback()
            print("Query Error:", e)
            return False
