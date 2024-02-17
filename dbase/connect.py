import logging
import json
import psycopg2
from typing import Dict, Set

from dbase.params import params

from chat.role import role

# Configure logging
logging.basicConfig(level=logging.WARNING,
                    filename="../yabotlogs/connect.log",
                    format="%(asctime)s %(levelname)s %(message)s",
                    filemode="w")


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
        temp = dbase.query(f'''SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table}'
               and table_catalog='{db}'
               and table_schema='{schema}'
            ORDER BY ordinal_position ''')
        return tuple([e[0] for e in temp])


def getUserParameters(user_id: int,
                      params=params) -> Dict | None:

    with postgresConn(params.getParams()) as dbase:
        values = dbase.query(f"""SELECT *
        FROM db.public.user
        where user_id = {user_id}
        """)

        columns = getTableColumns('user', 'db')

    if values and columns:
        return dict(zip(columns, values[0]))


def getModelName(model_id: int, params=params) -> str:
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query(f"""SELECT model_name
            FROM db.public.model
            where model_id = {model_id}
            """)

        return values[0][0]


def getContextName(context_id: int) -> str:
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query(f"""SELECT context_name
            FROM db.public.context
            where context_id = {context_id}
            """)
        # columns = getTableColumns('model', 'db')

    if values:
        return values[0][0]


def updateTemperature(temp: float,
                      user_id: int,
                      params=params) -> None:
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


def updateMaxTokens(max_tokens: int,
                    user_id: int,
                    params=params) -> None:
    with postgresConn(params.getParams()) as dbase:
        dbase.cursor.execute(f"""update "user"
            set max_tokens = {max(min(max_tokens, 16384), 0)}
            where user_id={user_id}
            """)


def updateModel(model_id: int,
                user_id: int, params=params) -> None:
    with postgresConn(params.getParams()) as dbase:
        dbase.cursor.execute(f"""update "user"
            set model_id = {model_id}
            where user_id={user_id}
            """)


def registerUser(user_id: int,
                 first_name: str,
                 last_name: str,
                 username: str,
                 params=params) -> None:
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query(f"""SELECT *
            FROM db.public.user
            where user_id = {user_id}
            """)

        if not values:
            try:
                dbase.cursor.execute(f"""
                insert into "user" (user_id, first_name, last_name, username)
                values({user_id}, '{first_name}', '{last_name}', '{username}')
                    """)
            except Exception:
                raise logging.exception("""{user_id=}, {first_name=},
                                     {last_name=},{username=},
                                     {value=s})""", exc_info=True)


def authRequest(user_id: int, params=params) -> bool:
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query(f"""SELECT *
            FROM db.public.user
            where user_id = {user_id}
                and is_admitted = true
            """)
    return len(values) == 1


def listOfModels(params=params) -> Dict | None:
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query("""SELECT *
            FROM db.public.model
            where in_use = true
            """)
        columns = getTableColumns('model', 'db')

    if values and columns:
        return {row[columns.index('model_id')]:
                row[columns.index('model_name')] for row in values}


def listOfContexts(user_id: int, params=params) -> Dict:
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query(f"""SELECT *
            FROM db.public.context
            where user_id = {user_id}
            """)
        columns = getTableColumns('context', 'db')

    if values and columns:
        return {row[columns.index('context_id')]:
                row[columns.index('context_name')] for row in values}
    else:
        return dict()


def deleteContext(context_id: int, params=params):
    with postgresConn(params.getParams()) as dbase:
        dbase.cursor.execute(f"""
            delete from context
            where context_id = {context_id}
            """)


def createContext(context_name: str,
                  context_description: str,
                  user_id: int,
                  params=params):
    lst = [{'role': role.SYSYEM, 'content': context_description.replace("'", "''")}]
    with postgresConn(params.getParams()) as dbase:
        try:
            dbase.cursor.execute(f"""
            insert into context (
                context_name,
                user_id,
                context)
            values (
                '{context_name[:30].replace("'", "''")}',
                {user_id},
                '{json.dumps(lst,ensure_ascii=False).encode('utf8').decode()}'
                )
            """)
        except Exception:
            logging.exception("""{context_name=},
                           {context_description=},
                           {user_id=}""", exc_info=True)


def getContext(context_id: int,
               params=params) -> str:
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query(f"""SELECT context
            FROM db.public.context
            where context_id = {context_id}
            """)

        return values[0][0]


def updateContext(context_id: int,
                  context: str,
                  context_role: role,
                  params=params) -> None:
    lst = [{'role': context_role, 'content': context.replace("'", "''")}]
    with postgresConn(params.getParams()) as dbase:
        dbase.cursor.execute(f"""
        update context
        set context = context::jsonb ||
            '{json.dumps(lst, ensure_ascii=False).encode('utf8').decode()}'::jsonb
        where context_id={context_id}
        """)


def getUserfromContext(context_id: int,
                       params=params) -> None:
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query(f"""SELECT user_id
            FROM db.public.context
            where context_id = {context_id}
            """)
        return values[0][0]


def createChatLog(completion: Dict,
                  params=params) -> None:
    with postgresConn(params.getParams()) as dbase:
        try:
            dbase.cursor.execute(f"""
                insert into chat_log (
                    id,
                    user_name,
                    model_name,
                    datetime,
                    completion_tokens,
                    prompt_tokens,
                    total_tokens,
                    content
                    )
                values (
                    '{completion['id']}',
                    '{completion['user_name']}',--поправить
                    '{completion['model_name']}',
                    {completion['created']},
                    {completion['completion_tokens']},
                    {completion['prompt_tokens']},
                    {completion['total_tokens']},
                    '{completion['content'].replace("'", "''")}')
            """)
        except Exception:
            raise logging.exception('{completion=}', exc_info=True)


def listOfUsers(params=params,
                is_admitted: bool = True):
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query(f'''SELECT *
            FROM db.public."user"
            where is_admitted = {is_admitted}
                and is_admin=False
            ''')

        columns = getTableColumns('user', 'db')

    if values and columns:
        return {row[columns.index('user_id')]:
                row[columns.index('username')] for row in values}
    else:
        return dict()


def setOfAdmins(params=params) -> Set:
    with postgresConn(params.getParams()) as dbase:
        values = dbase.query(f'''SELECT user_id
            FROM db.public."user"
            where is_admin = true
            ''')

    if values:
        return set([v[0] for v in values])
    else:
        return set()


def updateUserAdmission(user_id: int, is_admitted: bool) -> None:
    with postgresConn(params.getParams()) as dbase:
        dbase.cursor.execute(f"""
            update "user"
            set is_admitted = {is_admitted}
            where user_id={user_id}
        """)
