from environs import Env
import psycopg2

env = Env()
env.read_env('../env/.env')


class postgresParams():
    def __init__(self,
                 host: str = 'postgres',
                 database: str = 'db',
                 user: str = 'postgres',
                 password: str = 'postgres',
                 port: str = '5432') -> None:
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    def getParams(self):
        return {'host': self.host,
                'database': self.database,
                'port': self.port,
                'user': self.user,
                'password': self.password}


class postgresConn():
    def __init__(self, params):
        self._conn = psycopg2.connect(**params)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()


p = postgresParams(host='localhost',
                   user=env('POSTGRES_USER'),
                   password=env('POSTGRES_PASSWORD'))


def getTableColumns(params, table, db, schema='public'):
    '''
    The Python function getTableColumns retrieves the column '''
    '''names of a specified table from a PostgreSQL database.
    Parameters:
        params: An object containing parameters for establishing '''
    '''a connection to the PostgreSQL database.
        table: The name of the table for which column names are '''
    '''to be retrieved.
        db: The name of the database containing the specified table.
        schema (optional): The schema of the table. Default is 'public'.
    Output:
        The function returns a tuple containing the column names of '''
    '''the specified table retrieved from the database. If the table does '''
    '''not exist or there is an issue with the database connection, '''
    '''it returns an empty tuple.
    '''
    with postgresConn(params.getParams()) as dbase:
        temp = dbase.query(f"""SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table}'
               and table_catalog='{db}'
               and table_schema='{schema}'
            ORDER BY ordinal_position """)
        return tuple([e[0] for e in temp])


def getUserParameters(params, user_id):
    '''
    Retrieves parameters associated with a user from a PostgreSQL database '''
    '''based on the provided user_id.
    Parameters:
        params: An object containing parameters for establishing '''
    '''a connection to the PostgreSQL database.
        user_id: The unique identifier of the user whose parameters '''
    '''are to be retrieved.
    Output:
        If the function successfully retrieves parameters associated '''
    '''with the user and their corresponding columns from the database, '''
    '''it returns a dictionary containing the user's parameters mapped to '''
    '''their corresponding values. Otherwise, it returns None.
    '''
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query(f"""SELECT *
        FROM db.public.user
        where user_id = {user_id}
        """)

        columns = getTableColumns(params, 'user', 'db')
        # print(values, columns)

    if values and columns:
        return dict(zip(columns, values[0]))


def getModelName(params, model_id):
    '''
    Retrieves information about a model from a PostgreSQL '''
    '''database based on the provided model_id
    Parameters:
        params: An object containing parameters for establishing '''
    '''a connection to the PostgreSQL database.
        model_id: The unique identifier of the model whose information '''
    '''is to be retrieved.
    Output:
        If the function successfully retrieves information about '''
    '''the model and its columns from the database, it returns '''
    '''a dictionary containing the model's attributes mapped to their '''
    '''corresponding values. Otherwise, it returns None.
    '''
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query(f"""SELECT *
            FROM db.public.model
            where model_id = {model_id}
            """)
        columns = getTableColumns(params, 'model', 'db')

    if values and columns:
        return dict(zip(columns, values[0]))


def updateTemperature(params, temp, user_id):
    '''
    Updates the temperature for a specified user in a PostgreSQL database.
    Parameters:
        params: An object containing parameters for establishing a '''
    '''connectionto the PostgreSQL database.
        temp: The new temperature value to be updated for the user.
        user_id: The unique identifier of the user whose '''
    '''temperature is to be updated.
    Output:
        This function does not return any value.'''
    '''It directly updates the temperature value for the '''
    '''specified user in the database.'''
    with postgresConn(params.getParams()) as dbase:
        dbase.cursor.execute(f"""update "user"
            set temperature = {max(min(temp, 2), 0)}
            where user_id={user_id}
            """)


def updateMaxTokens(params, max_tokens, user_id):
    with postgresConn(params.getParams()) as dbase:
        dbase.cursor.execute(f"""update "user"
            set max_tokens = {max(min(max_tokens, 4000), 0)}
            where user_id={user_id}
            """)


def updateModel(params, model_id, user_id):
    with postgresConn(params.getParams()) as dbase:
        dbase.cursor.execute(f"""update "user"
            set model_id = {model_id}
            where user_id={user_id}
            """)


def registerUser(params, user_id, first_name, last_name, username):
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query(f"""SELECT *
            FROM db.public.user
            where user_id = {user_id}
            """)
        # columns = getTableColumns(params, 'user', 'db')

        if not values:
            dbase.cursor.execute(f"""
            insert into "user" (user_id, first_name, last_name, username)
            values({user_id}, '{first_name}', '{last_name}', '{username}')
                """)


def authRequest(params, user_id):
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query(f"""SELECT *
            FROM db.public.user
            where user_id = {user_id}
                and is_admitted = true
            """)
    return len(values) == 1

# print(authRequest(p, 204644083)==True)
# print(authRequest(p, 5555))


def listOfModels(params):
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query("""SELECT *
            FROM db.public.model
            where in_use = true
            """)
        columns = getTableColumns(params, 'model', 'db')

    if values and columns:
        return {row[columns.index('model_id')]:
                row[columns.index('model_name')] for row in values}
