from sqlalchemy import create_engine
import pymysql 
import pandas as pd
from mysql.connector import connection

import plotly.express as px

def save_to_db(tableName, con_string, df):
    try:

        conn = create_engine(con_string,max_identifier_length=128 ,echo=False) 
        df.to_sql(tableName, conn, if_exists = 'replace', index = True, index_label = 'id' ) # replace , append
        print('The data is saved')
    except Exception as e:
        print(f'error -save_to_db-> {e}')

def execute_query(sql_cmd, con_string, tableName = None, params=None):
    try:
        conn = create_engine(con_string, max_identifier_length=128)
        # connection = conn.connect() 
        print("We are connected to DB ...")
        if params:
            df = pd.read_sql(sql_cmd, conn, params)
            print(df.dtypes)
            if tableName:
                save_to_db(tableName, conn, df)
                print('The data is saved')
            return df
        else:
            df = pd.read_sql(sql_cmd, conn)
            if tableName:
                save_to_db(tableName, conn, df)
                print('The data is saved')
            return df
    except Exception as e:
        print(f'error -execute_query-> {e}')
    

#def create_new_table():

if __name__ == "__main__":
    
    print(f'pymysql version: {pymysql.__version__}')
    print(f'pandas version: {pd.__version__}')

    # uid = 'root'
    # pwd = ''
    # host = 'localhost'
    # port = 3306
    # db = 'sakila.db'
    # con_string = f'mysql+pymysql://{uid}:{pwd}@{host}:{port}/{db}'
    #print(f'connection string = {con_string}')

    # sql_cmd =  """select 
    #                 A.store_id,
    #                 B.address,
    #                 COUNT(*) AS totalN,
    #                 ROUND(SUM(D.amount),2) as totalSales
    #             FROM store A
    #                 JOIN address B on A.address_id = B.address_id
    #             JOIN staff C ON A.store_id = C.store_id
    #                 JOIN payment D ON C.store_id = D.staff_id
    #             GROUP BY 1, 2
    #                 ORDER BY 4 DESC;
    #             """

    sql_cmd =  """SELECT 
                    *
                  FROM CUSTOMER
                """

    uid = 'SYSTEM'
    pwd = 'Qwer1234!'
    host = 'localhost'
    port = 1521
    db = 'orcl101'
    con_string = f'oracle://{uid}:{pwd}@{host}:{port}/{db}'
    #df = pd.read_sql(sql, con, params = [2])
    # df = execute_query(sql_cmd, con_string, params= [2])
    df = execute_query(sql_cmd, con_string)
    print(df)
    print('-'*100)
    # print((df.loc[:,'budget']))
    print((df.loc[0:,'budget']))

   # df.to_sql('results',con, if_exists = 'replace', index=False)
    print('-'*100)
    tips = px.data.tips()
    print(tips.head())