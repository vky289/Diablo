import logging

from psycopg2._psycopg import AsIs
from psycopg2.extras import execute_values as exe_val
import cx_Oracle

import itertools
from utils.enums import DbType
from utils.db_connection import oracle_db, postgres_db
from utils.queries import O_TABLE_EXISTS, P_TABLE_EXISTS
from utils.queries import O_PRIM_KEY_SCRIPT_Q, O_UNI_KEY_SCRIPT_Q, P_PRIM_KEY_SCRIPT_Q
from utils.queries import P_UNI_KEY_SCRIPT_Q, O_PRIM_KEY_ALL_TABLE_Q, P_PRIM_KEY_ALL_TABLE_Q, O_UNI_KEY_ALL_TABLE_Q, P_UNI_KEY_ALL_TABLE_Q
from utils.queries import O_RET_TABLE_ROW_QUERY, P_RET_TABLE_ROW_QUERY, O_COLUMN_NAMES, P_COLUMN_NAMES
from app.core.models import SYSetting


class scrapper:
    def __init__(self, main_db):
        self.log = logging.getLogger(__name__)
        self.main_db = main_db
        self.db_type = main_db.type
        self.conn = None

    def check_table_exists(self, table_name):
        try:
            if self.db_type == DbType.ORACLE:
                if self.conn is None:
                    self.conn = oracle_db(self.main_db).get_connection()
                cur = self.conn.cursor()
                rows = cur.execute(O_TABLE_EXISTS, {'TABLE': table_name})
                fetch_rows = rows.fetchall()
                if fetch_rows is not None and fetch_rows[0][0] > 0:
                    return True
            if self.db_type == DbType.POSTGRES:
                if self.conn is None:
                    self.conn = postgres_db(self.main_db).get_connection()
                cur = self.conn.cursor()
                cur.execute(P_TABLE_EXISTS, (table_name,))
                fetch_rows = cur.fetchall()
                if fetch_rows is not None and fetch_rows[0][0] > 0:
                    return True
            return False
        finally:
            if self.conn is not None:
                self.conn.close()

    def get_connections(self, dbType):
        if dbType == DbType.ORACLE:
            if self.conn is None:
                return oracle_db(self.main_db).get_connection()
            else:
                return self.conn
        if dbType == DbType.POSTGRES:
            if self.conn is None:
                return postgres_db(self.main_db).get_connection()
            else:
                return self.conn

    def get_table_desc_cols(self, SCRIPT_Q):
        result = None
        col_names = None
        try:
            if self.db_type == DbType.ORACLE:
                self.conn = self.get_connections(self.db_type)
                cur = self.conn.cursor()
                rows = cur.execute(SCRIPT_Q, SCH=self.main_db.username)
                col_names = [desc[0] for desc in cur.description]
                result = rows.fetchall()
            if self.db_type == DbType.POSTGRES:
                self.conn = self.get_connections(self.db_type)
                cur = self.conn.cursor()
                cur.execute(SCRIPT_Q, {'SCHEMA': self.main_db.username})
                col_names = [desc[0] for desc in cur.description]
                result = cur.fetchall()
        except IOError as io_error:
            raise io_error
        except Exception as e:
            self.log.error("Error accessing query on DB Type {} - {}".format(str(self.db_type), str(e)))
        finally:
            if self.conn is not None:
                self.conn.close()

        return result, col_names

    def get_table_cols(self, table_name, schema_name, SCRIPT_Q):
        result = None
        col_names = None
        q_args = {'SCH': schema_name}
        try:
            if self.db_type == DbType.ORACLE:
                self.conn = self.get_connections(self.db_type)
                cur = self.conn.cursor()
                rows = cur.execute(SCRIPT_Q, q_args)
                col_names = [desc[0] for desc in cur.description]
                result = rows.fetchall()
            if self.db_type == DbType.POSTGRES:
                self.conn = self.get_connections(self.db_type)
                cur = self.conn.cursor()
                cur.execute(SCRIPT_Q, q_args)
                col_names = [desc[0] for desc in cur.description]
                result = cur.fetchall()
        except IOError as io_error:
            raise io_error
        except Exception as e:
            self.log.error("Error accessing query on DB Type {} - {}".format(str(self.db_type), str(e)))
        finally:
            if self.conn is not None:
                self.conn.close()

        return result, col_names

    def run_query_no_result(self, table_name, SCRIPT_Q):
        q_args = {'TABLE': table_name}
        try:
            if self.db_type == DbType.ORACLE:
                self.conn = self.get_connections(self.db_type)
                cur = self.conn.cursor()
                cur.execute(SCRIPT_Q, q_args)
                self.conn.commit()
            if self.db_type == DbType.POSTGRES:
                self.conn = self.get_connections(self.db_type)
                cur = self.conn.cursor()
                cur.execute(SCRIPT_Q % table_name)
                self.conn.commit()
        except Exception as e:
            self.log.error("Something wrong with the query - DB Type {} - {}".format(str(self.db_type), str(e)))
        finally:
            if self.conn is not None:
                self.conn.close()

    def run_query_with_results(self, schema_name, SCRIPT_Q, q_args=None):
        if q_args is None and schema_name is not None:
            q_args = {'SCH': schema_name}
        if schema_name is not None:
            q_args = dict({'SCH': schema_name}, **q_args)
        try:
            if self.db_type == DbType.ORACLE:
                self.conn = self.get_connections(self.db_type)
                cur = self.conn.cursor()
                rows = cur.execute(SCRIPT_Q, q_args)
                return rows.fetchall()
            if self.db_type == DbType.POSTGRES:
                self.conn = self.get_connections(self.db_type)
                cur = self.conn.cursor()
                cur.execute(SCRIPT_Q , q_args)
                return cur.fetchall()
        except Exception as e:
            self.log.error("Something wrong with the query - DB Type {} - {}".format(str(self.db_type), str(e)))
        finally:
            if self.conn is not None:
                self.conn.close()

    def get_pk_of_all_table(self):
        prim_key = {}
        try:
            if self.db_type == DbType.ORACLE:
                self.conn = self.get_connections(self.db_type)
                cur = self.conn.cursor()
                rows = cur.execute(O_PRIM_KEY_ALL_TABLE_Q.format(SCH="'" + self.main_db.username + "'"))
                fetch_rows = rows.fetchall()
            if self.db_type == DbType.POSTGRES:
                self.conn = self.get_connections(self.db_type)
                cur = self.conn.cursor()
                cur.execute(P_PRIM_KEY_ALL_TABLE_Q, {'SCHEMA': self.main_db.username})
                fetch_rows = cur.fetchall()
            if fetch_rows is not None and len(fetch_rows) > 0:
                for e_row in fetch_rows:
                    prim_key[e_row[1]] = e_row[0]
        except Exception as e:
            self.log.error("Something wrong with the query - DB Type {} - {} - find PK".format(str(self.db_type), str(e)))
        finally:
            if self.conn is not None:
                self.conn.close()
        return prim_key


    def get_pk_of_table(self, table_name, SCRIPT_Q=None):
        prim_key = None
        try:
            if self.db_type == DbType.ORACLE:
                self.conn = self.get_connections(self.db_type)
                cur = self.conn.cursor()
                if SCRIPT_Q is None:
                    SCRIPT_Q = O_PRIM_KEY_SCRIPT_Q
                rows = cur.execute(SCRIPT_Q.format(TAB="'" + table_name + "'"))
                fetch_rows = rows.fetchall()
                if fetch_rows is not None and len(fetch_rows) > 0:
                    prim_key = fetch_rows[0][0]
            if self.db_type == DbType.POSTGRES:
                self.conn = self.get_connections(self.db_type)
                cur = self.conn.cursor()
                if SCRIPT_Q is None:
                    SCRIPT_Q = P_PRIM_KEY_SCRIPT_Q
                cur.execute(SCRIPT_Q % table_name)
                fetch_rows = cur.fetchall()
                if fetch_rows is not None and len(fetch_rows) > 0:
                    prim_key = fetch_rows[0][0]
        except Exception as e:
            self.log.error("Something wrong with the query - DB Type {} - {} - find PK of table {} ".format(str(self.db_type), str(e), str(table_name)))
        finally:
            if self.conn is not None:
                self.conn.close()
        return prim_key

    def get_uk_of_all_table(self):
        ui_dict = {}
        try:
            fetch_rows = None
            if self.db_type == DbType.ORACLE:
                self.conn = self.get_connections(self.db_type)
                cur = self.conn.cursor()
                qqq = O_UNI_KEY_ALL_TABLE_Q.format(SCH=self.main_db.username)
                rows = cur.execute(qqq)
                fetch_rows = rows.fetchall()
            if self.db_type == DbType.POSTGRES:
                self.conn = self.get_connections(self.db_type)
                cur = self.conn.cursor()
                cur.execute(P_UNI_KEY_ALL_TABLE_Q, {'SCHEMA': self.main_db.username})
                fetch_rows = cur.fetchall()
            if fetch_rows is not None and len(fetch_rows) > 0:
                for rows in fetch_rows:
                    if ui_dict.get(rows[1]) is None:
                        ui_dict[rows[1]] = [rows[0]]
                    else:
                        ui_dict[rows[1]] += [rows[0]]
        except Exception as e:
            self.log.error("Something wrong with the query - DB Type {} - {} - find UI".format(str(self.db_type), str(e)))
        finally:
            if self.conn is not None:
                self.conn.close()
        return ui_dict


    def get_uk_of_table(self, table_name, schema_name, SCRIPT_Q=None):
        ui_key = None
        try:
            if self.db_type == DbType.ORACLE:
                self.conn = self.get_connections(self.db_type)
                cur = self.conn.cursor()
                if SCRIPT_Q is None:
                    SCRIPT_Q = O_UNI_KEY_SCRIPT_Q
                qqq = SCRIPT_Q.format(TAB=table_name, SCH=schema_name)
                rows = cur.execute(qqq)
                fetch_rows = rows.fetchall()
                if fetch_rows is not None and len(fetch_rows) > 0:
                    ui_key = set()
                    for rows in fetch_rows:
                        ui_key.add(rows[0])
            if self.db_type == DbType.POSTGRES:
                self.conn = self.get_connections(self.db_type)
                cur = self.conn.cursor()
                if SCRIPT_Q is None:
                    SCRIPT_Q = P_UNI_KEY_SCRIPT_Q
                cur.execute(SCRIPT_Q % table_name)
                fetch_rows = cur.fetchall()
                if fetch_rows is not None and len(fetch_rows) > 0:
                    ui_key = set()
                    for rows in fetch_rows:
                        ui_key.add(rows[0])
        except Exception as e:
            self.log.error("Something wrong with the query - DB Type {} - {} - find UI".format(str(self.db_type), str(e)))
        finally:
            if self.conn is not None:
                self.conn.close()
        return ui_key

    def prepare_stmt(self, rows, values):
        col_to_avoid = ['ROW_NUM']
        try:
            cols = SYSetting.objects.get(name="COL_TO_AVOID")
            c_to_a = cols.value
            for i in c_to_a.split(','):
                if i not in col_to_avoid:
                    col_to_avoid.append(i.strip())
        except SYSetting.DoesNotExist:
            pass
        fin_rows = ''
        fin_set = ()
        i = 0
        for row in rows:
            if row not in col_to_avoid:
                fin_rows += row.replace("'", "") + ","
                if row == 'GEOM':
                    if values[i] is not None:
                        fin_set += (self.construct_geom(values[i]), )
                    else:
                        fin_set += (None, )
                elif row.endswith("_VISIBILITY") or row.endswith("_ENABLED") or row.endswith("_DISABLED"):
                    if values[i] is not None:
                        fin_set += (AsIs('CAST (' + str(values[i]) + " as boolean)"), )
                    else:
                        fin_set += (values[i], )
                else:
                    fin_set += (values[i], )
            i += 1
        if fin_rows.endswith(","):
            fin_rows = fin_rows[0: len(fin_rows) - 1]
        return fin_rows, fin_set


    def dump_clob_object(self, obj):
        return obj.read()


    def dump_geom_object(self, obj):
        if obj.type.iscollection:
            li = []
            for value in obj.aslist():
                if isinstance(value, cx_Oracle.Object):
                    li.append(self.dump_geom_object(value))
                else:
                    li.append(repr(value))
            return li
        else:
            di = dict()
            for attr in obj.type.attributes:
                value = getattr(obj, attr.name)
                if isinstance(value, cx_Oracle.Object):
                    di[attr.name] = self.dump_geom_object(value)
                else:
                    di[attr.name] = repr(value)
            return di

    def crawl_db(self, table_name, table_row_count, pk_col, query=None, upper_bound=0, batch_size=5000, only_ui_pk=False):
        data = []
        col_names = None
        if pk_col is None:
            pk_col = 1
        try:
            cur = None
            if self.conn is None:
                self.conn = self.get_connections(self.db_type)
            cur = self.conn.cursor()

            for lower_bound in range(upper_bound, table_row_count, batch_size):
                if self.db_type == DbType.ORACLE:
                    if query is None:
                        if only_ui_pk:
                            if pk_col is not None and type(pk_col) is set or type(pk_col) is list:
                                query = O_RET_TABLE_ROW_QUERY.replace('aka.*', str(','.join(map('aka.{0}'.format, pk_col))))
                            else:
                                query = O_RET_TABLE_ROW_QUERY.replace('aka.*', 'aka.{0}'.format(pk_col))
                        else:
                            query = O_RET_TABLE_ROW_QUERY
                    qqq = query.format(TAB=table_name)
                    if type(pk_col) is set:
                        args = [str(','.join(pk_col)), str(','.join(pk_col)), lower_bound, lower_bound + batch_size - 1]
                    else:
                        args = [pk_col, pk_col, lower_bound,  lower_bound + batch_size - 1]
                    rows = cur.execute(qqq, args)
                else:
                    if query is None:
                        if only_ui_pk:
                            if pk_col is not None and type(pk_col) is set or type(pk_col) is list:
                                query = P_RET_TABLE_ROW_QUERY.replace('aka.*', str(','.join(map('aka.{0}'.format, pk_col))))
                            else:
                                query = P_RET_TABLE_ROW_QUERY.replace('aka.*', 'aka.{0}'.format(pk_col))
                        else:
                            query = P_RET_TABLE_ROW_QUERY
                    if type(pk_col) is set:
                        args = (str(','.join(pk_col)), table_name, str(','.join(pk_col)), lower_bound, lower_bound + batch_size - 1, )
                    else:
                        args = (pk_col, table_name, pk_col, lower_bound,  lower_bound + batch_size - 1, )
                    cur.execute(query % args)
                    rows = cur
                if col_names is None:
                    col_names = [desc[0].upper() for desc in cur.description]
                for row in rows.fetchall():
                    tt = tuple()
                    for rr in row:
                        if isinstance(rr, cx_Oracle.Object):
                            tt += (self.dump_geom_object(rr), )
                        elif isinstance(rr, cx_Oracle.LOB):
                            tt += (self.dump_clob_object(rr), )
                        else:
                            tt += (rr, )
                    data.append(tt)
        except Exception as ee:
            self.log.error("Error = {}".format(str(ee)))
        finally:
            if self.conn is not None:
                self.conn.close()
        return data, col_names

    def insert_row(self, table_name, list_values, col_names, row_count=None, commit_each=False):
        commit_interval = 1
        try:
            cols = SYSetting.objects.get(name="COMMIT_INTERVAL")
            commit_interval = cols.value
        except SYSetting.DoesNotExist:
            pass
        err_rec = 0
        cont = itertools.count()
        q_tuple_list = []
        try:
            for lv in list_values:
                cur_cont = next(cont)
                rws, my_tup = self.prepare_stmt(col_names, lv)
                stmt = '''INSERT INTO ''' + table_name + '''(''' + rws + ''') VALUES %s'''
                if commit_each or (cur_cont != 0 and cur_cont % commit_interval == 0):
                    if commit_each:
                        q_tuple_list.append(my_tup)
                    try:
                        if self.db_type == DbType.POSTGRES:
                            if self.conn is None:
                                self.conn = self.get_connections(self.db_type)
                            cur = self.conn.cursor()
                            self.conn.autocommit = True
                            exe_val(cur, stmt, q_tuple_list)
                            # self.conn.commit()
                            q_tuple_list = []
                    except Exception as w:
                        q_tuple_list = []
                        self.log.error("Error in inserting table {}".format(str(w)))
                        self.conn.rollback()
                        if not commit_each:
                            err_rec += (1 * commit_interval)
                else:
                    q_tuple_list.append(my_tup)

        finally:
            try:
                if self.db_type == DbType.POSTGRES:
                    if self.conn is None:
                        self.conn = self.get_connections(self.db_type)
                    cur = self.conn.cursor()
                    exe_val(cur, stmt, q_tuple_list)
                    self.conn.commit()
                    q_tuple_list = []
            except Exception as w:
                self.log.error("Error in inserting table {}".format(str(w)))
                self.conn.rollback()
                if not commit_each:
                    err_rec += (1 * commit_interval)
            self.log.debug("Total Records to insert : {}, Inserted Records {}, "
                           "Error inserting records : {}".format(str(row_count), str(cur_cont), str(err_rec)))
            if self.conn is not None:
                self.conn.close()
            return cur_cont, err_rec


    def construct_geom(self, raw_object):
        if raw_object is None or len(raw_object) == 0:
            return
        else:
            if len(raw_object) > 0 and raw_object.get('SDO_GTYPE') == '4001':
                sdo_POINT = raw_object.get('SDO_POINT')
                big_list = ()
                if sdo_POINT:
                    for s_o in sdo_POINT:
                        try:
                            values = float(sdo_POINT[s_o])
                        except ValueError:
                            values = 0
                        big_list += (values, )
                    while len(big_list) < 4:
                        big_list += (0, )
                return AsIs("ST_SetSRID(ST_MakePoint({}), 4326)::geometry".format(", ".join(str(p) for p in big_list)))
            elif len(raw_object) > 0 and (raw_object.get('SDO_GTYPE') == '4002'):
                sdo_ordinates = raw_object.get('SDO_ORDINATES')
                if sdo_ordinates:
                    iter = 0
                    big_list = ()
                    small_list = []
                    for s_o in sdo_ordinates:
                        try:
                            values = float(s_o)
                        except ValueError:
                            pass
                        iter += 1
                        if iter % 4 == 0:
                            small_list.append(values)
                            big_list += (' '.join(str(p) for p in small_list), )
                            small_list = []
                        else:
                            small_list.append(values)
                return AsIs("ST_GeomFromText('LINESTRINGZM ({})', 4326)::geometry".format(", ".join(big_list)))
            # elif len(raw_object) > 0 and raw_object.get('SDO_GTYPE') == '4006':
            #     sdo_ordinates = raw_object.get('SDO_ORDINATES')
            #     if sdo_ordinates:
            #         iter = 0
            #         bigger_list = []
            #         big_list = ()
            #         small_list = []
            #         for s_o in sdo_ordinates:
            #             try:
            #                 values = float(s_o)
            #             except ValueError:
            #                 pass
            #             iter += 1
            #             if iter % 4 == 0:
            #                 small_list.append(values)
            #                 big_list += (' '.join(str(p) for p in small_list), )
            #                 if iter % 4 == 0:
            #                     bigger_list.append(big_list)
            #                     big_list = ()
            #                 small_list = []
            #             else:
            #                 small_list.append(values)
            #     val = AsIs("ST_GeomFromText('MULTILINESTRING ({})', 4326)::geometry".format(", ".join(tuple(bigger_list))))
            #     return None
            else:
                self.log.info("Unable to handle SDO_GTYPE {}", raw_object.get('SDO_GTYPE'))
                return None