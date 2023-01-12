import psycopg2


class DataBase:
    def __init__(self, host, user, password, db_name):
        self.__connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        self.__connection.autocommit = True
        self.__create_tables()

    def __create_tables(self):
        with self.__connection.cursor() as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS sessions(
                id serial PRIMARY KEY,
                session_id varchar(15) NOT NULL,
                key varchar(100) NOT NULL,
                owner varchar(50) NOT NULL,
                repo varchar(50) NOT NULL);''')

    def create_session(self, session_id, key, owner, repo):
        with self.__connection.cursor() as cursor:
            cursor.execute(f'''INSERT INTO sessions(session_id, key, owner, repo) VALUES(
            '{session_id}',
            '{key}',
            '{owner}',
            '{repo}'
            );''')

    def get_by_session(self, session_id):
        with self.__connection.cursor() as cursor:
            cursor.execute(f'''SELECT key, owner, repo FROM sessions WHERE session_id='{session_id}';''')
            return cursor.fetchone()

    def remove_by_session(self, session_id):
        with self.__connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM sessions WHERE session_id='{session_id}'")


db = DataBase('localhost', 'postgres', 'qwerty', 'restapi')

