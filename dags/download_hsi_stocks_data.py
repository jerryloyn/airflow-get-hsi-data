from datetime import timedelta
from datetime import datetime
from airflow import DAG
from airflow.operators.hsi_plugin import HSIComponentsGetter, HSIDownloader
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'jerryloyn',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['yunnamlo@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
dag = DAG(
    'hsi_data',
    default_args=default_args,
    description='A daily job to download HSI stock data',
    schedule_interval=timedelta(days=1),
)


get_hsi_components = HSIComponentsGetter(task_id='get_hsi_components', dag=dag)

get_hsi_stocks_data = HSIDownloader(task_id='get_hsi_stocks_data', dag=dag)

get_hsi_components >> get_hsi_stocks_data
