from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults

from airflow.models import XCom


class HSIComponentsGetter(BaseOperator):

    @apply_defaults
    def __init__(
            self,
            *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, context):
        import urllib
        from bs4 import BeautifulSoup
        import pandas as pd

        # define header
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent, }

        # scrap table data
        url = "http://www.etnet.com.hk/www/eng/stocks/indexes_detail.php?subtype=HSI"
        request = urllib.request.Request(url, None, headers)
        html = urllib.request.urlopen(request).read()

        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'class': 'figureTable'})
        df = pd.read_html(str(table), header=0)[0]
        hsi_list = [str(code).rjust(4, '0')+'.HK' for code in df['Code']]

        # push to xcom
        ti = context['ti']
        ti.xcom_push(key='hsi_list', value=hsi_list)


class HSIDownloader(BaseOperator):

    @apply_defaults
    def __init__(
            self,
            *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, context):
        import yfinance as yf
        import pandas as pd

        hsi_list = context['task_instance'].xcom_pull(
            task_ids='get_hsi_components', key='hsi_list')
        df = []
        for code in hsi_list:
            tmp = yf.download(code, period="max", progress=False)
            tmp['code'] = code
            df.append(tmp)
        df = pd.concat(df, axis=0)
