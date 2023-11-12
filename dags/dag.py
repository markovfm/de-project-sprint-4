from airflow import DAG
from airflow.operators.python import PythonOperator
import psycopg2, psycopg2.extras
import pandas as pd
import datetime


dag = DAG(
    dag_id='542_s3_load_example',
    schedule_interval='0 0 * * *',
    start_date=datetime.datetime(2021, 1, 1),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
    tags=['example', 'example2'],
    params={"example_key": "example_value"},
)

def upload_from_s3_to_gp():
    uol_url = "https://storage.yandexcloud.net/s3-sprint3/cohort_18/Nick/project/TWpBeU15MHhNUzB3TWxReU1UbzBPRG8xTmdsT2FXTnI=/user_order_log.csv"
    ual_url = "https://storage.yandexcloud.net/s3-sprint3/cohort_18/Nick/project/TWpBeU15MHhNUzB3TWxReU1UbzBPRG8xTmdsT2FXTnI=/user_activity_log.csv"
    pl_url = "https://storage.yandexcloud.net/s3-sprint3/cohort_18/Nick/project/TWpBeU15MHhNUzB3TWxReU1UbzBPRG8xTmdsT2FXTnI=/price_log.csv"
    cr_url = "https://storage.yandexcloud.net/s3-sprint3/cohort_18/Nick/project/TWpBeU15MHhNUzB3TWxReU1UbzBPRG8xTmdsT2FXTnI=/customer_research.csv"


    df_order_log = pd.read_csv(uol_url)
    df_activity_log = pd.read_csv(ual_url)
    # df_pl = pd.read_csv(pl_url)
    df_customer_research = pd.read_csv(cr_url)
    
    pg_conn = psycopg2.connect("host='localhost' port='15432' dbname='de' user='jovyan' password='jovyan'")
    cur = pg_conn.cursor()


    df_customer_research.reset_index(drop = True, inplace = True)
    insert_cr = "insert into staging.customer_research (date_id,category_id,geo_id,sales_qty,sales_amt) VALUES {cr_val};"
    i = 0
    step = int(df_customer_research.shape[0] / 100)
    while i <= df_customer_research.shape[0]:
        print('df_customer_research' , i, end='\r')
        
        cr_val =  str([tuple(x) for x in df_customer_research.loc[i:i + step].to_numpy()])[1:-1]
        cur.execute(insert_cr.replace('{cr_val}',cr_val))
        pg_conn.commit()
        
        i += step+1

    #get order log
    df_order_log = df_order_log.drop_duplicates(subset=['uniq_id'])
    df_order_log.reset_index(drop = True, inplace = True)
    insert_uol = "insert into staging.user_order_log (uniq_id, date_time, city_id, city_name, customer_id, first_name, last_name, item_id, item_name, quantity, payment_amount) VALUES {uol_val};"
    i = 0
    step = int(df_order_log.shape[0] / 100)
    while i <= df_order_log.shape[0]:
        print('df_order_log',i, end='\r')
        
        uol_val =  str([tuple(x) for x in df_order_log.drop(columns = ['id'] , axis = 1).loc[i:i + step].to_numpy()])[1:-1]
        cur.execute(insert_uol.replace('{uol_val}',uol_val))
        pg_conn.commit()
        
        
        i += step+1

    #get activity log
    df_activity_log.reset_index(drop = True, inplace = True)
    insert_ual = "insert into staging.user_activity_log (uniq_id, date_time, action_id, customer_id, quantity) VALUES {ual_val};"
    i = 0
    step = int(df_activity_log.shape[0] / 100)
    while i <= df_activity_log.shape[0]:
        print('df_activity_log',i, end='\r')
        
        if df_activity_log.drop(columns = ['id'] , axis = 1).loc[i:i + step].shape[0] > 0:
            ual_val =  str([tuple(x) for x in df_activity_log.drop(columns = ['id'] , axis = 1).loc[i:i + step].to_numpy()])[1:-1]
            cur.execute(insert_ual.replace('{ual_val}',ual_val))
            pg_conn.commit()
        
        
        i += step+1


    cur.close()
    pg_conn.close()

    # df_uol.to_csv('user_order_log.csv', index=False)
    # df_ual.to_csv('user_activity_log.csv', index=False)
    # df_pl.to_csv('price_log.csv', index=False)



def insert_f_daily_sales():
    # pg_conn = BaseHook.get_connection('pg_connection')
    pg_conn = psycopg2.connect("host='localhost' port='15432' dbname='de' user='jovyan' password='jovyan'")
    cur = pg_conn.cursor()

    cur.execute('''INSERT INTO mart.f_sales (date_id, item_id, customer_id, city_id, quantity, payment_amount)
                    SELECT
                        dc.date_id,
                        uol.item_id,
                        uol.customer_id,
                        uol.city_id,
                        SUM(uol.quantity),
                        SUM(uol.payment_amount)
                    FROM staging.user_order_log AS uol
                    LEFT JOIN mart.d_calendar AS dc ON TO_DATE(uol.date_time::TEXT, 'YYYY-MM-DD') = dc.fact_date
                    GROUP BY dc.date_id, uol.item_id, uol.customer_id;''')
    pg_conn.commit()

    cur.close()
    pg_conn.close()

upload_from_s3_to_gp >> insert_f_daily_sales