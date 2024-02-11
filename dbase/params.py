from environs import Env


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


params = postgresParams(host='localhost',
                        user=env('POSTGRES_USER'),
                        password=env('POSTGRES_PASSWORD'))
