import logging
from app.dbs.models import DBTableCompare
from app.core.models import SYSetting
from utils.script_scrapper import scrapper
from utils.compare_database import any_db


class comparator:

    def __init__(self, user, src_db, dst_db, compare_db):
        self.user = user
        self.log = logging.getLogger(__name__)
        self.src_db = src_db
        self.dst_db = dst_db
        self.src_db_type = self.src_db.type
        self.dst_db_type = self.dst_db.type
        self.compare_db = compare_db


    def get_primary_key(self, table_name):
        return scrapper(db_type=self.src_db_type,
                        main_db=self.src_db).get_pk_of_table(table_name)

    def get_unique_key(self, table_name, src_schema_name):
        return scrapper(db_type=self.src_db_type,
                        main_db=self.src_db).get_uk_of_table(table_name, src_schema_name)

    def compare_data(self, table_name):
        if table_name is None:
            raise RuntimeError("Table Name cannot be empty")
        pk_col = self.get_primary_key(table_name=table_name)

        if pk_col is None:
            pk_col = self.get_unique_key(table_name=table_name, src_schema_name=self.src_db.username)

        if pk_col is None:
            raise RuntimeError("No Primary Key/Unique key found. Cannot compare data!")

        try:
            table_compare_record = DBTableCompare.objects.get(compare_dbs=self.compare_db, table_name=table_name)
            table_row_count = table_compare_record.src_row_count
            table_compare_max = 1000
            try:
                cols = SYSetting.objects.get(name="COL_COMPARE_MAX")
                table_compare_max = cols.value
            except SYSetting.DoesNotExist:
                pass
            try:
                table_compare_max = int(table_compare_max)
            except:
                table_compare_max = 1000
            if table_row_count >= int(table_compare_max):
                raise RuntimeError('Cannot compare table more than ' + str(table_compare_max) + ' records. Talk to Admin!')

            o_data, o_col_names, p_data, p_col_names = any_db(user=self.user,
                                                              src_db=self.src_db,
                                                              dst_db=self.dst_db,
                                                              compare_db=self.compare_db).compare_real_data(table_name=table_name,
                                                                                                            table_row_count=table_row_count,
                                                                                                            pk_col=pk_col)

            data = {}
            res_dict = {}
            data['rowCount'] = max(len(o_data), len(p_data))
            data['columnCount'] = len(o_col_names)
            data['tableName'] = table_name
            o_data_only_pk = []
            p_data_only_pk = []
            o_data_only_ui = {}
            p_data_only_ui = {}
            if pk_col is not None and type(pk_col) is not set:
                pk = o_col_names.index(pk_col)
                o_data_only_pk = [item[pk] for item in o_data]
                p_data_only_pk = [item[pk] for item in p_data]
                data['primaryKeyCol'] = pk
                data['primaryKeyFound'] = 'Yes'
            elif pk_col is not None and type(pk_col) is set:
                data['primaryKeyFound'] = 'No'
                for item in o_data:
                    joined_col = ';~;'.join([str(item[o_col_names.index(p_col)]) for p_col in pk_col])
                    for u in pk_col:
                        ind = o_col_names.index(u)
                        if o_data_only_ui.get(joined_col) is not None:
                            o_data_only_ui[joined_col].update({u: item[ind]})
                        else:
                            o_data_only_ui[joined_col] = {u: item[ind]}
                for item in p_data:
                    joined_col = ';~;'.join([str(item[p_col_names.index(p_col)]) for p_col in pk_col])
                    for u in pk_col:
                        ind = p_col_names.index(u)
                        if p_data_only_ui.get(joined_col) is not None:
                            p_data_only_ui[joined_col].update({u: item[ind]})
                        else:
                            p_data_only_ui[joined_col] = {u: item[ind]}
                data['uniqueIndexKeyCol'] = ';~;'.join([p_col for p_col in pk_col])

            if len(o_data_only_pk) > 0:
                for o in o_data_only_pk:
                    if o not in p_data_only_pk:
                        res_dict[o] = 'N/A'
                    else:
                        res_dict[o] = 'Present'
            if len(o_data_only_ui) > 0:
                for o in o_data_only_ui:
                    if o not in p_data_only_ui:
                        res_dict[o] = 'N/A'
                    else:
                        res_dict[o] = 'Present'

            data['data'] = res_dict

            return data

        except DBTableCompare.DoesNotExist:
            raise RuntimeError("Table compare data not found")