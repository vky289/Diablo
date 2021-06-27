import cx_Oracle
import psycopg2
import logging


class postgres_db:

    def __init__(self, args1):
        self.conn = None
        logging.basicConfig(level='ERROR')
        self.log = logging.getLogger(__name__)
        self.params = {'host': args1.host, 'database': args1.sid,
                       'port': args1.port, 'user': args1.username,
                       'password': args1.password, 'connect_timeout': 3}

    def get_connection(self):
        try:
            self.conn = psycopg2.connect(**self.params)
        except (Exception, psycopg2.DatabaseError) as error:
            self.log.error(error)
        return self.conn


class oracle_db:
    cx_Oracle.init_oracle_client(lib_dir='/Users/vsellamuthu/software/instantclient/')

    def __init__(self, args1):
        self.conn = None
        logging.basicConfig(level='ERROR')
        self.log = logging.getLogger(__name__)
        self.params = {'host': args1.host, 'sid': args1.sid,
                       'service': args1.service, 'port': args1.port,
                       'user': args1.username, 'password': args1.password}

    def get_connection(self):
        if self.params.get('service') is None:
            dsn_tns = cx_Oracle.makedsn(self.params.get('host'), self.params.get('port'), self.params.get('sid'))
        else:
            dsn_tns = str(self.params.get('host')) + ":" + str(self.params.get('port')) + '/' + str(self.params.get('service'))
        try:
            self.conn = cx_Oracle.connect(self.params.get('user'), self.params.get('password'), dsn_tns)
        except (Exception, cx_Oracle.DatabaseError) as error:
            self.log.error(error)
        return self.conn
