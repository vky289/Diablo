import logging

from utils.enums import DbType
from utils.script_scrapper import scrapper
from app.dbs.models import DBTableCompare, DBTableColumnCompare
from utils.queries import O_ROW_COUNT, P_ROW_COUNT, O_COLUMN_NAMES, P_COLUMN_NAMES


class any_db:
    def __init__(self, src_db, dst_db):
        self.log = logging.getLogger(__name__)
        self.src_db = src_db
        self.dst_db = dst_db
        self.src_db_type = self.src_db.type
        self.dst_db_type = self.dst_db.type

    @staticmethod
    def get_it_rows(set_of_values):
        fin_set = set()
        fin_dict = dict()
        if set_of_values:
            for s_o_v in set_of_values:
                if isinstance(s_o_v, str) or isinstance(s_o_v, int) or isinstance(s_o_v, float) or isinstance(s_o_v, tuple):
                    fin_set.add(s_o_v[0])
                    fin_dict[s_o_v[0]] = s_o_v[1]
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
                    fin_dict[s_o_v[0]] += [{'column_name' : s_o_v[1], 'data_type': s_o_v[2]}]
        return sorted(fin_set), fin_dict

    def store_in_db_columns(self, dict2, DbType):
        for o_r in dict2:
            l_c_list = dict2.get(o_r)
            for l_c in l_c_list:
                obj = DBTableColumnCompare()
                obj.table_name = o_r
                obj.src_db = self.src_db
                obj.dst_db = self.dst_db
                obj.type = DbType
                obj.column_name = l_c.get('column_name')
                obj.datatype = l_c.get('data_type')
                obj.save()

    def c_db(self):
        o_result, o_col_names = scrapper(db_type=self.src_db_type,
                                         main_db=self.src_db).get_table_desc_cols(schema_name=self.src_db.username,
                                                                                             SCRIPT_Q=O_ROW_COUNT)
        o_set, o_dict = self.get_it_rows(o_result)

        p_result, p_col_names = scrapper(db_type=self.dst_db_type,
                                         main_db=self.dst_db).get_table_desc_cols(schema_name=self.dst_db.service,
                                                                                  SCRIPT_Q=P_ROW_COUNT)
        p_set, p_dict = self.get_it_rows(p_result)

        if o_set is not None or p_set is not None:
            obj1 = DBTableCompare.objects.filter(src_db=self.src_db, dst_db=self.dst_db)
            obj1.delete()

        for o_r in o_set:
            obj = DBTableCompare()
            obj.table_name = o_r
            obj.src_db = self.src_db
            obj.dst_db = self.dst_db
            obj.src_row_count = o_dict.get(o_r)
            obj.dst_row_count = p_dict.get(o_r)
            obj.save()

    def cdata_db(self):
        obj1 = DBTableColumnCompare.objects.filter(src_db=self.src_db, dst_db=self.dst_db)
        obj1.delete()

        o_result1, o_col_names1 = scrapper(db_type=self.src_db_type,
                                           main_db=self.src_db).get_table_desc_cols(schema_name=self.src_db.username,
                                                                                              SCRIPT_Q=O_COLUMN_NAMES)
        o_set2, o_dict2 = self.get_it_col_datatype(o_result1)

        p_result2, p_col_names2 = scrapper(db_type=self.dst_db_type,
                                           main_db=self.dst_db).get_table_desc_cols(schema_name=self.dst_db.service,
                                                                                           SCRIPT_Q=P_COLUMN_NAMES)

        p_set2, p_dict2 = self.get_it_col_datatype(p_result2)


        self.store_in_db_columns(o_dict2, DbType.ORACLE)

        self.store_in_db_columns(p_dict2, DbType.POSTGRES)

