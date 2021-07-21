import cx_Oracle
import psycopg2
import logging
from utils.queries import O_PING_DB, O_PING_DB_2, P_PING_DB


class postgres_db:

    def __init__(self, args1):
        self.conn = None
        logging.basicConfig(level='ERROR')
        self.log = logging.getLogger(__name__)
        self.params = {'host': args1.host, 'database': args1.sid if args1.sid != '' else args1.service,
                       'port': args1.port, 'user': args1.username,
                       'password': args1.password, 'connect_timeout': 3}

    def get_connection(self):
        try:
            self.conn = psycopg2.connect(**self.params)
        except (Exception, psycopg2.DatabaseError) as error:
            self.log.error(error)
        return self.conn

    def ping_db(self):
        conn = None
        try:
            conn = psycopg2.connect(**self.params)
            cur = conn.cursor()
            cur.execute(P_PING_DB)
            if cur.fetchall is not None:
                return cur.fetchall()[0][0], 0
        except (Exception, psycopg2.DatabaseError) as error:
            self.log.error(error)
            return 'Check DB settings! ' + str(error), -1
        finally:
            if conn is not None:
                conn.close()


class oracle_db:
    #cx_Oracle.init_oracle_client(lib_dir='/Users/vsellamuthu/software/instantclient/')

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

    def ping_db(self):
        conn = None
        try:
            if self.params.get('service') is None:
                dsn_tns = cx_Oracle.makedsn(self.params.get('host'), self.params.get('port'), self.params.get('sid'))
            else:
                dsn_tns = str(self.params.get('host')) + ":" + str(self.params.get('port')) + '/' + str(self.params.get('service'))
            conn = cx_Oracle.connect(self.params.get('user'), self.params.get('password'), dsn_tns)
            cur = conn.cursor()
            try:
                rows = cur.execute(O_PING_DB)
            except (Exception, psycopg2.DatabaseError) as e2:
                rows = cur.execute(O_PING_DB_2)
            fetch_rows = rows.fetchall()
            if fetch_rows is not None:
                return fetch_rows[0][0], 0
        except (Exception, psycopg2.DatabaseError) as error:
            self.log.error(error)
            return 'Check DB settings! ' + str(error), -1
        finally:
            if conn is not None:
                conn.close()
