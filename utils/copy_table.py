import logging
from utils.script_scrapper import scrapper
from utils.queries import O_RET_TABLE_ROW_QUERY, O_PRIM_KEY_SCRIPT_Q, O_UNI_KEY_SCRIPT_Q
from django_rq import job


class xerox:
    def __init__(self, src_db, dst_db, table_name, table_row_count, upper_bound, commit_each):
        self.log = logging.getLogger(__name__)
        self.src_db = src_db
        self.dst_db = dst_db
        self.src_db_type = self.src_db.type
        self.dst_db_type = self.dst_db.type
        self.table_name = table_name
        self.table_row_count = table_row_count
        self.upper_bound = upper_bound
        self.commit_each = commit_each
        self.src_schema_name = self.src_db.username
        self.dst_schema_name = self.dst_db.username


    def get_primary_key(self):
        return scrapper(db_type=self.src_db_type,
                        main_db=self.src_db).get_pk_of_table(self.table_name, O_PRIM_KEY_SCRIPT_Q)

    def get_unique_key(self):
        return scrapper(db_type=self.src_db_type,
                        main_db=self.src_db).get_uk_of_table(self.table_name, self.src_schema_name, O_UNI_KEY_SCRIPT_Q)

    @job
    def insert_rows(self, data, col_names, commit_each=False):
        scrapper(db_type=self.dst_db_type,
                 main_db=self.dst_db).insert_row(self.table_name, data, col_names, self.table_row_count, commit_each=commit_each)

    def execute_it(self):
        pk_col = self.get_primary_key()

        if pk_col is None:
            pk_col = self.get_unique_key()

        data, col_names = scrapper(db_type=self.src_db_type,
                                   main_db=self.src_db).crawl_db(O_RET_TABLE_ROW_QUERY, self.table_name, int(self.table_row_count), pk_col,
                                                                 upper_bound=self.upper_bound)

        divide_by = 1000
        for i in range(0, len(data), divide_by):
            self.insert_rows(data[i: i + divide_by], col_names, self.commit_each)
            # self.insert_rows.delay(data[i: i + divide_by], col_names)
