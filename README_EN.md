# DQL DML PostgreSQL Commands with Python
Connects to a server and executes SQL commands directly in *Python*

The modules were created in *Python* and use the ```psycopg2``` library as a base to create an object that can execute these commands in a simpler and more intuitive way.

The base library can be installed by the command ```pip install psycopg2```

## Code example:
Suppose the following table exists in your database:

| col_1 |   col_2  |  col_3  |
| :---: | :------: | :-----: |
| 2     | 'text_2' | 'str_2' |
| 3     | 'text_3' | 'str_3' |

```python
from PgConnection import Connection
from Entity import Entity

# Connection Settings
config = {
    'user': 'user_name',
    'password': 'user_password',
    'host': 'localhost', #or IP
    'port': '5432',
    'database': 'database_name'
}

# Setting the Objects
conn = Connection(config)
table = Entity('table_name', conn)

# Commands
# --------------------------------
table.insert({
	'col_1': 1,
	'col_2': 'text',
	'col_3': 'string'
	}
)

table.update(
	{'col_1': 1}, #where statement
	{'col_2': 'new_text', 'col_3': 'new_string'}
)

table.delete({'col_1: 1})
# --------------------------------

# Return a list with all records
records = table.query('SELECT * FROM table_name')

# Iterate over table with cursor
for record in table:
	print(record) # record is a tuple

# Propertys
table.name    #-> 'table_name'
table.columns #-> list of columns
table.info    #-> dict with the columns and data types
table.len     #-> number of rows that the last execute() produced
len(table)    #-> number of records in table
```