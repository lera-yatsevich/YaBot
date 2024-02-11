import psycopg2

from dbase.params import params


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


# p = postgresParams(host='localhost',
#                    user=env('POSTGRES_USER'),
#                    password=env('POSTGRES_PASSWORD'))


def getTableColumns(table, db, schema='public', params=params):
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


def getUserParameters(user_id, params=params):
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

        columns = getTableColumns('user', 'db')

    if values and columns:
        return dict(zip(columns, values[0]))


def getModelName(model_id, params=params):
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
        columns = getTableColumns('model', 'db')

    if values and columns:
        return dict(zip(columns, values[0]))


def getContextName(context_id):
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query(f"""SELECT context_name
            FROM db.public.context
            where context_id = {context_id}
            """)
        # columns = getTableColumns('model', 'db')

    if values:
        return values[0][0]


def updateTemperature(temp, user_id, params=params):
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


def updateMaxTokens(max_tokens, user_id, params=params):
    with postgresConn(params.getParams()) as dbase:
        dbase.cursor.execute(f"""update "user"
            set max_tokens = {max(min(max_tokens, 4000), 0)}
            where user_id={user_id}
            """)


def updateModel(model_id, user_id, params=params):
    with postgresConn(params.getParams()) as dbase:
        dbase.cursor.execute(f"""update "user"
            set model_id = {model_id}
            where user_id={user_id}
            """)


def registerUser(user_id, first_name, last_name, username, params=params):
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query(f"""SELECT *
            FROM db.public.user
            where user_id = {user_id}
            """)

        if not values:
            dbase.cursor.execute(f"""
            insert into "user" (user_id, first_name, last_name, username)
            values({user_id}, '{first_name}', '{last_name}', '{username}')
                """)


def authRequest(user_id, params=params):
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query(f"""SELECT *
            FROM db.public.user
            where user_id = {user_id}
                and is_admitted = true
            """)
    return len(values) == 1


def listOfModels(params=params):
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query("""SELECT *
            FROM db.public.model
            where in_use = true
            """)
        columns = getTableColumns('model', 'db')

    if values and columns:
        return {row[columns.index('model_id')]:
                row[columns.index('model_name')] for row in values}


def listOfContexts(user_id, params=params):
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query(f"""SELECT *
            FROM db.public.context
            where user_id = {user_id}
            """)
        columns = getTableColumns('context', 'db')

    if values and columns:
        return {row[columns.index('context_id')]:
                row[columns.index('context_name')] for row in values}
