import logging
import time
from django.db import connection

_logger = logging.getLogger(__name__)

from sentry_sdk import capture_exception



class DatabaseUtils:
    """
    Helper functions for database
    """

    @classmethod
    def bulk_upsert(cls,model,df):
        chunkSize=10000
        chunks = DatabaseUtils.splitDataFrameIntoSmaller(df,chunkSize)
        for chunk in chunks:
            DatabaseUtils.bulk_upsert_chunk(model,chunk)

    @classmethod
    def splitDataFrameIntoSmaller(cls,df, chunkSize = 10000): 
        listOfDf = list()
        numberChunks = len(df) // chunkSize + 1
        for i in range(numberChunks):
            listOfDf.append(df[i*chunkSize:(i+1)*chunkSize])
        return listOfDf
    @classmethod
    def bulk_upsert_chunk(cls,model,df):
        df=df.dropna()
        # print(df)
        if len(df) ==0 :
            return
        sql_insert_into = "INSERT INTO {0} ({1}) VALUES ({2}) ON DUPLICATE KEY UPDATE {3};".format(
            model._meta.db_table, ','.join(df.columns), ','.join(['%s' for i in df.columns]), ','.join("{0} = VALUES({0})".format(column) for column in df.columns))
        
        
        try:
            # DatabaseUtils.upsert(P1_RTOLCap_RTOFFCap,results)
            with connection.cursor() as cursor:
                cursor.executemany(
                    sql_insert_into,
                    [
                        [row[column] for column in df.columns] for index, row in df.iterrows() 
                        
                    ])
        except Exception as e:
            # capture_exception(e)
            _logger.exception("Error when checking a function is exist or not.", exc_info=True)
        pass