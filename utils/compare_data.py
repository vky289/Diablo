import logging
from app.dbs.models import DBTableCompare

class comparator:

    def __init__(self, user, src_db, dst_db, compare_db):
        self.user = user
        self.log = logging.getLogger(__name__)
        self.src_db = src_db
        self.dst_db = dst_db
        self.src_db_type = self.src_db.type
        self.dst_db_type = self.dst_db.type
        self.compare_db = compare_db


    def compare_data(self, table_name):
        if table_name is None:
            raise RuntimeError("Table Name cannot be empty")
        table_compare_record = None
        try:
            table_compare_record = DBTableCompare.objects.get(compare_dbs=self.compare_db, table_name=table_name)
            src_rec_count = table_compare_record.src_row_count
            if src_rec_count > 1000:
                raise RuntimeError("Max limit to compare dataset is set to 1000. Talk to Admin!")

        except DBTableCompare.DoesNotExist:
            raise RuntimeError("Table compare data not found")