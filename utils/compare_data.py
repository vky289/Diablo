import logging
from app.dbs.models import DBTableCompare
from utils.script_scrapper import scrapper
from utils.compare_database import any_db
from datetime import datetime
from tempfile import NamedTemporaryFile
import json


class comparator:

    def __init__(self, user, src_db, dst_db, compare_db):
        self.user = user
        self.log = logging.getLogger(__name__)
        self.src_db = src_db
        self.dst_db = dst_db
        self.src_db_type = self.src_db.type
        self.dst_db_type = self.dst_db.type
        self.compare_db = compare_db
        self.table_name = None


    def get_primary_key(self, table_name):
        return scrapper(main_db=self.src_db).get_pk_of_table(table_name)

    def get_unique_key(self, table_name, src_schema_name):
        return scrapper(main_db=self.src_db).get_uk_of_table(table_name, src_schema_name)

    def create_and_load_temp_file(self, compared_data):
        new_file_name = self.table_name + '_' + str(datetime.now()).replace(' ',  '_') \
            .replace('-', '_') \
            .replace(':', '_')

        tfile = NamedTemporaryFile(delete=False, prefix=new_file_name, suffix='.json', )
        with open(tfile.name, 'w+') as fi:
            fi.write(json.dumps(compared_data, indent=4, sort_keys=True))
        tfile.flush()
        tfile.read()

        return tfile, new_file_name

    def compare_data(self, table_name, pk_col=None, table_row_count=None):
        if table_name is None:
            raise RuntimeError("Table Name cannot be empty")
        else:
            self.table_name = table_name

        if pk_col is None:
            pk_col = self.get_primary_key(table_name=table_name)

        if pk_col is None:
            pk_col = self.get_unique_key(table_name=table_name, src_schema_name=self.src_db.username)

        if pk_col is None:
            raise RuntimeError("No Primary Key/Unique key found. Cannot compare data!")

        try:
            o_data, o_col_names, p_data, p_col_names = any_db(user=self.user,
                                                              src_db=self.src_db,
                                                              dst_db=self.dst_db,
                                                              compare_db=self.compare_db)\
                .compare_real_data(table_name=table_name,
                                table_row_count=table_row_count,
                                pk_col=pk_col, only_pk_ui=True)

            data = {}
            res_dict = {}
            data['rowCount'] = max(len(o_data), len(p_data))
            data['columnCount'] = len(o_col_names)
            data['tableName'] = table_name

            if pk_col is not None and type(pk_col) is not set:
                pk = o_col_names.index(pk_col)
                o_data_only_pk = [item[pk] for item in o_data]
                p_data_only_pk = [item[pk] for item in p_data]
                data['searchColumn'] = pk
                data['primaryKeyUsed'] = 'Yes'
                data['uniqueKeyUsed'] = 'No'

                if len(o_data_only_pk) > 0:
                    for o in o_data_only_pk:
                        if o not in p_data_only_pk:
                            res_dict[o] = 'Not Found'
                        else:
                            res_dict[o] = 'Present'

            elif pk_col is not None and type(pk_col) is set:
                data['searchColumns'] = ';~;'.join([p_col for p_col in pk_col])
                data['uniqueKeyUsed'] = 'Yes'
                data['primaryKeyUsed'] = 'No'

                def find_and_update(o_p_o_col_names, o_p_data, o_p_pk_col):
                    data_only_ui = {}
                    for item in o_p_data:
                        joined_col = ';~;'.join([str(item[o_p_o_col_names.index(p_col)]) for p_col in o_p_pk_col])
                        for u in o_p_pk_col:
                            ind = o_p_o_col_names.index(u)
                            if data_only_ui.get(joined_col) is not None:
                                data_only_ui[joined_col].update({u: item[ind]})
                            else:
                                data_only_ui[joined_col] = {u: item[ind]}
                    return data_only_ui

                o_data_result_set = find_and_update(o_col_names, o_data, pk_col)
                p_data_result_set = find_and_update(p_col_names, p_data, pk_col)

                if len(o_data_result_set) > 0:
                    total_result_map = o_data_result_set.copy()
                    total_result_map.update(p_data_result_set)
                    for o in total_result_map:
                        if o not in o_data_result_set:
                            res_dict[o] = 'Not Found in Src'
                        elif o not in p_data_result_set:
                            res_dict[o] = 'Not Found in Dest'
                        else:
                            res_dict[o] = 'Present'

            data['data'] = res_dict

            return self.create_and_load_temp_file(data)

        except DBTableCompare.DoesNotExist:
            raise RuntimeError("Table compare data not found")
        except Exception as anyExp:
            raise RuntimeError(str(anyExp))
