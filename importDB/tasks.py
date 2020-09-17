from __future__ import absolute_import, unicode_literals

from celery import shared_task
import time
from . import views
from celery.schedules import crontab
from celery.task import periodic_task
import json
import requests
from datetime import datetime
import time
import importDB.pandasMysql as pm
import pandas as pd
import numpy as np
import os
from sqlalchemy.engine import create_engine
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from .models import Get_db       
from .models import Get_db_oracle
from .models import PRPM_v_grt_pj_team_eis  # " . " หมายถึง subfolder ต่อมาจาก root dir
from .models import PRPM_v_grt_pj_budget_eis
from .models import Prpm_v_grt_project_eis
from .models import master_ranking_university_name

# เกี่ยวกับกราฟ
from plotly.offline import plot
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

@shared_task
def sum(a,b):
    time.sleep(10)
    return a+b

@shared_task
def test():
    views.multiply.delay()
    print("done!")
    return None


@shared_task
def sleepy(duration):
    time.sleep(duration)
    print("tasks")
    return None

@shared_task
def dump2():
    try:
        
        sql_cmd =  """SELECT 
                    *
                FROM RESEARCH60.R_FUND_TYPE
                """

        con_string = views.getConstring('oracle')
        engine = create_engine(con_string, encoding="latin1" )
        df = pd.read_sql_query(sql_cmd, engine)
        # df = pm.execute_query(sql_cmd, con_string)
        

        ###################################################
        # save path
        con_string2 = views.getConstring('sql')
        pm.save_to_db('importdb_prpm_r_fund_type', con_string2, df)

        dt = datetime.now()
        timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

    except Exception as e :
        checkpoint = False
        print('Something went wrong :', e)

    print("End Dump2")
    return None


@shared_task
def tasks_dump():
    # dt = datetime.now()
    # print("Start Data Dumping")
    # print("."*20)
    # dump_RawData_1()
    # dump_RawData_2()
    # dump_RawData_3()
    # dump_RawData_4()
    # dump_RawData_5()
    # dump_RawData_6()

    print("Start Data Quering")
    print("."*20)
    # views.query1()
    # time.sleep(10)
    # views.query2()
    # time.sleep(10)
    # views.query3()
    # time.sleep(10)
    # views.query4()
    # time.sleep(10)
    # views.query5()
    # time.sleep(10)
    views.query6()
    # time.sleep(10)
    # views.query7()
    # time.sleep(10)
    # views.query8()
    # time.sleep(10)
    # views.query9()
    # time.sleep(10)
    # views.query10()
    # time.sleep(10)
    # views.query11()
    # time.sleep(10)
    # views.query12()
    # time.sleep(10)
    # views.query13()
    # time.sleep(10)

    return None