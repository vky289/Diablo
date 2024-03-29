import logging

from utils.enums import DbType, DBObject, DBSrcDst
from utils.script_scrapper import scrapper
from app.dbs.models import DBTableCompare, DBTableColumnCompare, DBObjectCompare, DBObjectFKCompare
from utils.queries import O_ROW_COUNT, P_ROW_COUNT2, O_COLUMN_NAMES, P_COLUMN_NAMES, O_VW_SCRIPT_Q, P_VW_SCRIPT_Q, O_IND_SCRIPT_Q, \
    P_IND_SCRIPT_Q, O_SEQ_SCRIPT_Q, P_SEQ_SCRIPT_Q, \
    O_TRIG_SCRIPT_Q, P_TRIG_SCRIPT_Q, P_ALL_TAB_SCRIPT_Q, P_COUNT_ROWS_Q, O_PROC_SCRIPT_Q, P_PROC_SCRIPT_Q
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
                if isinstance(s_o_v, str) or isinstance(s_o_v, int) or isinstance(s_o_v, float) or isinstance(s_o_v, tuple) or isinstance(s_o_v,
                                                                                                                                          list):
                    fin_set.add(s_o_v[0])
                    if len(s_o_v) == 2:
                        fin_dict[s_o_v[0]] = s_o_v[1]
                    if len(s_o_v) > 2:
                        fin_dict[s_o_v[0]] = s_o_v[1:]
        return sorted(fin_set), fin_dict

    @staticmethod
    def get_it_col_datatype(set_of_values, pk=None):
        fin_dict = dict()
        if set_of_values:
            for s_o_v in set_of_values:
                if isinstance(s_o_v, str) or isinstance(s_o_v, int) or isinstance(s_o_v, float) or isinstance(s_o_v, tuple):
                    if not fin_dict.get(s_o_v[0]):
                        fin_dict[s_o_v[0]] = []
                    fin_dict[s_o_v[0]] += [{'column_name': s_o_v[1], 'data_type': s_o_v[2], 'precision': s_o_v[3]}]
        return fin_dict

    def store_in_db_columns(self, dict2, db_type, src_dst):
        for o_r in dict2:
            for l_c in dict2.get(o_r):
                obj = DBTableColumnCompare()
                obj.table_name = o_r
                obj.compare_dbs = self.compare_db
                obj.type = db_type
                column_name = l_c.get('column_name')
                obj.column_name = column_name
                obj.src_dst = src_dst
                obj.datatype = l_c.get('data_type')
                obj.precision = l_c.get('precision')
                if not obj.is_ui:
                    obj.is_ui = False
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
            send_notification(self.user, "DB {} -> {} table comparison started".format(self.src_db.name, self.dst_db.name))
            obj1 = DBTableCompare.objects.filter(compare_dbs=self.compare_db)
            obj1.delete()

            o_result2 = []
            p_result2 = []

            if self.src_db_type == DbType.ORACLE:
                o_result2, o_col_names = scrapper(main_db=self.src_db).get_table_desc_cols(SCRIPT_Q=O_ROW_COUNT)
            if self.src_db_type == DbType.POSTGRES:
                o_result2, o_col_names = scrapper(main_db=self.src_db).get_table_desc_cols(SCRIPT_Q=P_ROW_COUNT2)

            if self.dst_db_type == DbType.ORACLE:
                p_result2, p_col_names = scrapper(main_db=self.dst_db).get_table_desc_cols(SCRIPT_Q=O_ROW_COUNT)
            if self.dst_db_type == DbType.POSTGRES:
                p_result2, p_col_names = scrapper(main_db=self.dst_db).get_table_desc_cols(SCRIPT_Q=P_ROW_COUNT2)


            o_set, o_dict = self.get_it_rows(o_result2)

            p_set, p_dict = self.get_it_rows(p_result2)

            for o_r in o_set:
                obj = DBTableCompare()
                obj.table_name = o_r
                obj.compare_dbs = self.compare_db
                obj.src_row_count = o_dict.get(o_r)
                obj.dst_row_count = p_dict.get(o_r)
                obj.geom = False
                obj.module_id = False
                obj.save()

            send_notification(self.user, "DB {} -> {} table comparison completed".format(self.src_db.name, self.dst_db.name))
        except Exception as e:
            send_notification(self.user, "DB {} -> {} exception occurred during table comparison - {}".format(self.src_db.name, self.dst_db.name, e))

    def fk_db(self):
        try:
            send_notification(self.user, "DB {} -> {} Foreign Key comparison started".format(self.src_db.name, self.dst_db.name))
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
            o_result, o_col_names = scrapper(main_db=self.src_db).get_table_desc_cols(SCRIPT_Q=src_q_script)
            o_set, o_dict = self.get_it_rows(o_result)

            p_result, p_col_names = scrapper(main_db=self.dst_db).get_table_desc_cols(SCRIPT_Q=dst_q_script)
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
            send_notification(self.user, "DB {} -> {} View comparison started".format(self.src_db.name, self.dst_db.name))
            self.x_c_data_extract(DBObject.VIEW, O_VW_SCRIPT_Q, P_VW_SCRIPT_Q)
            send_notification(self.user, "DB {} -> {} View comparison completed".format(self.src_db.name, self.dst_db.name))
        except Exception as e:
            send_notification(self.user, "DB {} -> {} exception occurred during View comparison- {}".format(
                self.src_db.name, self.dst_db.name, e))

    def cdata_ind(self):
        try:
            send_notification(self.user, "DB {} -> {} Index comparison started".format(self.src_db.name, self.dst_db.name))
            self.x_c_data_extract(DBObject.INDEX, O_IND_SCRIPT_Q, P_IND_SCRIPT_Q)
            send_notification(self.user, "DB {} -> {} Index comparison completed".format(self.src_db.name, self.dst_db.name))
        except Exception as e:
            send_notification(self.user, "DB {} -> {} exception occurred during Index comparison- {}".format(
                self.src_db.name, self.dst_db.name, e))

    def cdata_proc(self):
        try:
            send_notification(self.user, "DB {} -> {} Procedure/Function comparison started".format(self.src_db.name, self.dst_db.name))
            self.x_c_data_extract(DBObject.PROCEDURE, O_PROC_SCRIPT_Q, P_PROC_SCRIPT_Q)
            send_notification(self.user, "DB {} -> {} Procedure/Function comparison completed".format(self.src_db.name, self.dst_db.name))
        except Exception as e:
            send_notification(self.user, "DB {} -> {} exception occurred during Procedure/Function comparison- {}".format(
                self.src_db.name, self.dst_db.name, e))

    def cdata_seq(self):
        try:
            send_notification(self.user, "DB {} -> {} Sequence comparison started".format(self.src_db.name, self.dst_db.name))
            self.x_c_data_extract(DBObject.SEQUENCE, O_SEQ_SCRIPT_Q, P_SEQ_SCRIPT_Q)
            send_notification(self.user, "DB {} -> {} Sequence comparison completed".format(self.src_db.name, self.dst_db.name))
        except Exception as e:
            send_notification(self.user, "DB {} -> {} exception occurred during Sequence comparison- {}".format(
                self.src_db.name, self.dst_db.name, e))

    def cdata_trig(self):
        try:
            send_notification(self.user, "DB {} -> {} Trigger comparison started".format(self.src_db.name, self.dst_db.name))
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

        o_result1, o_col_names1 = scrapper(main_db=self.src_db).get_table_desc_cols(SCRIPT_Q=src_q_script)
        o_set, o_dict = self.get_it_rows(o_result1)

        p_result2, p_col_names2 = scrapper(main_db=self.dst_db).get_table_desc_cols(SCRIPT_Q=dst_q_script)
        p_set, p_dict = self.get_it_rows(p_result2)

        all_names = set(o_set + p_set)

        res_dict = self.compare_names(o_set, p_set, all_names)

        self.store_views(res_dict, obj_type)

    def process_pk_ui(self, dbs):

        obj = DBTableCompare.objects.filter(compare_dbs=self.compare_db).values('table_name')

        pk_all = scrapper(main_db=dbs).get_pk_of_all_table()
        ui_all = scrapper(main_db=dbs).get_uk_of_all_table()

        for each_table_dict in obj:
            each_table = each_table_dict.get('table_name')
            pk = pk_all.get(each_table)
            ui = ui_all.get(each_table)

            if ui is not None and type(ui) is list:
                for ppp in ui:
                    try:
                        obj = DBTableColumnCompare.objects.get(compare_dbs=self.compare_db, table_name=each_table, type=dbs.type, column_name=ppp)
                        obj.is_ui = True
                        obj.save()
                    except DBTableColumnCompare.DoesNotExist:
                        pass
            else:
                if pk is not None:
                    try:
                        obj = DBTableColumnCompare.objects.get(compare_dbs=self.compare_db, table_name=each_table, type=dbs.type, column_name=pk[0])
                        obj.is_ui = True
                        obj.save()
                    except DBTableColumnCompare.DoesNotExist:
                        pass

    def table_column_pk_ui_comparision(self):
        try:
            send_notification(self.user, "DB {} -> {} PK/UI comparison started".format(self.src_db.name, self.dst_db.name))

            self.process_pk_ui(self.src_db)

            self.process_pk_ui(self.dst_db)

        except Exception as e:
            send_notification(self.user, "DB {} -> {} exception occurred during PK/UI comparison- {}".format(self.src_db.name,
                                                                                                                    self.dst_db.name,
                                                                                                                e))

    def table_data_type_db(self):
        try:
            send_notification(self.user, "DB {} -> {} datatype comparison started".format(self.src_db.name, self.dst_db.name))
            obj1 = DBTableColumnCompare.objects.filter(compare_dbs=self.compare_db)
            obj1.delete()

            o_result1, o_col_names1, p_result2, p_col_names2 = None, None, None, None

            if self.src_db_type == DbType.ORACLE:
                o_result1, o_col_names1 = scrapper(main_db=self.src_db).get_table_desc_cols(SCRIPT_Q=O_COLUMN_NAMES)
            else:
                o_result1, o_col_names1 = scrapper(main_db=self.src_db).get_table_desc_cols(SCRIPT_Q=P_COLUMN_NAMES)

            if self.dst_db_type == DbType.ORACLE:
                p_result2, p_col_names2 = scrapper(main_db=self.dst_db).get_table_desc_cols(SCRIPT_Q=O_COLUMN_NAMES)
            else:
                p_result2, p_col_names2 = scrapper(main_db=self.dst_db).get_table_desc_cols(SCRIPT_Q=P_COLUMN_NAMES)

            o_dict2 = self.get_it_col_datatype(o_result1)
            p_dict2 = self.get_it_col_datatype(p_result2)

            self.store_in_db_columns(o_dict2, self.src_db.type, DBSrcDst.SRC)

            self.store_in_db_columns(p_dict2, self.dst_db.type, DBSrcDst.DST)

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

    def compare_real_data(self, table_name, table_row_count, pk_col, only_pk_ui=False):

        o_data, o_col_names = scrapper(main_db=self.src_db).crawl_db(table_name, int(table_row_count), pk_col, only_ui_pk=only_pk_ui)

        p_data, p_col_names = scrapper(main_db=self.dst_db).crawl_db(table_name, int(table_row_count), pk_col, only_ui_pk=only_pk_ui)

        return o_data, o_col_names, p_data, p_col_names

    def find_geom_module_id(self):
        all_table_columns = DBTableColumnCompare.objects.filter(compare_dbs=self.compare_db)
        for each_rows in all_table_columns:
            column_name = each_rows.column_name
            if column_name and column_name == 'GEOM':
                try:
                    oob = DBTableCompare.objects.get(table_name=each_rows.table_name, compare_dbs=self.compare_db)
                    oob.geom = True
                    oob.save()
                except DBTableCompare.DoesNotExist:
                    pass
            if column_name and column_name == 'MODULE_ID':
                try:
                    oob = DBTableCompare.objects.get(table_name=each_rows.table_name, compare_dbs=self.compare_db)
                    oob.module_id = True
                    oob.save()
                except DBTableCompare.DoesNotExist:
                    pass