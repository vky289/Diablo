import logging

from utils.enums import DbType, DBObject
from utils.script_scrapper import scrapper
from app.dbs.models import DBTableCompare, DBCompare, DBTableColumnCompare, DBObjectCompare, DBObjectFKCompare
from utils.queries import O_ROW_COUNT, P_ROW_COUNT, O_COLUMN_NAMES, P_COLUMN_NAMES, O_VW_SCRIPT_Q, P_VW_SCRIPT_Q, O_IND_SCRIPT_Q, \
    P_IND_SCRIPT_Q, O_SEQ_SCRIPT_Q, P_SEQ_SCRIPT_Q, \
    O_TRIG_SCRIPT_Q, P_TRIG_SCRIPT_Q
from utils.queries import O_FK_LIST, P_FK_LIST
from utils.common_func import send_notification


class any_db:
    def __init__(self, user, src_db, dst_db, compare_db):
        self.user = user
        self.log = logging.getLogger(__name__)
        self.src_db = src_db
        self.dst_db = dst_db
        self.src_db_type = self.src_db.type
        self.dst_db_type = self.dst_db.type
        self.compare_db = compare_db


    @staticmethod
    def get_it_rows(set_of_values):
        fin_set = set()
        fin_dict = dict()
        if set_of_values:
            for s_o_v in set_of_values:
                if isinstance(s_o_v, str) or isinstance(s_o_v, int) or isinstance(s_o_v, float) or isinstance(s_o_v, tuple):
                    fin_set.add(s_o_v[0])
                    if len(s_o_v) == 2:
                        fin_dict[s_o_v[0]] = s_o_v[1]
                    if len(s_o_v) > 2:
                        fin_dict[s_o_v[0]] = s_o_v[1:]
        return sorted(fin_set), fin_dict

    @staticmethod
    def get_it_col_datatype(set_of_values):
        fin_set = set()
        fin_dict = dict()
        if set_of_values:
            for s_o_v in set_of_values:
                if isinstance(s_o_v, str) or isinstance(s_o_v, int) or isinstance(s_o_v, float) or isinstance(s_o_v, tuple):
                    fin_set.add(s_o_v[0])
                    if not fin_dict.get(s_o_v[0]):
                        fin_dict[s_o_v[0]] = []
                    fin_dict[s_o_v[0]] += [{'column_name' : s_o_v[1], 'data_type': s_o_v[2], 'precision': s_o_v[3]}]
        return sorted(fin_set), fin_dict

    def store_in_db_columns(self, dict2, db_type):
        for o_r in dict2:
            l_c_list = dict2.get(o_r)
            for l_c in l_c_list:
                obj = DBTableColumnCompare()
                obj.table_name = o_r
                obj.compare_dbs = self.compare_db
                obj.type = db_type
                obj.column_name = l_c.get('column_name')
                if l_c.get('column_name') == 'GEOM':
                    try:
                        oob = DBTableCompare.objects.get(table_name=o_r, compare_dbs=self.compare_db)
                        oob.geom = True
                        oob.save()
                    except DBTableCompare.DoesNotExist:
                        pass
                obj.datatype = l_c.get('data_type')
                obj.precision = l_c.get('precision')
                obj.save()


    def store_views(self, result_dict, obj_type):
        for rs in result_dict.keys():
            obj = DBObjectCompare()
            obj.table_name = rs
            obj.compare_dbs = self.compare_db
            obj.type = obj_type
            if result_dict.get(rs).get('src') is not None:
                obj.src_exists = True
            else:
                obj.src_exists = False
            if result_dict.get(rs).get('dst') is not None:
                obj.dst_exists = True
            else:
                obj.dst_exists = False
            obj.save()

    def row_count_db(self):
        try:
            obj1 = DBTableCompare.objects.filter(compare_dbs=self.compare_db)
            obj1.delete()

            if self.src_db_type == DbType.ORACLE:
                src_q_script = O_ROW_COUNT
            else:
                src_q_script = P_ROW_COUNT

            if self.dst_db_type == DbType.ORACLE:
                dst_q_script = O_ROW_COUNT
            else:
                dst_q_script = P_ROW_COUNT

            o_result, o_col_names = scrapper(db_type=self.src_db_type,
                                             main_db=self.src_db).get_table_desc_cols(schema_name=self.src_db.username,
                                                                                                 SCRIPT_Q=src_q_script)
            o_set, o_dict = self.get_it_rows(o_result)

            p_result, p_col_names = scrapper(db_type=self.dst_db_type,
                                             main_db=self.dst_db).get_table_desc_cols(schema_name=self.dst_db.service,
                                                                                      SCRIPT_Q=dst_q_script)
            p_set, p_dict = self.get_it_rows(p_result)

            for o_r in o_set:
                obj = DBTableCompare()
                obj.table_name = o_r
                obj.compare_dbs = self.compare_db
                obj.src_row_count = o_dict.get(o_r)
                obj.dst_row_count = p_dict.get(o_r)
                obj.geom = False
                obj.save()

            send_notification(self.user, "DB {} -> {} table comparison completed".format(self.src_db.name, self.dst_db.name))
        except Exception as e:
            send_notification(self.user, "DB {} -> {} exception occurred during table comparison - {}".format(self.src_db.name, self.dst_db.name, e))

    def fk_db(self):
        try:
            obj = DBObjectFKCompare.objects.filter(compare_dbs=self.compare_db)
            obj.delete()

            if self.src_db_type == DbType.ORACLE:
                src_q_script = O_FK_LIST
            else:
                src_q_script = P_FK_LIST

            if self.dst_db_type == DbType.ORACLE:
                dst_q_script = O_FK_LIST
            else:
                dst_q_script = P_FK_LIST
            o_result, o_col_names = scrapper(db_type=self.src_db_type,
                                             main_db=self.src_db).get_table_desc_cols(schema_name=self.src_db.username,
                                                                                      SCRIPT_Q=src_q_script)
            o_set, o_dict = self.get_it_rows(o_result)

            p_result, p_col_names = scrapper(db_type=self.dst_db_type,
                                             main_db=self.dst_db).get_table_desc_cols(schema_name=self.dst_db.service,
                                                                                      SCRIPT_Q=dst_q_script)
            p_set, p_dict = self.get_it_rows(p_result)

            ent_fk = list(list(o_set) + list(set(p_set)-set(o_set)))

            if ent_fk is not None:
                for ll in ent_fk:
                    obj = DBObjectFKCompare()
                    obj.compare_dbs = self.compare_db
                    obj.const_name = ll
                    obj.src_1_table_name = o_dict.get(ll)[0] if o_dict.get(ll) is not None else None
                    obj.src_1_col_name = o_dict.get(ll)[1] if o_dict.get(ll) is not None else None
                    obj.src_2_table_name = o_dict.get(ll)[2] if o_dict.get(ll) is not None else None
                    obj.src_2_col_name = o_dict.get(ll)[3] if o_dict.get(ll) is not None else None
                    obj.dst_1_table_name = p_dict.get(ll)[0] if p_dict.get(ll) is not None else None
                    obj.dst_1_col_name = p_dict.get(ll)[1] if p_dict.get(ll) is not None else None
                    obj.dst_2_table_name = p_dict.get(ll)[2] if p_dict.get(ll) is not None else None
                    obj.dst_2_col_name = p_dict.get(ll)[3] if p_dict.get(ll) is not None else None
                    obj.src_exists = True if o_dict.get(ll) is not None else None
                    obj.dst_exists = True if p_dict.get(ll) is not None else None
                    obj.save()
            send_notification(self.user, "DB {} -> {} Foreign Key comparison completed".format(self.src_db.name, self.dst_db.name))
        except Exception as e:
            send_notification(self.user, "DB {} -> {} exception occurred during Foreign Key comparison- {}".format(
                self.src_db.name, self.dst_db.name, e))

    def cdata_view(self):
        try:
            self.x_c_data_extract(DBObject.VIEW, O_VW_SCRIPT_Q, P_VW_SCRIPT_Q)
            send_notification(self.user, "DB {} -> {} View comparison completed".format(self.src_db.name, self.dst_db.name))
        except Exception as e:
            send_notification(self.user, "DB {} -> {} exception occurred during View comparison- {}".format(
                self.src_db.name, self.dst_db.name, e))

    def cdata_ind(self):
        try:
            self.x_c_data_extract(DBObject.INDEX, O_IND_SCRIPT_Q, P_IND_SCRIPT_Q)
            send_notification(self.user, "DB {} -> {} Index comparison completed".format(self.src_db.name, self.dst_db.name))
        except Exception as e:
            send_notification(self.user, "DB {} -> {} exception occurred during Index comparison- {}".format(
                self.src_db.name, self.dst_db.name, e))

    def cdata_seq(self):
        try:
            self.x_c_data_extract(DBObject.SEQUENCE, O_SEQ_SCRIPT_Q, P_SEQ_SCRIPT_Q)
            send_notification(self.user, "DB {} -> {} Sequence comparison completed".format(self.src_db.name, self.dst_db.name))
        except Exception as e:
            send_notification(self.user, "DB {} -> {} exception occurred during Sequence comparison- {}".format(
                self.src_db.name, self.dst_db.name, e))

    def cdata_trig(self):
        try:
            self.x_c_data_extract(DBObject.TRIGGER, O_TRIG_SCRIPT_Q, P_TRIG_SCRIPT_Q)
            send_notification(self.user, "DB {} -> {} Trigger comparison completed".format(self.src_db.name, self.dst_db.name))
        except Exception as e:
            send_notification(self.user, "DB {} -> {} exception occurred during Trigger comparison- {}".format(
                self.src_db.name, self.dst_db.name, e))

    def x_c_data_extract(self, obj_type, o_script_q, p_script_q):
        obj1 = DBObjectCompare.objects.filter(compare_dbs=self.compare_db, type=obj_type)
        obj1.delete()

        if self.src_db_type == DbType.ORACLE:
            src_q_script = o_script_q
        else:
            src_q_script = p_script_q

        if self.dst_db_type == DbType.ORACLE:
            dst_q_script = o_script_q
        else:
            dst_q_script = p_script_q

        o_result1, o_col_names1 = scrapper(db_type=self.src_db_type,
                                           main_db=self.src_db).get_table_desc_cols(schema_name=self.src_db.username,
                                                                                    SCRIPT_Q=src_q_script)
        o_set, o_dict = self.get_it_rows(o_result1)

        p_result2, p_col_names2 = scrapper(db_type=self.dst_db_type,
                                           main_db=self.dst_db).get_table_desc_cols(schema_name=self.dst_db.service,
                                                                                    SCRIPT_Q=dst_q_script)
        p_set, p_dict = self.get_it_rows(p_result2)

        all_names = set(o_set + p_set)

        res_dict = self.compare_names(o_set, p_set, all_names)

        self.store_views(res_dict, obj_type)


    def table_data_type_db(self):
        try:
            obj1 = DBTableColumnCompare.objects.filter(compare_dbs=self.compare_db)
            obj1.delete()

            if self.src_db_type == DbType.ORACLE:
                src_q_script = O_COLUMN_NAMES
            else:
                src_q_script = P_COLUMN_NAMES

            if self.dst_db_type == DbType.ORACLE:
                dst_q_script = O_COLUMN_NAMES
            else:
                dst_q_script = P_COLUMN_NAMES

            o_result1, o_col_names1 = scrapper(db_type=self.src_db_type,
                                               main_db=self.src_db).get_table_desc_cols(schema_name=self.src_db.username,
                                                                                                  SCRIPT_Q=src_q_script)
            o_set2, o_dict2 = self.get_it_col_datatype(o_result1)

            p_result2, p_col_names2 = scrapper(db_type=self.dst_db_type,
                                               main_db=self.dst_db).get_table_desc_cols(schema_name=self.dst_db.service,
                                                                                               SCRIPT_Q=dst_q_script)

            p_set2, p_dict2 = self.get_it_col_datatype(p_result2)


            self.store_in_db_columns(o_dict2, DbType.ORACLE)

            self.store_in_db_columns(p_dict2, DbType.POSTGRES)

            table_com = list(o_dict2.keys()) + list(set(list(p_dict2.keys())) - set(list(o_dict2.keys())))

            self.process_column_mismatch(table_com, o_dict2, p_dict2)
            send_notification(self.user, "DB {} -> {} datatype comparison completed".format(self.src_db.name, self.dst_db.name))
        except Exception as e:
            send_notification(self.user, "DB {} -> {} exception occurred during datatype comparison- {}".format(self.src_db.name, self.dst_db.name,
                                                                                                                e))


    @staticmethod
    def compare_names(oracle_set, post_set, combo_set):
        final_dict = dict()
        for c_s in combo_set:
            final_dict[c_s] = {}
            if c_s in oracle_set:
                final_dict[c_s]['src'] = True
            if c_s in post_set:
                final_dict[c_s]['dst'] = True
        return final_dict

    def process_column_mismatch(self, tabs, o_dict2, p_dict2):
        for tt in tabs:
            ora_table = o_dict2.get(tt)
            pg_table = p_dict2.get(tt)
            if ora_table is not None and pg_table is not None and len(ora_table) != len(pg_table):
                oob = DBTableCompare.objects.get(table_name=tt, compare_dbs=self.compare_db)
                oob.mismatch_in_cols_count = True
                oob.save()
