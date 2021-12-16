import logging
import os

from utils.common_func import send_notification
from django_rq import job
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import DBCompareDBResults, DBCompare, DBTableCompare, DBTableCompareTokens
from utils.compare_data import comparator
from time import sleep
import random, string


logger = logging.getLogger(__name__)

channels_layer = get_channel_layer()


@job('default')
def get_compare_sync(compare_ids, __func_name):
    if compare_ids is None:
        return
    try:
        obj = DBCompareDBResults.objects.get(compare_dbs__id=compare_ids, func_call=__func_name)
        while obj.status != 1:
            try:
                obj = DBCompareDBResults.objects.get(compare_dbs__id=compare_ids, func_call=__func_name)
                sleep(5)
            except DBCompareDBResults.DoesNotExist:
                logger.info("Can't find the results for the combination of compare_id = " + str(compare_ids) + " and function name " + str(__func_name))
                async_to_sync(channels_layer.group_send)('job_ticks', {
                    'type': 'send_job_results', 'text': 'failure'
                })
        logger.info("results found for the combination of compare_id = " + str(compare_ids) + " and function name " + str(__func_name))
        async_to_sync(channels_layer.group_send)('job_ticks', {
            'type': 'send_job_results', 'text': 'success'
            }
        )
    except DBCompareDBResults.DoesNotExist:
        logger.info("Can't find the results for the combination of compare_id = " + str(compare_ids) + " and function name " + str(__func_name))
        async_to_sync(channels_layer.group_send)('job_ticks', {
            'type': 'send_job_results', 'text': 'failure'
        })


@job('default')
def real_table_data_compare(user, src_db, dst_db, com_db, table_name, compare_list, table_row_count):
    tfile = None
    try:
        send_notification(user, "DB {} -> {} Data comparison started - {} ".format(src_db.name, dst_db.name, table_name))
        tfile, new_file_name = comparator(user, src_db=src_db, dst_db=dst_db,
                   compare_db=com_db).compare_data(table_name=table_name, pk_col=compare_list, table_row_count=table_row_count)
    finally:
        if tfile is not None:
            obj = DBTableCompare.objects.get(compare_dbs=DBCompare.objects.get(src_db=src_db, dst_db=dst_db), table_name=table_name)
            try:
                if obj.last_compared_file_loc is not None:
                    os.remove(obj.last_compared_file_loc)
            except:
                pass
            token = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(50))
            obj.last_compared_file_loc = token
            obj2 = DBTableCompareTokens()
            obj2.token = token
            obj2.file_path = tfile.name
            obj2.save()
            obj.save()
            send_notification(user, "DB {} -> {} Data comparison result ".format(src_db.name, dst_db.name), token)
        send_notification(user, "DB {} -> {} Data comparison completed - {}.".format(src_db.name, dst_db.name, table_name))
