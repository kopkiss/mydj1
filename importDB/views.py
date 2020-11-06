from django.shortcuts import render, redirect    # หมายถึง เป็นการเรียกจาก Template ที่เราสร้างไว้
from django.http import HttpResponse   # หมายถึง เป็นการ วาด HTML เอง
import pandas as pd
import numpy as np
import os
import json
import requests
from pprint import pprint
import warnings
import itertools
# เกี่ยวกับวันที่ 
from datetime import datetime
import time

# เกี่ยวกับฐานข้อมูล
from .models import Get_db       # " . " หมายถึง subfolder ต่อมาจาก root dir
from .models import Get_db_oracle
from .models import PRPM_v_grt_pj_team_eis  
from .models import PRPM_v_grt_pj_budget_eis
from .models import Prpm_v_grt_project_eis
from .models import master_ranking_university_name

import pymysql
import cx_Oracle
from sqlalchemy.engine import create_engine
import importDB.pandasMysql as pm
import urllib.parse

# เกี่ยวกับกราฟ
from plotly.offline import plot
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

# เกี่ยวกับ scopus isi tci
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# เกี่ยวกับการ login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.models import User

# เกี่ยวกับการ predictions
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import r2_score
# ดึง script PHP
import subprocess
from subprocess import check_output

# Create your views here.

def getConstring(check):  # สร้างไว้เพื่อ เลือกที่จะ get database ด้วย mysql หรือ oracle
    
    if check == 'sql':
        uid = 'root'
        pwd = ''
        host = 'localhost'
        port = 3306
        db = 'mydj2'
        con_string = f'mysql+pymysql://{uid}:{pwd}@{host}:{port}/{db}'
    elif check == 'oracle':
        DIALECT = 'oracle'
        SQL_DRIVER = 'cx_oracle'
        USERNAME = 'pnantipat' #enter your username
        PASSWORD = urllib.parse.quote_plus('sfdgr4g4') #enter your password
        HOST = 'delita.psu.ac.th' #enter the oracle db host url
        PORT = 1521 # enter the oracle port number
        SERVICE = 'delita.psu.ac.th' # enter the oracle db service name
        con_string = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + PASSWORD +'@' + HOST + ':' + str(PORT) + '/?service_name=' + SERVICE

    return con_string

def showdbsql(request):

     #  Query data from Model
    print(f'pymysql version: {pymysql.__version__}')
    print(f'pandas version: {pd.__version__}')
    #################################
    ##### Mysql#######################
    ###############################
    uid = 'root'
    pwd = ''
    host = 'localhost'
    port = 3306
    db = 'sakila.db'
    ##########################################################
    #format--> dialect+driver://username:password@host:port/database
    con_string = f'mysql+pymysql://{uid}:{pwd}@{host}:{port}/{db}'
    #############################################################
    
    sql_cmd =  """select 
                customer_id,
                first_name,
                last_name
                from customer
                limit 10;
            """

    uid2 = 'root'
    pwd2 = ''
    host2 = 'localhost'
    port2 = 3306
    db2 = 'mydj2'
    con_string2 = f'mysql+pymysql://{uid2}:{pwd2}@{host2}:{port2}/{db2}'

    df = pm.execute_query(sql_cmd, con_string)
    
    pm.save_to_db('importDB/importdb_get_db', con_string2, df)
    #############################
    ################################################
    ##############Oracle #######################
    ##############################################

    # sql_cmd =  """SELECT 
    #                 *
    #               FROM CUSTOMER
    #             """

    # uid = 'SYSTEM'
    # pwd = 'Qwer1234!'
    # host = 'localhost'
    # port = 1521
    # db = 'orcl101'
    # con_string = f'oracle://{uid}:{pwd}@{host}:{port}/{db}'

    # df = pm.execute_query(sql_cmd, con_string)
    
    ###################################################
    data = Get_db.objects.all()  #ดึงข้อมูลจากตาราง Post มาทั้งหมด
    #data = Meta.objects.all()  #ดึงข้อมูลจากตาราง Post มาทั้งหมด

    return render(request,'showdbsql.html',{'posts':data})

def showdbOracle(request):

     #  Query data from Model
    print(f'pymysql version: {pymysql.__version__}')
    print(f'pandas version: {pd.__version__}')
    print(f'cx_Oracle version: {cx_Oracle.__version__}')

    os.environ["NLS_LANG"] = ".UTF8" 
    data = PRPM_v_grt_pj_budget_eis.objects.all()[:50]  #ดึงข้อมูลจากตาราง Get_db_oracle index 0 - 49

    return render(request,'importDB/showdbOracle.html',{'posts': data})

def home(requests):  # หน้า homepage หน้าแรก

    def moneyformat(x):  # เอาไว้เปลี่ยน format เป็นรูปเงิน
        return "{:,.2f}".format(x)

    def get_head_page(): # get จำนวนของนักวิจัย 
        df = pd.read_csv("""mydj1/static/csv/head_page.csv""")
        return df.iloc[0].astype(int)


    def graph7():
        df = pd.read_csv("""mydj1/static/csv/Filled_area_chart.csv""")

        df1 = df[["year","Goverment"]]
        df2 = df[["year","Revenue"]]
        df3 = df[["year","Campus"]]
        df4 = df[["year","Department"]]
        df5 = df[["year","National"]]
        df6 = df[["year","International"]]
        df7 = df[["year","Matching_fund"]]

        fig = go.Figure()

        # 0
        fig.add_trace(go.Scatter(
            x=df1["year"], y=df1["Goverment"],
            fill='tozeroy',
            mode='lines',
            line_color='#0066FF',
            line=dict(width=0.8),
            name="เงินงบประมาณแผ่นดิน"
            ))
        # 1
        fig.add_trace(go.Scatter(
            x=df2["year"], 
            y=df2["Revenue"],
            fill='tozeroy', # fill area between trace0 and trace1
            mode='lines',
            line_color='#1976D2 ' ,
            line=dict(width=0.8),
            name="เงินรายได้มหาวิทยาลัย"
            ))
        # 2
        fig.add_trace(go.Scatter(
            x=df3["year"], y=df3["Campus"],
            fill='tozeroy',
            mode='lines',
            line_color='#4FC3F7  ',
            line=dict(width=0.8),
            name="เงินรายได้วิทยาเขต"
            ))
        # 3
        fig.add_trace(go.Scatter(
            x=df4["year"], 
            y=df4["Department"],
            fill='tozeroy', # fill area between trace0 and trace1
            mode='lines',
            line_color='#03A9F4', 
            line=dict(width=0.8),
            name="เงินรายได้คณะ/หน่วยงาน"
        ))
        # 4
        fig.add_trace(go.Scatter(
            x=df5["year"], 
            y=df5["National"],
            fill='tozeroy',
            mode='lines',
            line_color='#5DADE2   ',
            line=dict(width=0.8),
            name="เงินทุนภายนอก(ในประเทศ)"
            ))
        # 5
        fig.add_trace(go.Scatter(
            x=df6["year"], 
            y=df6["International"],
            fill='tozeroy', # fill area between trace0 and trace1
            mode='lines', line_color='#2196F3 ' ,
            line=dict(width=0.8),
            name="เงินทุนภายนอก (ต่างประเทศ)"
        ))
        # 6
        fig.add_trace(go.Scatter(
            x=df7["year"], y=df7["Matching_fund"],
            fill='tozeroy',
            mode='lines',
            line_color='#80DEEA ',
            line=dict(width=0.8),
            name="เงินทุนร่วม"
            ))

        fig.update_layout(
            xaxis_title="<b>ปี พ.ศ.</b>",
            yaxis_title="<b>จำนวนเงิน (บาท)</b>",
            # font=dict(
            #     size=16,
            # )
        )
        fig.update_layout(  # ปรับความสูง ของกราฟให้เต็ม ถ้าใช้ graph object
            margin=dict(t=50),
        )
    
        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)

        return  plot_div

    def graph8(filter_year):  # แสดงกราฟโดนัด ของจำนวน เงินทั้ง 11 หัวข้อ
        
        df = pd.read_csv("""mydj1/static/csv/12types_of_budget.csv""")
        df.reset_index(level=0, inplace=False)
        df = df.rename(columns={"Unnamed: 0" : "budget_year"}, errors="raise")
        re_df =df[df["budget_year"]==int(filter_year)]
        newdf = pd.DataFrame({'BUDGET_TYPE' : ["สกอ-มหาวิทยาลัยวิจัยแห่งชาติ (NRU)"
                                       ,"เงินงบประมาณแผ่นดิน"
                                       ,"เงินกองทุนวิจัยมหาวิทยาลัย"
                                       ,"เงินจากแหล่งทุนภายนอก ในประเทศไทย"
                                       ,"เงินจากแหล่งทุนภายนอก ต่างประเทศ"
                                       ,"เงินรายได้มหาวิทยาลัย"
                                       ,"เงินรายได้คณะ (เงินรายได้)"
                                       ,"เงินรายได้คณะ (กองทุนวิจัย)"
                                       ,"เงินกองทุนวิจัยวิทยาเขต"
                                       ,"เงินรายได้วิทยาเขต"
                                       ,"เงินอุดหนุนโครงการการพัฒนาความปลอดภัยและความมั่นคง"     
                            ]})
        
        newdf["budget"] = 0.0

        for n in range(0,11):   # สร้างใส่ค่าใน column ใหม่
            newdf.budget[n] = re_df[str(n)]

        fig = px.pie(newdf, values='budget', names='BUDGET_TYPE' ,color_discrete_sequence=px.colors.sequential.haline, hole=0.5 ,)
        fig.update_traces(textposition='inside', textfont_size=14)
        # fig.update_traces(hoverinfo="label+percent+name",
        #           marker=dict(line=dict(color='#000000', width=2)))

        fig.update_layout(uniformtext_minsize=12 , uniformtext_mode='hide')  #  ถ้าเล็กกว่า 12 ให้ hide 
        # fig.update_layout(legend=dict(font=dict(size=16))) # font ของ คำอธิบายสีของกราฟ (legend) ด้านข้างซ้าย
        # fig.update_layout(showlegend=False)  # ไม่แสดง legend
        fig.update_layout(legend=dict(orientation="h"))  # แสดง legend ด้านล่างของกราฟ
        fig.update_layout( height=600)
        fig.update_layout( margin=dict(l=30, r=30, t=30, b=5))

        fig.update_layout( annotations=[dict(text="<b> &#3647; {:,.2f}</b>".format(newdf.budget.sum()), x=0.50, y=0.5,  font_color = "black", showarrow=False)]) ##font_size=20,
        # fig.update_traces(hovertemplate='%{name} <br> %{value}') 
         
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        
        return plot_div

    def graph3():

        df = pd.read_csv("""mydj1/static/csv/query_graph3.csv""")

        # df.to_csv ("""mydj1/static/csv/query_graph3.csv""", index = False, header=True)

        fig = px.line(df, x="budget_year", y="budget", color="camp_owner",
        line_shape="spline", render_mode="svg",  )
        fig.update_layout(
            xaxis_title="<b>ปี พ.ศ.</b>",
            yaxis_title="<b>จำนวนเงิน (บาท)</b>",
            # font=dict(
            #     size=16,
            # )
        )
        # fig.update_traces(mode="markers+lines", hovertemplate=None)
        # fig.update_layout(hovermode="x")
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        
        return plot_div

    def graph5():
        sql_cmd =  """SELECT camp_owner, sum(budget) as budget
                    FROM querygraph2
                    where budget_year = YEAR(date_add(NOW(), INTERVAL 543 YEAR))
                    group by 1"""
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string) 

        # df = pd.read_csv("""mydj1/static/csv/querygraph2.csv""")
        
        fig = px.pie(df, values='budget', names='camp_owner')
        fig.update_traces(textposition='inside', textfont_size=14)
        # fig.update_layout( width=900, height=450)
        fig.update_layout(uniformtext_minsize=12 , uniformtext_mode='hide')  #  ถ้าเล็กกว่า 12 ให้ hide 
        # fig.update_layout(legend=dict(font=dict(size=16))) # font ของ คำอธิบายสีของกราฟ (legend) ด้านข้างซ้าย
        # fig.update_layout(showlegend=False)  # ไม่แสดง legend
        fig.update_layout(legend=dict(orientation="h"))  # แสดง legend ด้านล่างของกราฟ
        # fig.update_layout( width=1000, height=485)
        fig.update_layout( margin=dict(l=30, r=30, t=30, b=5))

        fig.update_traces(hoverinfo="label+percent+name",
                  marker=dict(line=dict(color='#000000', width=2)))
        
        # fig.update_layout( height=400, width=520,)
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div

    def graph1():
        df = pd.read_csv("""mydj1/static/csv/query_graph1.csv""")

        fig = make_subplots(rows=1, cols=2,
                            column_widths=[1, 0.5],
                            specs=[[{"type": "bar"},{"type": "table"}]]
                            )

        fig.add_trace(
                        px.bar( df,
                            x = 'budget_year',
                            y = 'budget', 
                       ).data[0],
                       row=1,col=1
        )
              
    

        df['budget'] = df['budget'].apply(moneyformat) #เปลี่ยน format ของ budget เป็นรูปเเบบของเงิน

        fig.add_trace(
                        go.Table( 
                            columnwidth = [140,400],
                            header=dict(values=["<b>Year</b>","<b>Budget<b>"],
                                        fill = dict(color='#C2D4FF'),
                                        align = ['center'] * 10),
                            cells=dict(values=[df.budget_year, df.budget],
                                    fill = dict(color='#F5F8FF'),
                                    align = ['center','right'] * 5)
                                    )
                            , row=1, col=2)

        fig.update_layout(
                        
                        # height=500, width=800,
                        xaxis_title="<b>ปี พ.ศ</b>",
                        yaxis_title="<b>จำนวนเงิน (บาท)</b>")

        fig.update_layout(  # ปรับความสูง ของกราฟให้เต็ม ถ้าใช้ graph object
            margin=dict(t=50),
        )
        
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        
        return plot_div

    def graph2():
        # sql_cmd =  """SELECT * FROM querygraph2 where budget_year < YEAR(date_add(NOW(), INTERVAL 543 YEAR)) """
        # con_string = getConstring('sql')
        # df = pm.execute_query(sql_cmd, con_string) 
        df = pd.read_csv("""mydj1/static/csv/query_graph2.csv""")

        fig = px.bar(df, x="camp_owner", y="budget", color="camp_owner",
            animation_frame="budget_year", animation_group="faculty_owner")

        fig.update_layout(
            
            width=900, height=450)



        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div

    def graph4():

        df = pd.read_csv("""mydj1/static/csv/query_graph4.csv""")

        fig = px.bar(df, x="year", y="n", color="time",  barmode="group" , template='presentation', text='n')

        fig.update_layout(
            title={   #กำหนดให้ title อยู่ตรงกลาง
                'text': "งานวิจัยที่เสร็จทัน และไม่ทันเวลาที่กำหนด",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'}
            ,width=900, height=450,  #ความกว้างความสูง ของกราฟในหน้าต่าง 
            xaxis_title="ปี ค.ศ",
            yaxis_title="จำนวน"
            ,margin=dict(l=100, r=100, t=100, b=100)  # กำหนด left right top bottom ของกราฟในหน้าต่าง 
            ,paper_bgcolor="LightSteelBlue" # กำหนด สี BG 
            # font=dict(
            #     family="Courier New, monospace",
            #     size=18,
            #     color="#7f7f7f"
            )
        fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='crimson', ticklen=10)    #เพิ่มเส้นขีดสีแดง ตามแกน x 
        fig.update_yaxes(ticks="outside", tickwidth=2, tickcolor='crimson', ticklen=10, col=1) #เพิ่มเส้นขีดสีแดง ตามแกน y
        # fig.update_yaxes(automargin=True)    

        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        
        return plot_div

    def graph6():
        sql_cmd =  """select year, n_of_publish  as number_of_publication
                    from importdb_prpm_scopus
                    where year BETWEEN YEAR(date_add(NOW(), INTERVAL 543 YEAR))-10 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))-1"""
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string) 
        
        fig = px.line(df, x="year", y="number_of_publication",
        line_shape="spline", render_mode="svg",  template='plotly_dark' )
        
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        
        return plot_div

    context={
        ###### Head_page ########################    
        'head_page': get_head_page(),
        'now_year' : (datetime.now().year)+543,
        #########################################
        
        'plot1' : graph1(),
        'plot3': graph3(),
        # 'plot4': graph4(),
        'plot5': graph5(),
        # 'plot6': graph6(),
        'plot7': graph7(),
        'plot8': graph8(datetime.now().year+543),

    }
    
    return render(requests, 'importDB/welcome.html', context)
    
def rodReport(request):

     #  Query data from Model
    print(f'pymysql version: {pymysql.__version__}')
    print(f'pandas version: {pd.__version__}')
    print(f'cx_Oracle version: {cx_Oracle.__version__}')
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้  
    
    data = PRPM_v_grt_pj_team_eis.objects.all()  #ดึงข้อมูลจากตาราง  มาทั้งหมด
    return render(request,'importDB/rodreport.html',{'posts':data})

###################################################################
#### ฟังก์ชันหลัก " DUMP " เพื่อ dump ข้อมูลจาก External Data เช่น Oracle ####
#### ฟังก์ชันหลัก " Query " เพื่อ query ข้อมูลจาก MySQL ####
###################################################################

@login_required(login_url='login')
def dump(request):  # ดึงข้อมูล จาก Oracle เข้าสู่ ฐาน Mysql
    print('dumping')
    if request.method == "POST":
        # print(f'pymysql version: {pymysql.__version__}')
        # print(f'pandas version: {pd.__version__}')
        # print(f'cx_Oracle version: {cx_Oracle.__version__}')
        os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้  
        checkpoint = True
        whichrows = ''
        dt = datetime.now()
        timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

        if request.POST['row']=='Dump1':  #project
            checkpoint = dump1()
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row1'

        elif request.POST['row']=='Dump2':  #team
            checkpoint = dump2()
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row2'

        elif request.POST['row']=='Dump3':   #budget
            checkpoint = dump3()
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row3'

        elif request.POST['row']=='Dump4':   #FUND_TYPE
            checkpoint = dump4()
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row4'
        
        elif request.POST['row']=='Dump5':   #assistant
            checkpoint = dump5()
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row5'

        elif request.POST['row']=='Dump6':   #HRIMS
            checkpoint = dump6()
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row6'

        if checkpoint:
            result = 'Dumped'
        else:
            result = 'Cant Dump'
    
        context={
            'result': result,
            'time':datetime.fromtimestamp(timestamp),
            'whichrow' : whichrows
        }

    else :
        context={}

    return render(request,'importDB/dump-data.html',context)

@login_required(login_url='login')
def query(request): # Query ฐานข้อมูล Mysql (เป็น .csv) เพื่อสร้างเป็น กราฟ หรือ แสดงข้อมูล บน tamplate
    # print('dQuery')
    # print(f'pymysql version: {pymysql.__version__}')
    # print(f'pandas version: {pd.__version__}')
    # print(f'cx_Oracle version: {cx_Oracle.__version__}')
    
    if request.method == "POST":
        os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้
        checkpoint = True
        whichrows = ""
        ranking = ""
        
        dt = datetime.now()
        timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

        def moneyformat(x):  # เอาไว้เปลี่ยน format เป็นรูปเงิน
            return "{:,.2f}".format(x)

        def cited_isi():
            path = """importDB"""
            driver = webdriver.Chrome(path+'/chromedriver.exe')  # เปิด chromedriver
            WebDriverWait(driver, 10)
            
            try: 
                # get datafreame by web scraping
                driver.get('http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&SID=D2Ji7v7CLPlJipz1Cc4&search_mode=GeneralSearch')
                wait = WebDriverWait(driver, 10)
                element = wait.until(EC.element_to_be_clickable((By.ID, 'container(input1)')))  # hold by id

                btn1 =driver.find_element_by_id('value(input1)')
                btn1.clear()
                btn1.send_keys("Prince Of Songkla University")
                driver.find_element_by_xpath("//span[@id='select2-select1-container']").click()
                driver.find_element_by_xpath("//input[@class='select2-search__field']").send_keys("Organization-Enhanced")  # key text
                driver.find_element_by_xpath("//span[@class='select2-results']").click() 
                driver.find_element_by_xpath("//span[@class='searchButton']").click()

                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'summary_CitLink')))   # hold by class_name
                driver.find_element_by_class_name('summary_CitLink').click()

                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'select2-selection.select2-selection--single')))
                driver.find_element_by_xpath("//a[@class='snowplow-citation-report']").click() 
                element = wait.until(EC.element_to_be_clickable((By.NAME, 'cr_timespan_submission')))  # hold by name

                # หาค่า citation ของปีปัจจุบันd
                cited1 = driver.find_element_by_id("CR_HEADER_4" ).text
                cited2 = driver.find_element_by_id("CR_HEADER_3" ).text
                h_index = driver.find_element_by_id("H_INDEX" ).text
                
                # หาค่า h_index ของปีปัจจุบัน
                
                cited1 =  cited1.replace(",","")  # ตัด , ในตัวเลขที่ได้มา เช่น 1,000 เป็น 1000
                cited2 =  cited2.replace(",","")

                
                # ใส่ ตัวเลขที่ได้ ลง dataframe
                df1=pd.DataFrame({'year':datetime.now().year+543 , 'cited':cited1}, index=[0])
                df2=pd.DataFrame({'year':datetime.now().year+543-1 , 'cited':cited2}, index=[1])
                df_records = pd.concat([df1,df2],axis = 0) # ต่อ dataframe
                df_records['cited'] = df_records['cited'].astype('int') # เปลี่ยนตัวเลขเป็น int    

                print(df_records)

                return df_records, h_index

            except Exception as e:
                print("Error")
                print(e)
                return None, None

            finally:
                driver.quit()

        def get_new_uni_isi(item, driver, df): # ทำการ ดึงคะเเนน isi ของมหาลัยใหม่ ที่ถูกเพิ่มในฐานข้อมูล admin
            try: 
                driver.get('http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&SID=D2Ji7v7CLPlJipz1Cc4&search_mode=GeneralSearch')
                wait = WebDriverWait(driver, 10)
                element = wait.until(EC.element_to_be_clickable((By.ID, 'container(input1)')))

                btn1 =driver.find_element_by_id('value(input1)')  # เลือกกล่อง input
                btn1.clear() # ลบ ค่าที่อยู่ในกล่องเดิม ที่อาจจะมีอยู่
                btn1.send_keys(item['name_eng'])   # ใส่ค่าเพื่อค้นหาข้อมูล
                driver.find_element_by_xpath("//span[@id='select2-select1-container']").click() # กดปุ่ม
                driver.find_element_by_xpath("//input[@class='select2-search__field']").send_keys("Organization-Enhanced")
                driver.find_element_by_xpath("//span[@class='select2-results']").click()
                driver.find_element_by_xpath("//span[@class='searchButton']").click()

                # กดปุ่ม Analyze Results
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'summary_CitLink')))
                # driver.find_element_by_class_name('summary_CitLink').click()
                # WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, 'd-flex.align-items-center')))
                driver.find_element_by_class_name('summary_CitLink').click()

                # กดปุ่ม Publication Years
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'select2-selection.select2-selection--single')))
                driver.find_element_by_xpath('//*[contains(text(),"Publication Years")]').click()  # กดจากการค้าหา  ด้วย text
        
                # ดึงข้อมูล ในปีปัจุบัน ใส่ใน row1 และ ปัจุบัน -1 ใส่ใน row2
                WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, 'd-flex.align-items-center')))
                # row1 = driver.find_elements_by_class_name("RA-NEWRAresultsEvenRow" ).text.split(' ')
                matched_elements = driver.find_elements_by_class_name("RA-NEWRAresultsEvenRow" )
                texts_1 = []
                for matched_element in matched_elements:
                    text = matched_element.text.split(' ')[:2]
                    texts_1.append(text)
                    # print(texts_1)
                WebDriverWait(driver, 15)  
                matched_elements = driver.find_elements_by_class_name("RA-NEWRAresultsOddRow" )
                texts_2 = []
                for matched_element in matched_elements:
                    text = matched_element.text.split(' ')[:2]
                    texts_2.append(text)

                new_column = pd.DataFrame()
                
                for i in range(len(texts_2)):
                    texts_1[i][1] =  texts_1[i][1].replace(",","")  # ตัด , ในตัวเลขที่ได้มา เช่น 1,000 เป็น 1000
                    texts_2[i][1] =  texts_2[i][1].replace(",","")
                    df1=pd.DataFrame({'year':int(texts_1[i][0])+543 , item['short_name']:texts_1[i][1]}, index=[0])
                    df2=pd.DataFrame({'year':int(texts_2[i][0])+543 , item['short_name']:texts_2[i][1]}, index=[1])
                    temp = pd.concat([df1,df2],axis = 0) # รวมให้เป็น dataframe ชั่วคราว
                    new_column = new_column.append(temp) # ต่อ dataframe ใหม่

                new_column[item['short_name']] = new_column[item['short_name']].astype('int') # เปลี่ยนตัวเลขเป็น int
                new_column = new_column.set_index('year')
                df  = df.join(new_column)  # รวม dataframe เข้าด้วยกัน
            except Exception as e:
                print("Error: ",item['name_eng'])

            return df    

        def isi(): 
            path = """importDB"""
            df = pd.read_csv("""mydj1/static/csv/ranking_isi.csv""", index_col=0)
            flag = False
            col_used = df.columns.tolist()  # เก็บชื่อย่อมหาลัย ที่อยู่ใน ranking_isi.csv ตอนนี้
            # print(path+'/chromedriver.exe')
            driver = webdriver.Chrome(path+'/chromedriver.exe')  # เปิด chromedriver
            # os.chdir(path)  # setpath
            WebDriverWait(driver, 10)
            try:
                data = master_ranking_university_name.objects.all() # ดึงรายละเอียดมหาลัยที่จะค้นหา จากฐานข้อมูล Master
                
                # new_df = pd.DataFrame()
                for item in data.values('short_name','name_eng','flag_used'): # วน for เพื่อตรวจสอบ ว่า มี มหาวิทยาลัยใหม่ ถูกเพิ่ม/หรือ ไม่ได้ใช้ (flag_used = false )มาในฐานข้อมูลหรือไม่
                    if (item['flag_used'] == True) & (item['short_name'] not in col_used) :
                        flag = True  # ธง ตั้งไว้เพื่อ จะตรวจสอบว่าต้อง save csv ตอนท้าย
                        print(f"""There is a new university "{item['name_eng']}", saving isi value of the university to csv.....""")
                        df = get_new_uni_isi(item, driver, df)

                    if (item['flag_used'] == False) & (item['short_name'] in col_used):  # ถ้า มีมหาลัย flag_used == False ทำการลบออกจาก df เดิม
                        flag = True 
                        print(f"""ไม่ได้ใช้เเล้ว คือ :{item['name_eng']} ..... """)
                        df = df.drop([item['short_name']], axis = 1)
                        print(f"""{item['name_eng']} ถูกลบเเล้ว .... .""")

                if flag:  # ทำการบันทึกเข้า csv ถ้าเกิด มี column ใหม่ หรือ ถูกลบ column
                    print("--df--")
                    print(df)
                    ########## save df ISI  to csv ##########      
                    if not os.path.exists("mydj1/static/csv"):
                            os.mkdir("mydj1/static/csv")
                            
                    df.to_csv ("""mydj1/static/csv/ranking_isi.csv""", index = True, header=True)
                    print("ranking_isi is updated")

            
                searches = {}
                for item in data.values('short_name','name_eng','flag_used'):
                    if item['flag_used'] == True:
                        searches.update( {item['short_name'] : item['name_eng']} )

                last_df =pd.DataFrame()    
                driver.get('http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&SID=D2Ji7v7CLPlJipz1Cc4&search_mode=GeneralSearch')
                for key, value in searches.items(): 
                    # print(value)
                    # กำหนด URL ของ ISI
                    driver.get('http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&SID=D2Ji7v7CLPlJipz1Cc4&search_mode=GeneralSearch')
                    wait = WebDriverWait(driver, 10)
                    element = wait.until(EC.element_to_be_clickable((By.ID, 'container(input1)')))

                    btn1 =driver.find_element_by_id('value(input1)')  # เลือกกล่อง input
                    btn1.clear() # ลบ ค่าที่อยู่ในกล่องเดิม ที่อาจจะมีอยู่
                    btn1.send_keys(value)   # ใส่ค่าเพื่อค้นหาข้อมูล
                    driver.find_element_by_xpath("//span[@id='select2-select1-container']").click() # กดปุ่ม
                    driver.find_element_by_xpath("//input[@class='select2-search__field']").send_keys("Organization-Enhanced")
                    driver.find_element_by_xpath("//span[@class='select2-results']").click()
                    driver.find_element_by_xpath("//span[@class='searchButton']").click()

                    # กดปุ่ม Analyze Results
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'summary_CitLink')))
                    # driver.find_element_by_class_name('summary_CitLink').click()
                    # WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, 'd-flex.align-items-center')))
                    driver.find_element_by_class_name('summary_CitLink').click()
        
                    # กดปุ่ม Publication Years
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'select2-selection.select2-selection--single')))
                    driver.find_element_by_xpath('//*[contains(text(),"Publication Years")]').click()  # กดจากการค้าหา  ด้วย text
            
                    # ดึงข้อมูล ในปีปัจุบัน ใส่ใน row1 และ ปัจุบัน -1 ใส่ใน row2
                    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, 'd-flex.align-items-center')))
                    row1 = driver.find_element_by_class_name("RA-NEWRAresultsEvenRow" ).text.split(' ')[:2]
                    WebDriverWait(driver, 15)  
                    row2 = driver.find_element_by_class_name("RA-NEWRAresultsOddRow" ).text.split(' ') [:2]
                    # print(row2)
                    for i in range(len(row2)):
                        row2[i] =  row2[i].replace(",","")  # ตัด , ในตัวเลขที่ได้มา เช่น 1,000 เป็น 1000
                        row1[i] =  row1[i].replace(",","")
                    
                    # ใส่ ตัวเลขที่ได้ ลง dataframe
                    df1=pd.DataFrame({'year':row1[0] , key:row1[1]}, index=[0])
                    df2=pd.DataFrame({'year':row2[0] , key:row2[1]}, index=[1])
                    df_records = pd.concat([df1,df2],axis = 0) # ต่อ dataframe
                    
                    df_records[key] = df_records[key].astype('int') # เปลี่ยนตัวเลขเป็น int
                    if(key=='PSU'):
                        last_df = pd.concat([last_df,df_records], axis= 1)
                    else:
                        last_df = pd.concat([last_df,df_records[key]], axis= 1)
                    

                last_df['year'] = last_df['year'].astype('int')
                last_df['year'] = last_df['year'] + 543
                print("-------isi-------")
                print(last_df)
                print("-----------------")
                return last_df

            except Exception as e:
                print(e)
                return None

            finally:
                driver.quit()

        def get_new_uni_tci(item, driver, df): # ทำการ ดึงคะเเนน tci ของมหาลัยใหม่ ที่ถูกเพิ่มในฐานข้อมูล admin  
            try:
                driver.get('https://tci-thailand.org/wp-content/themes/magazine-style/tci_search/advance_search.html')
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID,'searchBtn')))
                btn1 =driver.find_element_by_class_name('form-control')
                btn1.send_keys(item['name_eng'])

                driver.find_element_by_xpath("//button[@class='btn btn-success']").click()
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME,'fa')))

                elements =driver.find_elements_by_class_name('form-control')
                elements[2].send_keys("OR")
                elements[3].send_keys(item['name_th'])
                elements[4].send_keys("Affiliation")

                driver.find_element_by_xpath("//select[@class='form-control xxx']").click()
                driver.find_element_by_xpath("//option[@value='affiliation']").click()
                WebDriverWait(driver, 10)
                driver.find_element_by_xpath("//button[@id='searchBtn']").click()
                WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.ID,'export_excel_btn')))
                # driver.find_element_by_xpath("//input[@value=' more']").click()
                driver.find_element_by_xpath("//span[@class='right']").click()
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID,'year2001')))
                data = driver.find_element_by_class_name("col-md-3" ).text
                WebDriverWait(driver, 10)
                
                data2 = data[15:]
                st = data2.split('\n')
                years = [int(st[i])+543 for i in range(0, 40, 2)]
                values = [int(st[i][1:][:-1]) for i in range(1, 40, 2)]
                # print(years)
                # print(values)
                
                new_column = pd.DataFrame({"year" : years,
                                        item["short_name"] : values
                                        } )

                new_column = new_column.set_index('year')
                df  = df.join(new_column)  # รวม dataframe เข้าด้วยกัน

            except Exception as e:
                print("Error: ",item['name_eng'])

            return df

        def tci():
            path = """importDB"""
            df = pd.read_csv("""mydj1/static/csv/ranking_tci.csv""", index_col=0)
            flag = False
            col_used = df.columns.tolist()  # เก็บชื่อย่อมหาลัย ที่อยู่ใน ranking_isi.csv ตอนนี้
            try : 
                driver = webdriver.Chrome(path+'/chromedriver.exe')

                data = master_ranking_university_name.objects.all() # ดึงรายละเอียดมหาลัยที่จะค้นหา จากฐานข้อมูล Master
            
                for item in data.values('short_name','name_eng','name_th','flag_used'): # วน for เพื่อตรวจสอบ ว่า มี มหาวิทยาลัยใหม่ ถูกเพิ่ม/หรือ ไม่ได้ใช้ (flag_used = false )มาในฐานข้อมูลหรือไม่
                    if (item['flag_used'] == True) & (item['short_name'] not in col_used) :
                        flag = True  # ธง ตั้งไว้เพื่อ จะตรวจสอบว่าต้อง save csv ตอนท้าย
                        print(f"""There is a new university "{item['name_eng']}", saving isi value of the university to csv.....""")
                        df = get_new_uni_tci(item, driver, df)

                    if (item['flag_used'] == False) & (item['short_name'] in col_used):  # ถ้า มีมหาลัย flag_used == False ทำการลบออกจาก df เดิม
                        flag = True 
                        print(f"""ไม่ได้ใช้เเล้ว คือ :{item['name_eng']} ..... """)
                        df = df.drop([item['short_name']], axis = 1)
                        print(f"""{item['name_eng']} ถูกลบเเล้ว .... .""")

                if flag:  # ทำการบันทึกเข้า csv ถ้าเกิด มี column ใหม่ หรือ ถูกลบ column

                    ########## save df ISI  to csv ##########      
                    if not os.path.exists("mydj1/static/csv"):
                            os.mkdir("mydj1/static/csv")
                            
                    df.to_csv ("""mydj1/static/csv/ranking_tci.csv""", index = True, header=True)
                    print("ranking_tci is updated")

                searches = {} # ตัวแปรเก็บชื่อมหาลัย ที่ต้องการ update ข้อมูลปี ล่าสุด และ ล่าสุด-1
                
                for item in data.values('short_name','name_eng','name_th','flag_used'):
                    if item['flag_used'] == True:
                        searches.update( {item['short_name'] : [item['name_eng'],item['name_th']]} )
                print(searches)
                final_df =pd.DataFrame()   
                
                for key, value in searches.items():  # ทำการวน ดึงค่า tci จากแต่ละมหาลัย ที่อยู่ใน ตัวแปล searches
                    print(value[0])
                    driver.get('https://tci-thailand.org/wp-content/themes/magazine-style/tci_search/advance_search.html')
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID,'searchBtn')))
                    btn1 =driver.find_element_by_class_name('form-control')
                    btn1.send_keys(value[0])

                    driver.find_element_by_xpath("//button[@class='btn btn-success']").click()
                    WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.CLASS_NAME,'fa')))

                    elements =driver.find_elements_by_class_name('form-control')
                    elements[2].send_keys("OR")
                    elements[3].send_keys(value[1])
                    elements[4].send_keys("Affiliation")

                    driver.find_element_by_xpath("//select[@class='form-control xxx']").click()
                    driver.find_element_by_xpath("//option[@value='affiliation']").click()
                    WebDriverWait(driver, 10)
                    driver.find_element_by_xpath("//button[@id='searchBtn']").click()
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID,'export_excel_btn')))
                    data2 = driver.find_element_by_class_name("col-md-3" ).text 
                    df = pd.DataFrame({"year" : [data2[14:].split('\n')[1:3][0], data2[14:].split('\n')[3:5][0] ]
                                                , key : [data2[14:].split('\n')[1:3][1][1:][:-1], data2[14:].split('\n')[3:5][1][1:][:-1]]} )
                    if(key=='PSU'): # ถ้า key = psu ต้องเก็บอีกแแบบ เพราะ เป้นมหาลัยแรก ใน dataframe : final_df
                        final_df = pd.concat([final_df,df], axis= 1)
                    else:
                        final_df = pd.concat([final_df,df[key]], axis= 1)
                    
                    print(final_df)
                    

                final_df['year'] =final_df['year'].astype(int) + 543
                
                for item in data.values('short_name','flag_used'):   # ทำการเปลี่ยน type ให้เป็น int 
                    if item['flag_used'] == True:
                        final_df[item['short_name']] = final_df[item['short_name']].astype(int)
                
                print("--TCI--")
                print(final_df)
                return final_df
            
            except Exception as e:
                print(e)
                return None

            finally:
                driver.quit() 
        
        def get_new_uni_scopus(item , df, apiKey, URL, year): # ทำการ ดึงคะเเนน scopus ของมหาลัยใหม่ ที่ถูกเพิ่มในฐานข้อมูล admin
            new_df = pd.DataFrame()
            final_df = pd.DataFrame()
            
            for y in range(2001,year+1):
                print(item['short_name'],": ",y)
                query = f"{item['af_id']} and PUBYEAR IS {y}"
                # defining a params dict for the parameters to be sent to the API 
                PARAMS = {'query':query,'apiKey':apiKey}  

                # sending get request and saving the response as response object 
                r = requests.get(url = URL, params = PARAMS) 

                # extracting data in json format 
                data = r.json() 

                # convert the datas to dataframe
                new_df=pd.DataFrame({'year':y+543, item['short_name']:data['search-results']['opensearch:totalResults']}, index=[0])
            
                new_df[item['short_name']] = new_df[item['short_name']].astype('int')
                
                final_df = pd.concat([final_df,new_df])

            final_df = final_df.set_index('year')
            df  = df.join(final_df)  # รวม dataframe เข้าด้วยกัน
            
            return df

        def sco(year):
            
            URL = "https://api.elsevier.com/content/search/scopus"
            
            # params given here 
            con_file = open("importDB\config.json")
            config = json.load(con_file)
            con_file.close()
            year2 = year-1
            
            apiKey = config['apikey']

            df = pd.read_csv("""mydj1/static/csv/ranking_scopus.csv""", index_col=0)
            flag = False
            col_used = df.columns.tolist()  # เก็บชื่อย่อมหาลัย ที่อยู่ใน ranking_isi.csv ตอนนี้ 

            data = master_ranking_university_name.objects.all() # ดึงรายละเอียดมหาลัยที่จะค้นหา จากฐานข้อมูล Master

            for item in data.values('short_name','name_eng','af_id','flag_used'): # วน for เพื่อตรวจสอบ ว่า มี มหาวิทยาลัยใหม่ ถูกเพิ่ม/หรือ ไม่ได้ใช้ (flag_used = false )มาในฐานข้อมูลหรือไม่
                if (item['flag_used'] == True) & (item['short_name'] not in col_used) :
                    flag = True  # ธง ตั้งไว้เพื่อ จะตรวจสอบว่าต้อง save csv ตอนท้าย
                    print(f"""There is a new university "{item['name_eng']}", saving isi value of the university to csv.....""")
                    df = get_new_uni_scopus(item , df, apiKey, URL , year)
                    print(df)

                if (item['flag_used'] == False) & (item['short_name'] in col_used):  # ถ้า มีมหาลัย flag_used == False ทำการลบออกจาก df เดิม
                    flag = True 
                    print(f"""ไม่ได้ใช้เเล้ว คือ :{item['name_eng']} ..... """)
                    df = df.drop([item['short_name']], axis = 1)
                    print(f"""{item['name_eng']} ถูกลบเเล้ว .... .""")

            if flag:  # ทำการบันทึกเข้า csv ถ้าเกิด มี column ใหม่ หรือ ถูกลบ column
                ########## save df ISI  to csv ##########      
                if not os.path.exists("mydj1/static/csv"):
                        os.mkdir("mydj1/static/csv")
                        
                df.to_csv ("""mydj1/static/csv/ranking_scopus.csv""", index = True, header=True)
                print("ranking_scopus is updated")

            searches = {}
            for item in data.values('short_name','af_id', 'flag_used'):
                if item['flag_used'] == True:
                    searches.update( {item['short_name'] : item['af_id']} )  

            last_df =pd.DataFrame()

            try:
                for key, value in searches.items():  
                    query = f"{value} and PUBYEAR IS {year}"
                    # defining a params dict for the parameters to be sent to the API 
                    PARAMS = {'query':query,'apiKey':apiKey}  

                    # sending get request and saving the response as response object 
                    r = requests.get(url = URL, params = PARAMS) 

                    # extracting data in json format 
                    data1= r.json() 

                    query = f"{value} and PUBYEAR IS {year2}"
                        
                    # defining a params dict for the parameters to be sent to the API 
                    PARAMS = {'query':query,'apiKey':apiKey}  

                    # sending get request and saving the response as response object 
                    r = requests.get(url = URL, params = PARAMS) 

                    # extracting data in json format 
                    data2 = r.json() 
                    # convert the datas to dataframe
                    df1=pd.DataFrame({'year':year+543, key:data1['search-results']['opensearch:totalResults']}, index=[0])
                    df2=pd.DataFrame({'year':year2+543 , key:data2['search-results']['opensearch:totalResults']}, index=[1])
                    df_records = pd.concat([df1,df2],axis = 0)
                    df_records[key]= df_records[key].astype('int')
                    
                    if(key=='PSU'):  # ถ้าใส่ข้อมูลใน last_df ครั้งแรก ต้องใส่ df_records แบบไม่ใส่ key
                        last_df = pd.concat([last_df,df_records], axis= 1)
                    else:            # ใส่ครั้งต่อๆ ไป 
                        last_df = pd.concat([last_df,df_records[key]], axis= 1)

                print("--scopus--")
                print(last_df)
                return last_df

            except Exception as e:
                print(e)
                return None

        def get_df_by_rows(rows):
            categories = list()
            i = 0
            for row in rows:
                j = 0
                for j, c in enumerate(row.text):
                    if c.isdigit():
                        break
                categories.append(tuple((row.text[0:j-1],row.text[j:])))

            for index, item in enumerate(categories):
                itemlist = list(item)
                itemlist[1] = itemlist[1].split(" ",1)[0].replace(",","")
                item = tuple(itemlist)
                categories[index] = item

            return(categories)    

        def chrome_driver_get_research_areas_ISI():
            path = """importDB"""
            driver = webdriver.Chrome(path+'/chromedriver.exe')  # เปิด chromedriver
            WebDriverWait(driver, 10)
            try: 
                # get datafreame by web scraping
                driver.get('http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&SID=D2Ji7v7CLPlJipz1Cc4&search_mode=GeneralSearch')
                wait = WebDriverWait(driver, 10)
                element = wait.until(EC.element_to_be_clickable((By.ID, 'container(input1)')))  # hold by id

                btn1 =driver.find_element_by_id('value(input1)')
                btn1.clear()
                btn1.send_keys("Prince Of Songkla University")
                driver.find_element_by_xpath("//span[@id='select2-select1-container']").click()
                driver.find_element_by_xpath("//input[@class='select2-search__field']").send_keys("Organization-Enhanced")  # key text
                driver.find_element_by_xpath("//span[@class='select2-results']").click() 
                driver.find_element_by_xpath("//span[@class='searchButton']").click()

                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'summary_CitLink')))   # hold by class_name
                driver.find_element_by_class_name('summary_CitLink').click()

                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'column-box.ra-bg-color'))) 
                driver.find_element_by_xpath('//*[contains(text(),"Research Areas")]').click()  # กดจากการค้าหา  ด้วย text

                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@class="bold-text" and contains(text(), "Treemap")]')))  # hold until find text by CLASSNAME

                evens = driver.find_elements_by_class_name("RA-NEWRAresultsEvenRow" )
                odds = driver.find_elements_by_class_name("RA-NEWRAresultsOddRow" )

                categories_evens = get_df_by_rows(evens)
                categories_odds = get_df_by_rows(odds)

                df1 = pd.DataFrame(categories_evens, columns=['categories', 'count'])
                df2 = pd.DataFrame(categories_odds, columns=['categories', 'count'])

                df = pd.concat([df1,df2], axis = 0)
                df['count'] = df['count'].astype('int')
                df = df.sort_values(by='count', ascending=False)

            except Exception as e :
                df = None
                print('Something went wrong :', e)
            
            return df

        def chrome_driver_get_catagories_ISI():
            path = """importDB"""
            driver = webdriver.Chrome(path+'/chromedriver.exe')  # เปิด chromedriver
            WebDriverWait(driver, 10)
            try: 
                # get datafreame by web scraping
                driver.get('http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&SID=D2Ji7v7CLPlJipz1Cc4&search_mode=GeneralSearch')
                wait = WebDriverWait(driver, 10)
                element = wait.until(EC.element_to_be_clickable((By.ID, 'container(input1)')))  # hold by id

                btn1 =driver.find_element_by_id('value(input1)')
                btn1.clear()
                btn1.send_keys("Prince Of Songkla University")
                driver.find_element_by_xpath("//span[@id='select2-select1-container']").click()
                driver.find_element_by_xpath("//input[@class='select2-search__field']").send_keys("Organization-Enhanced")  # key text
                driver.find_element_by_xpath("//span[@class='select2-results']").click() 
                driver.find_element_by_xpath("//span[@class='searchButton']").click()

                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'summary_CitLink')))   # hold by class_name
                driver.find_element_by_class_name('summary_CitLink').click()

                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'column-box.ra-bg-color'))) 
                driver.find_element_by_xpath('//*[contains(text(),"Web of Science Categories")]').click()  # กดจากการค้าหา  ด้วย text

                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@class="bold-text" and contains(text(), "Treemap")]')))  # hold until find text by CLASSNAME

                evens = driver.find_elements_by_class_name("RA-NEWRAresultsEvenRow" )
                odds = driver.find_elements_by_class_name("RA-NEWRAresultsOddRow" )

                categories_evens = get_df_by_rows(evens)
                categories_odds = get_df_by_rows(odds)

                df1 = pd.DataFrame(categories_evens, columns=['categories', 'count'])
                df2 = pd.DataFrame(categories_odds, columns=['categories', 'count'])

                df = pd.concat([df1,df2], axis = 0)
                df['count'] = df['count'].astype('int')
                df = df.sort_values(by='count', ascending=False)

            except Exception as e :
                df = None
                print('Something went wrong :', e)
            
            return df

        if request.POST['row']=='Query1': # 12 types of budget, budget_of_fac 
            checkpoint = query1()
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row1'

        elif request.POST['row']=='Query2': # รายได้ในประเทศ รัฐ/เอกชน
            checkpoint = query2()
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row2'

        elif request.POST['row']=='Query3': # Query รูปกราฟ ที่จะแสดงใน ตารางของ tamplate revenues.html
            checkpoint = query3()
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row3'
            
        elif request.POST['row']=='Query4': #ตารางแหล่งทุนภายนอก exFund.html
            checkpoint = query4() 
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row4'
            
        elif request.POST['row']=='Query5': #ตาราง marker * และ ** ของแหล่งทุน
            checkpoint = query5() 
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row5'

        elif request.POST['row']=='Query6': # ISI SCOPUS TCI 
            ranking, checkpoint = query6() 
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row6'

        elif request.POST['row']=='Query7': # Head Page
            checkpoint = query7() 
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row7'
        
        elif request.POST['row']=='Query8': # web of science Research Areas   
            checkpoint = query8() 
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row8'
        
        elif request.POST['row']=='Query9': # web of science catagories    
            checkpoint = query9() 
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row9'

        elif request.POST['row']=='Query10': # Citation ISI and H-index  
            checkpoint = query10() 
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row10'
            
        elif request.POST['row']=='Query11': # จำนวนผู้วิจัยที่ได้รับทุน 
            checkpoint = query11() 
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row11'  
        
        elif request.POST['row']=='Query12': #จำนวนผู้วิจัยหลัก
            checkpoint = query12() 
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row12'

        elif request.POST['row']=='Query13': # หา Parameter ของ ARIMA Model
            checkpoint = query13() 
            dt = datetime.now()
            timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
            whichrows = 'row13'

        
        if checkpoint == 'chk_ranking':
            result = ""+ranking
        elif checkpoint:
            result = 'Dumped'
        else:
            result = "Can't Dump"
        
        context={
            'result': result,
            'time':datetime.fromtimestamp(timestamp),
            'whichrow' : whichrows
        }

    else:
        context={}
    return render(request,'importDB/query-data.html',context)


###################################################################
#### "function DUMP" เพื่อ dump ข้อมูลจาก External Data เช่น Oracle ####
###################################################################
def dump1():
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดง/บันทึก ข้อความเป็น ภาษาไทยได้
    print("-"*20)
    print("Starting DUMP#1 ...")
    checkpoint = True
    try:
        
        sql_cmd =  """select * from research60.v_grt_project_eis 
                    WHERE psu_project_id not in ('X541090' ,'X541067','X551445')
                """
        DIALECT = 'oracle'
        SQL_DRIVER = 'cx_oracle'
        USERNAME = 'pnantipat' #enter your username
        PASSWORD = urllib.parse.quote_plus('sfdgr4g4') #enter your password
        HOST = 'delita.psu.ac.th' #enter the oracle db host url
        PORT = 1521 # enter the oracle port number
        SERVICE = 'delita.psu.ac.th' # enter the oracle db service name
        ENGINE_PATH_WIN_AUTH = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + PASSWORD +'@' + HOST + ':' + str(PORT) + '/?service_name=' + SERVICE

        engine = create_engine(ENGINE_PATH_WIN_AUTH, encoding="latin1" ,max_identifier_length=128)
        df = pd.read_sql_query(sql_cmd, engine)
        # df = pm.execute_query(sql_cmd, con_string)
        

        ###################################################
        # save path
        uid = 'root'
        pwd = ''
        host = 'localhost'
        port = 3306
        db = 'mydj2'
        con_string = f'mysql+pymysql://{uid}:{pwd}@{host}:{port}/{db}'

        pm.save_to_db('importdb_prpm_v_grt_project_eis', con_string, df)
        
        print("Ending DUMP#1 ...")
        return checkpoint

    except Exception as e :
        checkpoint = False
        print('Something went wrong :', e)
        return checkpoint

def dump2():
    print("-"*20)
    print("Starting DUMP#2 ...")
    checkpoint = True
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้
    
    try:
        sql_cmd =""" select * from research60.v_grt_pj_team_eis"""
        DIALECT = 'oracle'
        SQL_DRIVER = 'cx_oracle'
        USERNAME = 'pnantipat' #enter your username
        PASSWORD = urllib.parse.quote_plus('sfdgr4g4') #enter your password
        HOST = 'delita.psu.ac.th' #enter the oracle db host url
        PORT = 1521 # enter the oracle port number
        SERVICE = 'delita.psu.ac.th' # enter the oracle db service name
        ENGINE_PATH_WIN_AUTH = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + PASSWORD +'@' + HOST + ':' + str(PORT) + '/?service_name=' + SERVICE

        engine = create_engine(ENGINE_PATH_WIN_AUTH, encoding="latin1" ,max_identifier_length=128 )
        df = pd.read_sql_query(sql_cmd, engine)
        
        ###########################################################
        ##### save data ที่ไม่ได้ clean ลง ฐานข้อมูล mysql ####
        ############################################################
        uid2 = 'root'
        pwd2 = ''
        host2 = 'localhost'
        port2 = 3306
        db2 = 'mydj2'
        con_string = f'mysql+pymysql://{uid2}:{pwd2}@{host2}:{port2}/{db2}'

        pm.save_to_db('importdb_prpm_v_grt_pj_team_eis', con_string, df)

        ###########################################################
        ##### clean data ที่ sum(lu_percent) = 0 ให้ เก็บค่าเฉลี่ยแทน ####
        ############################################################
        
        for i in range(1,14):
            df2 = pd.read_csv(r"""mydj1/static/csv/clean_lu/edit_lu_percet_"""+str(i)+""".csv""")
            df.loc[df['psu_project_id'].isin(df2['psu_project_id']), ['lu_percent']] = 100/i
        
        pm.save_to_db('cleaned_prpm_team_eis', con_string, df)
        #############################################################
        print("Ending DUMP#2 ...")
        return checkpoint

    except Exception as e :
        checkpoint = False
        print('Something went wrong :', e)
        return checkpoint

def dump3():
    print("-"*20)
    print("Starting DUMP#3 ...")
    checkpoint = True
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้
    
    try:
        sql_cmd =  """SELECT 
                    *
                FROM research60.v_grt_pj_budget_eis
                """
        DIALECT = 'oracle'
        SQL_DRIVER = 'cx_oracle'
        USERNAME = 'pnantipat' #enter your username
        PASSWORD = urllib.parse.quote_plus('sfdgr4g4') #enter your password
        HOST = 'delita.psu.ac.th' #enter the oracle db host url
        PORT = 1521 # enter the oracle port number
        SERVICE = 'delita.psu.ac.th' # enter the oracle db service name
        ENGINE_PATH_WIN_AUTH = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + PASSWORD +'@' + HOST + ':' + str(PORT) + '/?service_name=' + SERVICE

        engine = create_engine(ENGINE_PATH_WIN_AUTH, encoding="latin1" ,max_identifier_length=128)
        df = pd.read_sql_query(sql_cmd, engine)
        # df = pm.execute_query(sql_cmd, con_string)
        
        ###################################################
        # save path
        uid2 = 'root'
        pwd2 = ''
        host2 = 'localhost'
        port2 = 3306
        db2 = 'mydj2'
        con_string2 = f'mysql+pymysql://{uid2}:{pwd2}@{host2}:{port2}/{db2}'

        pm.save_to_db('importdb_prpm_v_grt_pj_budget_eis', con_string2, df)

        ###########################################################
        ##### clean data ที่ budget_source_group_id = Null ให้ เก็บค่า 11 ####
        ############################################################
        df.loc[df['budget_source_group_id'].isna(), ['budget_source_group_id']] = 11
        
        pm.save_to_db('cleaned_prpm_budget_eis', con_string2, df)
        #############################################################   
        print("Ending DUMP#3 ...")
        return checkpoint

    except Exception as e :
        checkpoint = False
        print('Something went wrong :', e)
        return checkpoint

def dump4():
    print("-"*20)
    print("Starting DUMP#4 ...")
    checkpoint = True
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้
    try:
        
        sql_cmd =  """SELECT 
                    *
                FROM RESEARCH60.R_FUND_TYPE
                """

        con_string = getConstring('oracle')
        engine = create_engine(con_string, encoding="latin1" ,max_identifier_length=128)
        df = pd.read_sql_query(sql_cmd, engine)
        # df = pm.execute_query(sql_cmd, con_string)
        

        ###################################################
        # save path
        con_string2 = getConstring('sql')
        pm.save_to_db('importdb_prpm_r_fund_type', con_string2, df)

        #############################################################   
        print("Ending DUMP#4 ...")
        return checkpoint

    except Exception as e :
        checkpoint = False
        print('Something went wrong :', e)
        return checkpoint

def dump5():
    print("-"*20)
    print("Starting DUMP#5 ...")
    checkpoint = True
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้
    
    try:
        
        sql_cmd =  """SELECT 
                    *
                FROM research60.v_grt_pj_assistant_eis
                """

        con_string = getConstring('oracle')
        engine = create_engine(con_string, encoding="latin1" ,max_identifier_length=128)
        df = pd.read_sql_query(sql_cmd, engine)
        # df = pm.execute_query(sql_cmd, con_string)
        
        print(df.head())
        ###################################################
        # save path
        con_string2 = getConstring('sql')
        pm.save_to_db('importdb_prpm_v_grt_pj_assistant_eis', con_string2, df)

        ########################################################
        print("Ending DUMP#5 ...")
        return checkpoint

    except Exception as e :
        checkpoint = False
        print('Something went wrong :', e)
        return checkpoint

def dump6():
    print("-"*20)
    print("Starting DUMP#6 ...")
    checkpoint = True
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้
    try:
        
        sql_cmd =  """SELECT
                            AW_NO_ID,
                            STAFF_ID,
                            FNAME_THAI,
                            LNAME_THAI,
                            FNAME_ENG,
                            LNAME_ENG,
                            POS_NAME_THAI,
                            TYPE_ID,
                            CORRESPONDING,
                            END_YEAR,
                            MTYPE_ID,
                            MTYPE_NAME,
                            JDB_ID,
                            JDB_NAME,
                            AT_PERCENT,
                            BUDGET_AMOUNT,
                            REVENUE_AMOUNT,
                            DOMESTIC_AMOUNT,
                            FOREIGN_AMOUNT,
                            PAYBACK_AMOUNT,
                            FAC_ID,
                            DEPT_ID
                            
                        FROM
                            HRMIS.V_AW_FOR_RANKING
                                            """

        con_string = getConstring('oracle')
        engine = create_engine(con_string, encoding="latin1" ,max_identifier_length=128)
        df = pd.read_sql_query(sql_cmd, engine)
        # print(df.head())
        # df = pm.execute_query(sql_cmd, con_string)
    
        # cleaning
        print("Start Cleaning")  # ลบ ค่า 0 ใน column ข้างล่างนี้ ให้เป็น none
        df['budget_amount'] = df['budget_amount'].apply(lambda x: None if x == 0 else x) 
        df['revenue_amount'] = df['revenue_amount'].apply(lambda x: None if x == 0 else x) 
        df['domestic_amount'] = df['domestic_amount'].apply(lambda x: None if x == 0 else x) 
        df['foreign_amount'] = df['foreign_amount'].apply(lambda x: None if x == 0 else x) 
        df['payback_amount'] = df['payback_amount'].apply(lambda x: None if x == 0 else x) 
        print("End Cleaning")

        ###################################################
        # save path
        con_string2 = getConstring('sql')
        pm.save_to_db('importdb_hrmis_v_aw_for_ranking', con_string2, df)

        ########################################################
        print("Ending DUMP#6 ...")
        return checkpoint

    except Exception as e :
        checkpoint = False
        print('Something went wrong :', e)
        return checkpoint


###################################################################
#### "function เสริม" เพื่อช่วยในการ query ข้อมูล ที่จะเเสดงใน dashboard####
###################################################################
def moneyformat(x):  # เอาไว้เปลี่ยน format เป็นรูปเงิน
    return "{:,.2f}".format(x)

def cited_isi():
    path = """importDB"""

    try:
        driver = webdriver.Chrome(path+'/chromedriver.exe')  # เปิด chromedriver
    except Exception as e:
        print(e,"โปรดทำการ update เวอร์ชั่นใหม่ของ File chromedriver.exe")
        print("https://chromedriver.chromium.org/downloads")
        return None

    WebDriverWait(driver, 10)
    
    try: 
        # get datafreame by web scraping
        driver.get('http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&SID=D2Ji7v7CLPlJipz1Cc4&search_mode=GeneralSearch')
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.ID, 'container(input1)')))  # hold by id

        btn1 =driver.find_element_by_id('value(input1)')
        btn1.clear()
        btn1.send_keys("Prince Of Songkla University")
        driver.find_element_by_xpath("//span[@id='select2-select1-container']").click()
        driver.find_element_by_xpath("//input[@class='select2-search__field']").send_keys("Organization-Enhanced")  # key text
        driver.find_element_by_xpath("//span[@class='select2-results']").click() 
        driver.find_element_by_xpath("//span[@class='searchButton']").click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'link-style1')))  # hold by id
        driver.find_element_by_xpath("//a[@class='link-style1']").click()

        # ติ๊ก เลือก 10 ปี 
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, 'more_title')))
        driver.find_element_by_xpath("//input[@id='PY_1']").click()
        driver.find_element_by_xpath("//input[@id='PY_2']").click()
        driver.find_element_by_xpath("//input[@id='PY_3']").click()
        driver.find_element_by_xpath("//input[@id='PY_4']").click()
        driver.find_element_by_xpath("//input[@id='PY_5']").click()
        driver.find_element_by_xpath("//input[@id='PY_6']").click()
        driver.find_element_by_xpath("//input[@id='PY_7']").click()
        driver.find_element_by_xpath("//input[@id='PY_8']").click()
        driver.find_element_by_xpath("//input[@id='PY_9']").click()
        driver.find_element_by_xpath("//input[@id='PY_10']").click()

        # กดปุ่ม Refine
        WebDriverWait(driver, 15)
        driver.find_element_by_xpath("//button[@title='Refine' and contains(text(), 'Refine') ]").click()

        # กดปุ่ม Create Citation Report
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, 'snowplow-citation-report.citation-report-summary-link')))
        driver.find_element_by_xpath("//span[contains(text(), 'Create Citation Report')]").click()

        # หาค่า citation ของปีล่าสุด และ ปี ล่าสุด - 1 
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, 'select2-selection__rendered')))
        cited1 = driver.find_element_by_id("CR_HEADER_4" ).text
        cited2 = driver.find_element_by_id("CR_HEADER_3" ).text
        
        # หาค่า h_index ของปีปัจจุบัน
        h_index = driver.find_element_by_id("H_INDEX" ).text

        # หา avg cite per item ของปีปัจจุบัน
        avg_per_item = driver.find_element_by_class_name("minor.commafy.last" ).text

        # ตัด , ในตัวเลขที่ได้มา เช่น 1,000 เป็น 1000
        cited1 =  cited1.replace(",","")  
        cited2 =  cited2.replace(",","")
        h_index =  h_index.replace(",","")
        
        # หาปี ล่าสุด และ ล่าสุด-1
        tag_years = driver.find_element_by_xpath("//div[@class='CitReportTotalRow1']")
        years = tag_years.text.split("\n")[1].split(" ")
        year = int(years[-1])+543
        previous_year = int(years[-2])+543
        
        # ใส่ ตัวเลขที่ได้ ลง dataframe
        df1=pd.DataFrame({'year':year , 'cited':cited1}, index=[0])
        df2=pd.DataFrame({'year':previous_year , 'cited':cited2}, index=[1])
        df_records = pd.concat([df1,df2],axis = 0)
        df_records['cited'] = df_records['cited'].astype('int') # เปลี่ยนตัวเลขเป็น int    

        print(df_records)

        return df_records, h_index, avg_per_item

    except Exception as e:
        print("Error")
        print(e)
        return None, None

    finally:
        driver.quit()

def get_new_uni_isi(item, driver, df): # ทำการ ดึงคะเเนน isi ของมหาลัยใหม่ ที่ถูกเพิ่มในฐานข้อมูล admin
    try: 
        driver.get('http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&SID=D2Ji7v7CLPlJipz1Cc4&search_mode=GeneralSearch')
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.ID, 'container(input1)')))

        btn1 =driver.find_element_by_id('value(input1)')  # เลือกกล่อง input
        btn1.clear() # ลบ ค่าที่อยู่ในกล่องเดิม ที่อาจจะมีอยู่
        btn1.send_keys(item['name_eng'])   # ใส่ค่าเพื่อค้นหาข้อมูล
        driver.find_element_by_xpath("//span[@id='select2-select1-container']").click() # กดปุ่ม
        driver.find_element_by_xpath("//input[@class='select2-search__field']").send_keys("Organization-Enhanced")
        driver.find_element_by_xpath("//span[@class='select2-results']").click()
        driver.find_element_by_xpath("//span[@class='searchButton']").click()

        # กดปุ่ม Analyze Results
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'summary_CitLink')))
        # driver.find_element_by_class_name('summary_CitLink').click()
        # WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, 'd-flex.align-items-center')))
        driver.find_element_by_class_name('summary_CitLink').click()

        # กดปุ่ม Publication Years
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'select2-selection.select2-selection--single')))
        driver.find_element_by_xpath('//*[contains(text(),"Publication Years")]').click()  # กดจากการค้าหา  ด้วย text

        # ดึงข้อมูล ในปีปัจุบัน ใส่ใน row1 และ ปัจุบัน -1 ใส่ใน row2
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, 'd-flex.align-items-center')))
        # row1 = driver.find_elements_by_class_name("RA-NEWRAresultsEvenRow" ).text.split(' ')
        matched_elements = driver.find_elements_by_class_name("RA-NEWRAresultsEvenRow" )
        texts_1 = []
        for matched_element in matched_elements:
            text = matched_element.text.split(' ')[:2]
            texts_1.append(text)
            # print(texts_1)
        WebDriverWait(driver, 15)  
        matched_elements = driver.find_elements_by_class_name("RA-NEWRAresultsOddRow" )
        texts_2 = []
        for matched_element in matched_elements:
            text = matched_element.text.split(' ')[:2]
            texts_2.append(text)

        new_column = pd.DataFrame()
        
        for i in range(len(texts_2)):
            texts_1[i][1] =  texts_1[i][1].replace(",","")  # ตัด , ในตัวเลขที่ได้มา เช่น 1,000 เป็น 1000
            texts_2[i][1] =  texts_2[i][1].replace(",","")
            df1=pd.DataFrame({'year':int(texts_1[i][0])+543 , item['short_name']:texts_1[i][1]}, index=[0])
            df2=pd.DataFrame({'year':int(texts_2[i][0])+543 , item['short_name']:texts_2[i][1]}, index=[1])
            temp = pd.concat([df1,df2],axis = 0) # รวมให้เป็น dataframe ชั่วคราว
            new_column = new_column.append(temp) # ต่อ dataframe ใหม่

        new_column[item['short_name']] = new_column[item['short_name']].astype('int') # เปลี่ยนตัวเลขเป็น int
        new_column = new_column.set_index('year')
        df  = df.join(new_column)  # รวม dataframe เข้าด้วยกัน
    except Exception as e:
        print("Error: ",item['name_eng'])

    return df    

def isi(): 
    path = """importDB"""
    df = pd.read_csv("""mydj1/static/csv/ranking_isi.csv""", index_col=0)
    flag = False
    col_used = df.columns.tolist()  # เก็บชื่อย่อมหาลัย ที่อยู่ใน ranking_isi.csv ตอนนี้
   
    # print(path+'/chromedriver.exe')
    try:
        driver = webdriver.Chrome(path+'/chromedriver.exe')  # เปิด chromedriver
    except Exception as e:
        print(e,"โปรดทำการ update เวอร์ชั่นใหม่ของ File chromedriver.exe")
        print("https://chromedriver.chromium.org/downloads")
        return None

    # os.chdir(path)  # setpath
    WebDriverWait(driver, 10)
    try:
        data = master_ranking_university_name.objects.all() # ดึงรายละเอียดมหาลัยที่จะค้นหา จากฐานข้อมูล Master
        
        # new_df = pd.DataFrame()
        for item in data.values('short_name','name_eng','flag_used'): # วน for เพื่อตรวจสอบ ว่า มี มหาวิทยาลัยใหม่ ถูกเพิ่ม/หรือ ไม่ได้ใช้ (flag_used = false )มาในฐานข้อมูลหรือไม่
            if ((item['flag_used'] == True) | (item['flag_used'] == '1')) & (item['short_name'] not in col_used) :
                flag = True  # ธง ตั้งไว้เพื่อ จะตรวจสอบว่าต้อง save csv ตอนท้าย
                print(f"""There is a new university "{item['name_eng']}", saving isi value of the university to csv.....""")
                df = get_new_uni_isi(item, driver, df)

            if ((item['flag_used'] == False) | (item['flag_used'] == '0')) & (item['short_name'] in col_used):  # ถ้า มีมหาลัย flag_used == False ทำการลบออกจาก df เดิม
                flag = True 
                print(f"""ไม่ได้ใช้เเล้ว คือ :{item['name_eng']} ..... """)
                df = df.drop([item['short_name']], axis = 1)
                print(f"""{item['name_eng']} ถูกลบเเล้ว .... .""")

        if flag:  # ทำการบันทึกเข้า csv ถ้าเกิด มี column ใหม่ หรือ ถูกลบ column
            print("--df--")
            print(df)
            ########## save df ISI  to csv ##########      
            if not os.path.exists("mydj1/static/csv"):
                    os.mkdir("mydj1/static/csv")
                    
            df.to_csv ("""mydj1/static/csv/ranking_isi.csv""", index = True, header=True)
            print("ranking_isi is updated")

        searches = {}
        for item in data.values('short_name','name_eng','flag_used'):
            if ((item['flag_used'] == True) | (item['flag_used'] == '1')):
                searches.update( {item['short_name'] : item['name_eng']} )
        
        last_df =pd.DataFrame()    
        
        for key, value in searches.items():
            # key = "CU" 
            # value = "Chulalongkorn University"
            print(key)
            driver.get('http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&SID=D2Ji7v7CLPlJipz1Cc4&search_mode=GeneralSearch')
            # กำหนด URL ของ ISI
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.element_to_be_clickable((By.ID, 'container(input1)')))

            btn1 =driver.find_element_by_id('value(input1)')  # เลือกกล่อง input
            btn1.clear() # ลบ ค่าที่อยู่ในกล่องเดิม ที่อาจจะมีอยู่
            btn1.send_keys(value)   # ใส่ค่าเพื่อค้นหาข้อมูล
            driver.find_element_by_xpath("//span[@id='select2-select1-container']").click() # กดปุ่ม
            driver.find_element_by_xpath("//input[@class='select2-search__field']").send_keys("Organization-Enhanced")
            driver.find_element_by_xpath("//span[@class='select2-results']").click()
            driver.find_element_by_xpath("//span[@class='searchButton']").click()

            # กดปุ่ม Analyze Results
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'summary_CitLink')))
            # driver.find_element_by_class_name('summary_CitLink').click()
            # WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, 'd-flex.align-items-center')))
            driver.find_element_by_class_name('summary_CitLink').click()

            # กดปุ่ม Publication Years
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'select2-selection.select2-selection--single')))
            driver.find_element_by_xpath('//*[contains(text(),"Publication Years")]').click()  # กดจากการค้าหา  ด้วย text

            # ดึงข้อมูล ในปีปัจุบัน ใส่ใน row1 และ ปัจุบัน -1 ใส่ใน row2
            WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, 'd-flex.align-items-center')))
            all_even_rows = driver.find_elements_by_class_name("RA-NEWRAresultsEvenRow" )
            WebDriverWait(driver, 15)  
            all_odd_rows = driver.find_elements_by_class_name("RA-NEWRAresultsOddRow" )
            WebDriverWait(driver, 15)  

            # กำหนดตัวแปรปีปัจจุบัน
            now_year = int(datetime.now().year)
            result_row_2 = []
            result_row_1 = []

            # ดึง isi value ใน ปีปัจจุบัน และ ปีปัจจุบัน - 1 
            for i in  range(len(all_even_rows)):
                if( (now_year == int(all_even_rows[i].text[:4])) | (now_year-1 == int(all_even_rows[i].text[:4]))):
                    result_row_1 = all_even_rows[i].text.split()[:2]
                    break


            for i in  range(len(all_odd_rows)):
                if( (now_year == int(all_odd_rows[i].text[:4])) | (now_year-1 == int(all_odd_rows[i].text[:4]))):
                    result_row_2 = all_odd_rows[i].text.split()[:2]
                    break

            # ตัด , ในตัวเลขที่ได้มา เช่น 1,000 เป็น 1000
            for i in range(len(result_row_2)):
                result_row_2[i] =  result_row_2[i].replace(",","")  # ตัด , ในตัวเลขที่ได้มา เช่น 1,000 เป็น 1000
                result_row_1[i] =  result_row_1[i].replace(",","")

            # ใส่ ตัวเลขที่ได้ ลง dataframe
            df1=pd.DataFrame({'year':result_row_1[0] , key:result_row_1[1]}, index=[0])
            df2=pd.DataFrame({'year':result_row_2[0] , key:result_row_2[1]}, index=[1])
            df_records = pd.concat([df1,df2],axis = 0) # ต่อ dataframe
            
            df_records[key] = df_records[key].astype('int') # เปลี่ยนตัวเลขเป็น int
            df_records = df_records.sort_values(by=['year'], ascending=False).reset_index(drop=True) # sort ให้ ปี ปัจจุบัน อยู่บน
            print(df_records)
            if(key=='PSU'):
                last_df = pd.concat([last_df,df_records], axis= 1)
            else:
                last_df = pd.concat([last_df,df_records[key]], axis= 1)

            print(last_df)

        last_df['year'] = last_df['year'].astype('int')
        last_df['year'] = last_df['year'] + 543
        print("-------isi-------")
        print(last_df)
        print("-----------------")
        return last_df

    except Exception as e:
        print(e)
        return None

    finally:
        driver.quit()

def get_new_uni_tci(item, driver, df): # ทำการ ดึงคะเเนน tci ของมหาลัยใหม่ ที่ถูกเพิ่มในฐานข้อมูล admin  
    try:
        driver.get('https://tci-thailand.org/wp-content/themes/magazine-style/tci_search/advance_search.html')
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID,'searchBtn')))
        btn1 =driver.find_element_by_class_name('form-control')
        btn1.send_keys(item['name_eng'])

        driver.find_element_by_xpath("//button[@class='btn btn-success']").click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME,'fa')))

        elements =driver.find_elements_by_class_name('form-control')
        elements[2].send_keys("OR")
        elements[3].send_keys(item['name_th'])
        elements[4].send_keys("Affiliation")

        driver.find_element_by_xpath("//select[@class='form-control xxx']").click()
        driver.find_element_by_xpath("//option[@value='affiliation']").click()
        WebDriverWait(driver, 10)
        driver.find_element_by_xpath("//button[@id='searchBtn']").click()
        WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.ID,'export_excel_btn')))
        # driver.find_element_by_xpath("//input[@value=' more']").click()
        driver.find_element_by_xpath("//span[@class='right']").click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID,'year2001')))
        data = driver.find_element_by_class_name("col-md-3" ).text
        WebDriverWait(driver, 10)
        
        data2 = data[15:]
        st = data2.split('\n')
        years = [int(st[i])+543 for i in range(0, 40, 2)]
        values = [int(st[i][1:][:-1]) for i in range(1, 40, 2)]
        # print(years)
        # print(values)
        
        new_column = pd.DataFrame({"year" : years,
                                item["short_name"] : values
                                } )

        new_column = new_column.set_index('year')
        df  = df.join(new_column)  # รวม dataframe เข้าด้วยกัน

    except Exception as e:
        print("Error: ",item['name_eng'])

    return df

def tci():
    path = """importDB"""
    df = pd.read_csv("""mydj1/static/csv/ranking_tci.csv""", index_col=0)
    flag = False
    col_used = df.columns.tolist()  # เก็บชื่อย่อมหาลัย ที่อยู่ใน ranking_isi.csv ตอนนี้

    try:
        driver = webdriver.Chrome(path+'/chromedriver.exe')  # เปิด chromedriver
    except Exception as e:
        print(e,"โปรดทำการ update เวอร์ชั่นใหม่ของ File chromedriver.exe")
        print("https://chromedriver.chromium.org/downloads")
        return None

    try : 
        data = master_ranking_university_name.objects.all() # ดึงรายละเอียดมหาลัยที่จะค้นหา จากฐานข้อมูล Master
        
        for item in data.values('short_name','name_eng','name_th','flag_used'): # วน for เพื่อตรวจสอบ ว่า มี มหาวิทยาลัยใหม่ ถูกเพิ่ม/หรือ ไม่ได้ใช้ (flag_used = false )มาในฐานข้อมูลหรือไม่
            if ((item['flag_used'] == True) | (item['flag_used'] == '1')) & (item['short_name'] not in col_used) :
                flag = True  # ธง ตั้งไว้เพื่อ จะตรวจสอบว่าต้อง save csv ตอนท้าย
                print(f"""There is a new university "{item['name_eng']}", saving isi value of the university to csv.....""")
                df = get_new_uni_tci(item, driver, df)

            if ((item['flag_used'] == False) | (item['flag_used'] == '0')) & (item['short_name'] in col_used):  # ถ้า มีมหาลัย flag_used == False ทำการลบออกจาก df เดิม
                flag = True 
                print(f"""ไม่ได้ใช้เเล้ว คือ :{item['name_eng']} ..... """)
                df = df.drop([item['short_name']], axis = 1)
                print(f"""{item['name_eng']} ถูกลบเเล้ว .... .""")

        if flag:  # ทำการบันทึกเข้า csv ถ้าเกิด มี column ใหม่ หรือ ถูกลบ column

            ########## save df ISI  to csv ##########      
            if not os.path.exists("mydj1/static/csv"):
                    os.mkdir("mydj1/static/csv")
                    
            df.to_csv ("""mydj1/static/csv/ranking_tci.csv""", index = True, header=True)
            print("ranking_tci is updated")

        searches = {} # ตัวแปรเก็บชื่อมหาลัย ที่ต้องการ update ข้อมูลปี ล่าสุด และ ล่าสุด-1
        
        for item in data.values('short_name','name_eng','name_th','flag_used'):
            if ((item['flag_used'] == True) | (item['flag_used'] == '1')):
                searches.update( {item['short_name'] : [item['name_eng'],item['name_th']]} )
        print(searches)
        final_df =pd.DataFrame()   
        
        for key, value in searches.items():  # ทำการวน ดึงค่า tci จากแต่ละมหาลัย ที่อยู่ใน ตัวแปล searches
            print(value[0])
            driver.get('https://tci-thailand.org/wp-content/themes/magazine-style/tci_search/advance_search.html')
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID,'searchBtn')))
            btn1 =driver.find_element_by_class_name('form-control')
            btn1.send_keys(value[0])

            driver.find_element_by_xpath("//button[@class='btn btn-success']").click()
            WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.CLASS_NAME,'fa')))

            elements =driver.find_elements_by_class_name('form-control')
            elements[2].send_keys("OR")
            elements[3].send_keys(value[1])
            elements[4].send_keys("Affiliation")

            driver.find_element_by_xpath("//select[@class='form-control xxx']").click()
            driver.find_element_by_xpath("//option[@value='affiliation']").click()
            WebDriverWait(driver, 10)
            driver.find_element_by_xpath("//button[@id='searchBtn']").click()
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID,'export_excel_btn')))
            data2 = driver.find_element_by_class_name("col-md-3" ).text 
            df = pd.DataFrame({"year" : [data2[14:].split('\n')[1:3][0], data2[14:].split('\n')[3:5][0] ]
                                        , key : [data2[14:].split('\n')[1:3][1][1:][:-1], data2[14:].split('\n')[3:5][1][1:][:-1]]} )
            if(key=='PSU'): # ถ้า key = psu ต้องเก็บอีกแแบบ เพราะ เป้นมหาลัยแรก ใน dataframe : final_df
                final_df = pd.concat([final_df,df], axis= 1)
            else:
                final_df = pd.concat([final_df,df[key]], axis= 1)
            
            print(final_df)
            

        final_df['year'] =final_df['year'].astype(int) + 543
        
        for item in data.values('short_name','flag_used'):   # ทำการเปลี่ยน type ให้เป็น int 
            if ((item['flag_used'] == True) | (item['flag_used'] == '1')):
                final_df[item['short_name']] = final_df[item['short_name']].astype(int)
        
        print("--TCI--")
        print(final_df)
        return final_df
    
    except Exception as e:
        print(e)
        return None

    finally:
        driver.quit() 

def get_new_uni_scopus(item , df, apiKey, URL, year): # ทำการ ดึงคะเเนน scopus ของมหาลัยใหม่ ที่ถูกเพิ่มในฐานข้อมูล admin
    new_df = pd.DataFrame()
    final_df = pd.DataFrame()
    
    for y in range(2001,year+1):
        print(item['short_name'],": ",y)
        query = f"{item['af_id']} and PUBYEAR IS {y}"
        # defining a params dict for the parameters to be sent to the API 
        PARAMS = {'query':query,'apiKey':apiKey}  

        # sending get request and saving the response as response object 
        r = requests.get(url = URL, params = PARAMS) 

        # extracting data in json format 
        data = r.json() 

        # convert the datas to dataframe
        new_df=pd.DataFrame({'year':y+543, item['short_name']:data['search-results']['opensearch:totalResults']}, index=[0])
    
        new_df[item['short_name']] = new_df[item['short_name']].astype('int')
        
        final_df = pd.concat([final_df,new_df])

    final_df = final_df.set_index('year')
    df  = df.join(final_df)  # รวม dataframe เข้าด้วยกัน
    
    return df

def sco(year):
    
    URL = "https://api.elsevier.com/content/search/scopus"
    
    # params given here 
    con_file = open("importDB\config.json")
    config = json.load(con_file)
    con_file.close()
    year2 = year-1
    
    apiKey = config['apikey']

    df = pd.read_csv("""mydj1/static/csv/ranking_scopus.csv""", index_col=0)
    flag = False
    col_used = df.columns.tolist()  # เก็บชื่อย่อมหาลัย ที่อยู่ใน ranking_isi.csv ตอนนี้ 

    data = master_ranking_university_name.objects.all() # ดึงรายละเอียดมหาลัยที่จะค้นหา จากฐานข้อมูล Master

    for item in data.values('short_name','name_eng','af_id','flag_used'): # วน for เพื่อตรวจสอบ ว่า มี มหาวิทยาลัยใหม่ ถูกเพิ่ม/หรือ ไม่ได้ใช้ (flag_used = false )มาในฐานข้อมูลหรือไม่
        if ((item['flag_used'] == True) | (item['flag_used'] == '1')) & (item['short_name'] not in col_used) :
            flag = True  # ธง ตั้งไว้เพื่อ จะตรวจสอบว่าต้อง save csv ตอนท้าย
            print(f"""There is a new university "{item['name_eng']}", saving isi value of the university to csv.....""")
            df = get_new_uni_scopus(item , df, apiKey, URL , year)
            print(df)

        if ((item['flag_used'] == False) | (item['flag_used'] == '0')) & (item['short_name'] in col_used):  # ถ้า มีมหาลัย flag_used == False ทำการลบออกจาก df เดิม
            flag = True 
            print(f"""ไม่ได้ใช้เเล้ว คือ :{item['name_eng']} ..... """)
            df = df.drop([item['short_name']], axis = 1)
            print(f"""{item['name_eng']} ถูกลบเเล้ว .... .""")

    if flag:  # ทำการบันทึกเข้า csv ถ้าเกิด มี column ใหม่ หรือ ถูกลบ column
        ########## save df ISI  to csv ##########      
        if not os.path.exists("mydj1/static/csv"):
                os.mkdir("mydj1/static/csv")
                
        df.to_csv ("""mydj1/static/csv/ranking_scopus.csv""", index = True, header=True)
        print("ranking_scopus is updated")

    searches = {}
    for item in data.values('short_name','af_id', 'flag_used'):
        if ((item['flag_used'] == True) | (item['flag_used'] == '1')):
            searches.update( {item['short_name'] : item['af_id']} )  

    last_df =pd.DataFrame()

    try:
        for key, value in searches.items():  
            query = f"{value} and PUBYEAR IS {year}"
            # defining a params dict for the parameters to be sent to the API 
            PARAMS = {'query':query,'apiKey':apiKey}  

            # sending get request and saving the response as response object 
            r = requests.get(url = URL, params = PARAMS) 

            # extracting data in json format 
            data1= r.json() 

            query = f"{value} and PUBYEAR IS {year2}"
                
            # defining a params dict for the parameters to be sent to the API 
            PARAMS = {'query':query,'apiKey':apiKey}  

            # sending get request and saving the response as response object 
            r = requests.get(url = URL, params = PARAMS) 

            # extracting data in json format 
            data2 = r.json() 
            # convert the datas to dataframe
            df1=pd.DataFrame({'year':year+543, key:data1['search-results']['opensearch:totalResults']}, index=[0])
            df2=pd.DataFrame({'year':year2+543 , key:data2['search-results']['opensearch:totalResults']}, index=[1])
            df_records = pd.concat([df1,df2],axis = 0)
            df_records[key]= df_records[key].astype('int')
            
            if(key=='PSU'):  # ถ้าใส่ข้อมูลใน last_df ครั้งแรก ต้องใส่ df_records แบบไม่ใส่ key
                last_df = pd.concat([last_df,df_records], axis= 1)
            else:            # ใส่ครั้งต่อๆ ไป 
                last_df = pd.concat([last_df,df_records[key]], axis= 1)

        print("--scopus--")
        print(last_df)
        return last_df

    except Exception as e:
        print(e)
        return None

def get_df_by_rows(rows):
    categories = list()
    i = 0
    for row in rows:
        j = 0
        for j, c in enumerate(row.text):
            if c.isdigit():
                break
        categories.append(tuple((row.text[0:j-1],row.text[j:])))

    for index, item in enumerate(categories):
        itemlist = list(item)
        itemlist[1] = itemlist[1].split(" ",1)[0].replace(",","")
        item = tuple(itemlist)
        categories[index] = item

    return(categories)    

def chrome_driver_get_research_areas_ISI(driver):
    
    try: 
        # get datafreame by web scraping
        driver.get('http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&SID=D2Ji7v7CLPlJipz1Cc4&search_mode=GeneralSearch')
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.ID, 'container(input1)')))  # hold by id

        btn1 =driver.find_element_by_id('value(input1)')
        btn1.clear()
        btn1.send_keys("Prince Of Songkla University")
        driver.find_element_by_xpath("//span[@id='select2-select1-container']").click()
        driver.find_element_by_xpath("//input[@class='select2-search__field']").send_keys("Organization-Enhanced")  # key text
        driver.find_element_by_xpath("//span[@class='select2-results']").click() 
        driver.find_element_by_xpath("//span[@class='searchButton']").click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'summary_CitLink')))   # hold by class_name
        driver.find_element_by_class_name('summary_CitLink').click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'column-box.ra-bg-color'))) 
        driver.find_element_by_xpath('//*[contains(text(),"Research Areas")]').click()  # กดจากการค้าหา  ด้วย text

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@class="bold-text" and contains(text(), "Treemap")]')))  # hold until find text by CLASSNAME

        evens = driver.find_elements_by_class_name("RA-NEWRAresultsEvenRow" )
        odds = driver.find_elements_by_class_name("RA-NEWRAresultsOddRow" )

        categories_evens = get_df_by_rows(evens)
        categories_odds = get_df_by_rows(odds)

        df1 = pd.DataFrame(categories_evens, columns=['categories', 'count'])
        df2 = pd.DataFrame(categories_odds, columns=['categories', 'count'])

        df = pd.concat([df1,df2], axis = 0)
        df['count'] = df['count'].astype('int')
        df = df.sort_values(by='count', ascending=False)

    except Exception as e :
        df = None
        print('Something went wrong :', e)
    
    return df

def chrome_driver_get_catagories_ISI(driver):
   
    try: 
        # get datafreame by web scraping
        driver.get('http://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&SID=D2Ji7v7CLPlJipz1Cc4&search_mode=GeneralSearch')
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.ID, 'container(input1)')))  # hold by id

        btn1 =driver.find_element_by_id('value(input1)')
        btn1.clear()
        btn1.send_keys("Prince Of Songkla University")
        driver.find_element_by_xpath("//span[@id='select2-select1-container']").click()
        driver.find_element_by_xpath("//input[@class='select2-search__field']").send_keys("Organization-Enhanced")  # key text
        driver.find_element_by_xpath("//span[@class='select2-results']").click() 
        driver.find_element_by_xpath("//span[@class='searchButton']").click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'summary_CitLink')))   # hold by class_name
        driver.find_element_by_class_name('summary_CitLink').click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'column-box.ra-bg-color'))) 
        driver.find_element_by_xpath('//*[contains(text(),"Web of Science Categories")]').click()  # กดจากการค้าหา  ด้วย text

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@class="bold-text" and contains(text(), "Treemap")]')))  # hold until find text by CLASSNAME

        evens = driver.find_elements_by_class_name("RA-NEWRAresultsEvenRow" )
        odds = driver.find_elements_by_class_name("RA-NEWRAresultsOddRow" )

        categories_evens = get_df_by_rows(evens)
        categories_odds = get_df_by_rows(odds)

        df1 = pd.DataFrame(categories_evens, columns=['categories', 'count'])
        df2 = pd.DataFrame(categories_odds, columns=['categories', 'count'])

        df = pd.concat([df1,df2], axis = 0)
        df['count'] = df['count'].astype('int')
        df = df.sort_values(by='count', ascending=False)

    except Exception as e :
        df = None
        print('Something went wrong :', e)
    
    return df

################################################################################################
#### "function ย่อย" ในการ query ข้อมูล ที่จะเเสดงใน dashboard หรือ html โดย จะถูกเรียกใช้จากฟังก์ชั่นหลัก####
################################################################################################
def query1(): # 12 types of budget, budget_of_fac
    print("-"*20)
    print("Starting Query#1 ...")
    checkpoint = True
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้
    fiscal_year = get_fiscal_year() # ปีงบประมาณ
    print("ปีงบประมาณ",fiscal_year)
    try:   
        sql_cmd =  """with temp1 as ( 
                        select psu_project_id, budget_year, budget_source_group_id, sum(budget_amount) as budget_amount
                        from cleaned_prpm_budget_eis
                        where budget_group = 4 
                        group by 1, 2,3
                        order by 1
                    ),
                    
                    temp2 as (
                        select psu_project_id, user_full_name_th, camp_name_thai, fac_name_thai,research_position_id,research_position_th ,lu_percent
                        from cleaned_prpm_team_eis
                        where psu_staff = "Y" 
                        order by 1
                    ),
                    
                    temp3 as (
                        select psu_project_id, fund_budget_year as submit_year
                        from importdb_prpm_v_grt_project_eis
                    ),
                    
                    temp4 as (
            
                        select t1.psu_project_id,t3.submit_year, t1.budget_year, budget_source_group_id, budget_amount, user_full_name_th, camp_name_thai,fac_name_thai, research_position_th,lu_percent, lu_percent/100*budget_amount as final_budget
                        from temp1 as t1
                        join temp2 as t2 on t1.psu_project_id = t2.psu_project_id
                        join temp3 as t3 on t1.psu_project_id = t3.psu_project_id
                        where 
                            submit_year > 2553 and 
                            research_position_id <> 2 
                        order by 2
                    ),

                    temp5 as (
                                            
                            select  sg1.budget_source_group_id,sg1.budget_source_group_th, budget_year,camp_name_thai, fac_name_thai, sum(final_budget) as sum_final_budget
                            from temp4 
                            join importdb_budget_source_group as sg1 on temp4.budget_source_group_id = sg1.budget_source_group_id
                            group by 1,2,3,4,5
                            order by 1
                    )
                            
                        select budget_year, budget_source_group_id,budget_source_group_th, sum(sum_final_budget) as sum_final_budget
                    from temp5
                    where budget_year between """+str(fiscal_year-9)+""" and """+str(fiscal_year)+"""
                    group by 1,2,3 """

        con_string = getConstring('sql')

        df = pm.execute_query(sql_cmd, con_string)
        print(df)
        ############## build dataframe for show in html ##################
        index_1 = df["budget_year"].unique()
        df2 = pd.DataFrame(columns=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],index = index_1)  
 
        for index, row in df.iterrows():
            df2[int(row['budget_source_group_id'])][row["budget_year"]] = row['sum_final_budget']
 
        df2 = df2.fillna(0.0)
        df2 = df2.sort_index(ascending=False)
        df2 = df2.head(10).sort_index()
            
        
        ########## save to csv ตาราง เงิน 12 ประเภท ##########      
        if not os.path.exists("mydj1/static/csv"):
                os.mkdir("mydj1/static/csv")
                
        df2.to_csv ("""mydj1/static/csv/12types_of_budget.csv""", index = True, header=True)
        print ("Data#1 is saved")
        #################################################
        ################# save ตาราง แยกคณะ #############
        #################################################
        sql_cmd =  """WITH temp1 AS (
                            SELECT
                                psu_project_id,
                                budget_year,
                                budget_source_group_id,
                                sum( budget_amount ) AS budget_amount 
                            FROM
                                cleaned_prpm_budget_eis 
                            WHERE
                                budget_group = 4 
                            GROUP BY 1, 2, 3 
                            ORDER BY 1 
                                ),
                                temp2 AS ( SELECT psu_project_id, user_full_name_th, camp_name_thai, fac_name_thai, research_position_id, research_position_th, lu_percent FROM cleaned_prpm_team_eis WHERE psu_staff = "Y" ORDER BY 1 ),
                                temp3 AS ( SELECT psu_project_id, fund_budget_year AS submit_year FROM importdb_prpm_v_grt_project_eis ),
                                temp4 AS (
                            SELECT
                                t1.psu_project_id,
                                t3.submit_year,
                                t1.budget_year,
                                budget_source_group_id,
                                budget_amount,
                                user_full_name_th,
                                camp_name_thai,
                                fac_name_thai,
                                research_position_th,
                                lu_percent,
                                lu_percent / 100 * budget_amount AS final_budget 
                            FROM
                                temp1 AS t1
                                JOIN temp2 AS t2 ON t1.psu_project_id = t2.psu_project_id
                                JOIN temp3 AS t3 ON t1.psu_project_id = t3.psu_project_id 
                            WHERE
                                submit_year > 2553 
                                AND research_position_id <> 2 
                            ORDER BY 2 
                                ),
                                temp5 AS (
                            SELECT
                                sg1.budget_source_group_id,
                                sg1.budget_source_group_th,
                                budget_year,
                                camp_name_thai,
                                fac_name_thai,
                                sum( final_budget ) AS sum_final_budget 
                            FROM
                                temp4
                                JOIN importdb_budget_source_group AS sg1 ON temp4.budget_source_group_id = sg1.budget_source_group_id 
                            GROUP BY 1, 2, 3, 4, 5 
                            ORDER BY
                                1 
                                ) SELECT
                                budget_year,
                                A.budget_source_group_id,
                                A.budget_source_group_th,
                                B.type,
                                camp_name_thai,
                                fac_name_thai,
                                sum( sum_final_budget ) AS sum_final_budget 
                            FROM
                                temp5 AS A
                                JOIN importdb_budget_source_group AS B ON A.budget_source_group_id = B.budget_source_group_id 
                            where budget_year between """+str(fiscal_year-9)+""" and """+str(fiscal_year)+"""
                            GROUP BY 1, 2, 3, 4, 5, 6
                                """

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)
        df.to_csv ("""mydj1/static/csv/budget_of_fac.csv""", index = False, header=True)
    
        print ("Data#2 is saved")
        print("Ending Query#1 ...")
        return checkpoint

    except Exception as e :
        checkpoint = False
        print('At Query#1: Something went wrong :', e)
        return checkpoint

def query2(): # รายได้ในประเทศ รัฐ/เอกชน
    print("-"*20)
    print("Starting Query#2 ...")
    checkpoint = True
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้
    fiscal_year = get_fiscal_year() # ปีงบประมาณ
    print("ปีงบประมาณ",fiscal_year)

    try:      
        sql_cmd = """with temp1 as ( 
                        select psu_project_id, budget_year, budget_source_group_id, sum(budget_amount) as budget_amount
                        from cleaned_prpm_budget_eis
                        where budget_group = 4 
                              and budget_source_group_id = 3
                        group by 1, 2,3 
                        order by 1
                    ),
                    
                    temp2 as (
                        select psu_project_id, user_full_name_th, camp_name_thai, fac_name_thai,research_position_id,research_position_th ,lu_percent
                        from cleaned_prpm_team_eis
                        where psu_staff = "Y" 
                        order by 1
                    ),
                    
                    temp3 as (
                        select A.psu_project_id, A.fund_budget_year as submit_year, A.fund_type_id, A.fund_type_th, B.fund_type_group, C.fund_type_group_th
                                                    from importdb_prpm_v_grt_project_eis as A
                                                    left join importdb_prpm_r_fund_type as B on A.fund_type_id = B.fund_type_id
                                                    left join fund_type_group as C on B.fund_type_group = C.fund_type_group_id
                    )
                                        
                                            
                select t1.budget_year,fund_type_group, fund_type_group_th, camp_name_thai,fac_name_thai,lu_percent, lu_percent/100*budget_amount as final_budget
                from temp1 as t1
                join temp2 as t2 on t1.psu_project_id = t2.psu_project_id
                join temp3 as t3 on t1.psu_project_id = t3.psu_project_id
                where budget_year between """+str(fiscal_year-9)+""" and """+str(fiscal_year)+"""
                        and submit_year > 2553 
                        and research_position_id <> 2
                        
                order by 1
                    
                            """

        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)
        
        ########## save to csv ตาราง เงิน 11 ประเภท ##########      
        if not os.path.exists("mydj1/static/csv"):
                os.mkdir("mydj1/static/csv")

        df.to_csv("""mydj1/static/csv/gover&comp.csv""", index = True, header=True)

        print ("Data#1 is saved")
        print("Ending Query#2 ...")
        return checkpoint

    except Exception as e :
        checkpoint = False
        print('At Query#2: Something went wrong :', e)    
        return checkpoint

def query3(): # Query รูปกราฟ ที่จะแสดงใน ตารางของ tamplate revenues.html
    print("-"*20)
    print("Starting Query#3 ...")
    checkpoint = True
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้
    fiscal_year = get_fiscal_year() # ปีงบประมาณ
    print("ปีงบประมาณ",fiscal_year)
    try:
        ### 11 กราฟ ในหัวข้อ 1 - 11  หรือ 12 ที่ไม่ระบุที่มา
        FUND_SOURCES = ["0","1","2","3","4","5","6","7","8","9","10","11"]  # ระบุหัว column ทั้ง 12 ห้วข้อใหญ๋

        df = pd.read_csv("""mydj1/static/csv/12types_of_budget.csv""", index_col=0)
        # now = datetime.now()
        now_year = fiscal_year # ปีงบประมาณ
        temp = 0 
        for i, index in enumerate(df.index):  # temp เพื่อเก็บ ว่า ปีปัจจุบัน อยุ่ใน row ที่เท่าไร
            if index == now_year:
                temp = i+1
        i= 1
        for FUND_SOURCE in FUND_SOURCES:
            i = i +1
            print(i)
            df2 = df[FUND_SOURCE][:temp-1].to_frame()   # กราฟเส้นทึบ
            df3 = df[FUND_SOURCE][temp-2:temp].to_frame()  # กราฟเส้นประ
            # df4 = df['11'][:10-(now_year-2563)].to_frame() # กราฟ ของ แหล่งงบประมาณที่ไม่ระบุ (สีเทา)
            df4 = df['11'][:].to_frame() # กราฟ ของ แหล่งงบประมาณที่ไม่ระบุ (สีเทา)
            print(df4)
            
            # กราฟสีเทา
            fig = go.Figure(data=go.Scatter(x=df4.index, y=df4['11']
                                    ,line=dict( width=2 ,color='#D5DBDB') )
            ,
            layout= go.Layout( xaxis={
                                            'zeroline': False,
                                            'showgrid': False,
                                            'visible': False,},
                                    yaxis={
                                            'showgrid': False,
                                            'showline': False,
                                            'zeroline': False,
                                            'visible': False,
                                    })
                        )
            
            print('เส้นสีเทา เสร็จ',i)
            # กราฟ เส้นประ
            fig.add_trace(go.Scatter(x=df3.index, y=df3[FUND_SOURCE]
                                    ,line=dict( width=2, dash='dot',color='royalblue') )
                                )

            # กราฟ สีน้ำเงิน
            fig.add_trace(go.Scatter(x=df2.index, y=df2[FUND_SOURCE] ,line=dict( color='royalblue' ))
                                )
        
            fig.update_layout(showlegend=False)
            fig.update_layout( width=100, height=55, plot_bgcolor = "#fff")
            fig.update_layout( margin=dict(l=0, r=0, t=0, b=0))
            plot_div = plot(fig, output_type='div', include_plotlyjs=False, config =  {'displayModeBar': False} )
            
            
            df4 = df[FUND_SOURCE][:temp].to_frame() # เพื่อดึงตั้งแต่ row 0
            
            if FUND_SOURCE == "11":
                FUND_SOURCE = "13"  # เปลี่ยนเป็น 13 เพราะ 11 คือ เงินภายใน จากหน่วยงานรัฐ เดียวจะซ้ำกัน
                df4 = df4.rename(columns={"11": "13"})
                
            # save to csv
            if not os.path.exists("mydj1/static/csv"):
                    os.mkdir("mydj1/static/csv")       
            df4.to_csv ("""mydj1/static/csv/table_"""+FUND_SOURCE+""".csv""", index = True, header=True)
            
            # write an img
            if not os.path.exists("mydj1/static/img"):
                os.mkdir("mydj1/static/img")
            fig.write_image("""mydj1/static/img/fig_"""+FUND_SOURCE+""".png""")

            

        ##########################################
        ### 2 กราฟย่อย ใน หัวข้อ 3.1 รัฐ และ 3.2 เอกชน
        ###########################################
        df = pd.read_csv("""mydj1/static/csv/gover&comp.csv""", index_col=0)

        df2 = df[df['fund_type_group'] == 1]
        df2 = df2.groupby(["budget_year"])['final_budget'].sum()
        df2 = df2.to_frame()

        df3 = df[df['fund_type_group'] == 2]
        df3 = df3.groupby(["budget_year"])['final_budget'].sum()
        df3 = df3.to_frame()

        df = pd.merge(df2,df3,on='budget_year',how='left')
        df = df.fillna(0)
        df = df.rename(columns={"final_budget_x": "11", "final_budget_y": "12"})

        for i, index in enumerate(df.index): #  ต้องรู้ index เพราะว่า ข้อมูลอาจมีน้อยกว่า 10 ปีย้อนหลัง คือ มีเเค่ 3 ปีเริ่มต้น
            if index == now_year:
                temp = i+1

        FUND_SOURCES2 = ["11","12"]
        for FUND_SOURCE2 in FUND_SOURCES2:
            
            df2 = df[FUND_SOURCE2][:temp-1].to_frame()   # กราฟเส้นทึบ
            df3 = df[FUND_SOURCE2][temp-2:temp].to_frame()  # กราฟเส้นประ

            fig = go.Figure(data=go.Scatter(x=df2.index, y=df2[FUND_SOURCE2],line=dict( color='royalblue')), layout= go.Layout( xaxis={
                                            'zeroline': False,
                                            'showgrid': False,
                                            'visible': False,},
                                    yaxis={
                                            'showgrid': False,
                                            'showline': False,
                                            'zeroline': False,
                                            'visible': False,
                                    }))

            #### กราฟเส้นประ ###
            fig.add_trace(go.Scatter(x=df3.index, y=df3[FUND_SOURCE2]
                    ,line=dict( width=2, dash='dot',color='royalblue') )
                )

            fig.update_layout(showlegend=False)
            fig.update_layout( width=100, height=55, plot_bgcolor = "#fff")
            fig.update_layout( margin=dict(l=0, r=0, t=0, b=0))

            plot_div = plot(fig, output_type='div', include_plotlyjs=False, config =  {'displayModeBar': False} )
            
            if not os.path.exists("mydj1/static/img"):
                os.mkdir("mydj1/static/img")
            fig.write_image("""mydj1/static/img/fig_"""+FUND_SOURCE2+""".png""")
            
                # save to csv
            if not os.path.exists("mydj1/static/csv"):
                    os.mkdir("mydj1/static/csv")       
            df[FUND_SOURCE2].to_csv ("""mydj1/static/csv/table_"""+FUND_SOURCE2+""".csv""", index = True, header=True)
        

        ##########################################
        ### 2 กราฟย่อย รวมเงินจากภายนอก และรวมเงินจากภายใน
        ###########################################
                
        df = pd.read_csv("""mydj1/static/csv/12types_of_budget.csv""")
        df.reset_index(level=0, inplace=False)
        df = df.rename(columns={"Unnamed: 0" : "budget_year","0": "col0", "1": "col1", "2": "col2",
                    "3": "col3", "4": "col4", "5": "col5",
                    "6": "col6", "7": "col7", "8": "col8",
                    "9": "col9", "10": "col10", "11": "col11"}
                    , errors="raise")
        
        list_in=['col0','col1','col3','col4','col10']
        list_out=['col2','col5','col6','col7','col8','col9']

        result_sum = pd.DataFrame()
        for y in range(now_year-9,now_year+1):
            
            df2 = df[df["budget_year"]== int(y)]
                
            result_in = df2[list_in].sum(axis=1)
            
            result_out = df2[list_out].sum(axis=1)
            
            result_in = result_in.iloc[0]
            
            result_out = result_out.iloc[0]

            
            re_df = {'year' : y, 
                    'sum_national' : result_in, 
                    'sum_international' : result_out,  
                    }
            result_sum = result_sum.append(re_df, ignore_index=True)
            
        
        result_sum['year'] = result_sum['year'].astype(int)
        
        #################
        #### เงินภายใน####

        #### กราฟเส้นทึบ ###
        fig = go.Figure(data=go.Scatter(x=result_sum['year'][:9], y=result_sum['sum_national'][:9],line=dict( color='royalblue')), layout= go.Layout( xaxis={
                                            'zeroline': False,
                                            'showgrid': False,
                                            'visible': False,},
                                    yaxis={
                                            'showgrid': False,
                                            'showline': False,
                                            'zeroline': False,
                                            'visible': False,
                                    }))

        #### กราฟเส้นประ ###
        fig.add_trace(go.Scatter(x=result_sum['year'][8:], y=result_sum['sum_national'][8:]
                ,line=dict( width=2, dash='dot',color='royalblue') )
            )

        fig.update_layout(showlegend=False)
        fig.update_layout( width=100, height=55, plot_bgcolor = "#fff")
        fig.update_layout( margin=dict(l=0, r=0, t=0, b=0))

        plot_div = plot(fig, output_type='div', include_plotlyjs=False, config =  {'displayModeBar': False} )
        
        if not os.path.exists("mydj1/static/img"):
            os.mkdir("mydj1/static/img")
        fig.write_image("""mydj1/static/img/fig_sum_national.png""")
        
        
        #### เงินภายนอก
        ##################
        #### กราฟเส้นทึบ ###
        fig = go.Figure(data=go.Scatter(x=result_sum['year'][:9], y=result_sum['sum_international'][:9],line=dict( color='royalblue')), layout= go.Layout( xaxis={
                                            'zeroline': False,
                                            'showgrid': False,
                                            'visible': False,},
                                    yaxis={
                                            'showgrid': False,
                                            'showline': False,
                                            'zeroline': False,
                                            'visible': False,
                                    }))
        
        #### กราฟเส้นประ ###
        fig.add_trace(go.Scatter(x=result_sum['year'][8:], y=result_sum['sum_international'][8:]
                ,line=dict( width=2, dash='dot',color='royalblue') )
            )

        fig.update_layout(showlegend=False)
        fig.update_layout( width=100, height=55, plot_bgcolor = "#fff")
        fig.update_layout( margin=dict(l=0, r=0, t=0, b=0))

        plot_div = plot(fig, output_type='div', include_plotlyjs=False, config =  {'displayModeBar': False} )
        
        if not os.path.exists("mydj1/static/img"):
            os.mkdir("mydj1/static/img")
        fig.write_image("""mydj1/static/img/fig_sum_international.png""")

        #save to csv บันทึก CSV ของกราฟ 
        if not os.path.exists("mydj1/static/csv"):
                os.mkdir("mydj1/static/csv")       
        result_sum.to_csv ("""mydj1/static/csv/table_sum_inter&national.csv""", index = True, header=True)
        
        print ("All Data and images are saved")
        print("Ending Query#3 ...")

        return checkpoint
        
    except Exception as e :
        checkpoint = False
        print('At Query#3: Something went wrong :', e) 
        return checkpoint

def query4(): # ตารางแหล่งทุนภายนอก exFund.html
    print("-"*20)
    print("Starting Query#4 ...")
    checkpoint = True
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้
    try:
        sql_cmd =  """with temp1 as (select A.fund_type_id
                                ,A.fund_type_th
                                ,A.FUND_TYPE_GROUP
                                ,B.fund_type_group_th
                                ,A.fund_source_id
                    from importdb_prpm_r_fund_type as A
                    left join fund_type_group as B on A.FUND_TYPE_GROUP = B.FUND_TYPE_GROUP_ID
                    where flag_used = 1 and (fund_source_id = 05 or fund_source_id = 06 )
                    order by 1 )

                    select A.fund_type_id,A.fund_type_th,A.fund_source_id,A.FUND_TYPE_GROUP, A.FUND_TYPE_GROUP_TH, B.marker
                    from temp1 as A
                    left join q_marker_ex_fund as B on A.fund_type_id = B.fund_type_id
                    order by 4 desc
                                """
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)
        df = df.fillna("")
        ###################################################
        # save to bd: q_ex_fund
        pm.save_to_db('q_ex_fund', con_string, df)   
        print ("Data is saved")
        print("Ending Query#4 ...")
        return checkpoint

    except Exception as e :
        checkpoint = False
        print('At Query#4: Something went wrong :', e)
        return checkpoint

def query5(): # ตาราง marker * และ ** ของแหล่งทุน
    print("-"*20)
    print("Starting Query#5 ...")
    checkpoint = True
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้
    
    try:
        ################### แหล่งทุนใหม่ #######################
        sql_cmd =  """with temp as  (SELECT A.FUND_TYPE_ID, A.FUND_TYPE_TH,A.FUND_SOURCE_TH, C.Fund_type_group, count(A.fund_type_id) as count, A.fund_budget_year
                                    from importdb_prpm_v_grt_project_eis as A 
                                    join importdb_prpm_r_fund_type as C on A.FUND_TYPE_ID = C.FUND_TYPE_ID
                                    where  (A.FUND_SOURCE_ID = 05 or A.FUND_SOURCE_ID = 06 )
                                    group by 1, 2 ,3 ,4 
                                    ORDER BY 5 desc)
                                                            
                    select FUND_TYPE_ID from temp where count = 1 and (fund_budget_year >= YEAR(date_add(NOW(), INTERVAL 543 YEAR))-1)
                    order by 1"""

        con_string = getConstring('sql')
        df1 = pm.execute_query(sql_cmd, con_string)
        df1['marker'] = '*'
        
        ################## แหล่งทุน ให้ทุนซ้ำ>=3ครั้ง  #####################
        sql_cmd2 =  """with temp as  (SELECT A.FUND_TYPE_ID, 
                                            A.FUND_TYPE_TH,
                                            A.FUND_SOURCE_TH, 
                                            C.Fund_type_group, 
                                            A.fund_budget_year
                                        from importdb_prpm_v_grt_project_eis as A 
                                        join importdb_prpm_r_fund_type as C on A.FUND_TYPE_ID = C.FUND_TYPE_ID
                                        where  (A.FUND_SOURCE_ID = 05 or A.FUND_SOURCE_ID = 06 )
                                        ORDER BY 1 desc
                                        ),
                                                                        
                            temp2 as (select * 
                                        from temp 
                                        where  (fund_budget_year  BETWEEN YEAR(date_add(NOW(), INTERVAL 543 YEAR))-5 AND YEAR(date_add(NOW(), INTERVAL 543 YEAR))-1)
                                    ),
        
                            temp3 as( select FUND_TYPE_ID, FUND_TYPE_TH,FUND_SOURCE_TH, fund_budget_year ,count(fund_type_id) as count
                                        from temp2
                                        group by 1
                                    )
                        
                            select FUND_TYPE_ID from temp3 where count >= 3"""

        con_string2 = getConstring('sql')
        df2 = pm.execute_query(sql_cmd2, con_string2)
        df2['marker'] = '**'
        
        ################## รวม df1 และ df2 ########################
        df = pd.concat([df1,df2],ignore_index = True)
        ###################################################
        # save path
        pm.save_to_db('q_marker_ex_fund', con_string, df)   

        print ("Data is saved")
        print("Ending Query#5 ...")
        return checkpoint

    except Exception as e :
        checkpoint = False
        print('At Query#5: Something went wrong :', e)
        return checkpoint

def query6(): # ISI SCOPUS TCI
    print("-"*20)
    print("Starting Query#6 ...")
    checkpoint = True
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้

    dt = datetime.now()
    now_year = dt.year+543
    ranking = ""

    try: 
        ########################
        #### สร้าง df เพื่อ บันทึก ISI #########
        ########################
        print("start ISI update")
        isi_df = isi()  # get ISI dataframe จาก web Scraping

        if(isi_df is None): 
            print("ISI'web scraping ERROR 1 time, call isi() again....")
            isi_df = isi()
            if(isi_df is None): 
                print("ISI'web scraping ERROR 2 times, break....")
        else:
            print("finished_web_scraping_ISI")

        isi_df.set_index('year', inplace=True)
        df = pd.read_csv("""mydj1/static/csv/ranking_isi.csv""", index_col=0)
        
        if df[-1:].index.values != now_year: # เช่น ถ้า เป็นปีใหม่ (ไม่อยู่ใน df มาก่อน) จะต้องใส่ index ปีใหม่ โดยการ append
            df.loc[now_year-1:now_year-1].update(isi_df.loc[now_year-1:now_year-1])  #ปีใหม่ - 1
            df =  df.append(isi_df.loc[now_year:now_year])  # ปีใหม่ 
        else :  
            df.loc[now_year:now_year].update(isi_df.loc[now_year:now_year])  # ปีปัจจุบัน 
            df.loc[now_year-1:now_year-1].update(isi_df.loc[ now_year-1:now_year-1]) # ปีปัจจุบัน - 1
        
        ########## save df ISI  to csv ##########      
        if not os.path.exists("mydj1/static/csv"):
                os.mkdir("mydj1/static/csv")
                
        df.to_csv ("""mydj1/static/csv/ranking_isi.csv""", index = True, header=True)
        print("ISI saved")
        ranking = ranking + "ISI Ok!, "

    except Exception as e:
        print("ISI_Error: "+str(e))
        ranking = ranking + "ISI Error, "

    try:
        ########################
        #### สร้าง df เพื่อ บันทึก scopus #########
        ########################
        print("start SCOPUS update")
        sco_df = sco(now_year-543)  # get scopus dataframe จาก API scopus_search
        
        if(sco_df is None): 
            print("Scopus can't scrap")
        else:
            print("finished_web_scraping_Scopus")

        sco_df.set_index('year', inplace=True)
        df = pd.read_csv("""mydj1/static/csv/ranking_scopus.csv""", index_col=0)
        
        if df[-1:].index.values != now_year: # เช่น ถ้า เป็นปีใหม่ (ไม่อยู่ใน df มาก่อน) จะต้องใส่ index ปีใหม่ โดยการ append
            df.loc[now_year-1:now_year-1].update(sco_df.loc[now_year-1:now_year-1])  #ปีใหม่ - 1
            df =  df.append(sco_df.loc[now_year:now_year])  # ปีใหม่
            
        else :  
            df.loc[now_year:now_year].update(sco_df.loc[now_year:now_year])  # ปีปัจจุบัน 
            df.loc[now_year-1:now_year-1].update(sco_df.loc[ now_year-1:now_year-1]) # ปีปัจจุบัน - 1
            
        ########## save df scopus to csv ##########      
        if not os.path.exists("mydj1/static/csv"):
                os.mkdir("mydj1/static/csv")
                
        df.to_csv ("""mydj1/static/csv/ranking_scopus.csv""", index = True, header=True)
        print("Scopus saved")
        ranking = ranking + "SCO Ok!, "

    except Exception as e:
        print("SCO Error: "+str(e))
        ranking = ranking + "SCO Error, "
    
    try:
        ########################
        #### สร้าง df เพื่อ บันทึก TCI #########
        ########################
        print("start TCI update")
        tci_df = tci()  # get TCI dataframe จาก web Scraping
        if(tci_df is None): 
            print("TCI'web scraping ERROR 1 time, call TCI() again....")
            tci_df = tci()
            if(tci_df is None): 
                print("TCI'web scraping ERROR 2 times, break....")
        else:
            print("finished_web scraping_TCI")

        tci_df.set_index('year', inplace=True)

        df = pd.read_csv("""mydj1/static/csv/ranking_tci.csv""", index_col=0)
    
        if df[-1:].index.values != now_year: # เช่น ถ้า เป็นปีใหม่ (ไม่อยู่ใน df มาก่อน) จะต้องใส่ index ปีใหม่ โดยการ append
            df.loc[now_year-1:now_year-1].update(tci_df.loc[now_year-1:now_year-1])  #ปีใหม่ - 1
            df =  df.append(tci_df.loc[now_year:now_year])  # ปีใหม่
        else :  
            df.loc[now_year:now_year].update(tci_df.loc[now_year:now_year])  # ปีปัจจุบัน 
            df.loc[now_year-1:now_year-1].update(tci_df.loc[ now_year-1:now_year-1]) # ปีปัจจุบัน - 1
        
        ########## save df TCI  to csv ##########      
        if not os.path.exists("mydj1/static/csv"):
                os.mkdir("mydj1/static/csv")
                
        df.to_csv ("""mydj1/static/csv/ranking_tci.csv""", index = True, header=True)
        print("TCI saved")
        ranking = ranking + "TCI Ok!, "

    except Exception as e:
        print("TCI Error: "+str(e))
        ranking = ranking + "TCI Error, "

    ##############  end #####################
    checkpoint = "chk_ranking"
    print("Results: ",ranking)
    return ranking,checkpoint

def query7(): # Head Page
    print("-"*20)
    print("Starting Query#7 ...")
    checkpoint = True
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้
    try:
        con_string = getConstring('sql')
        
        ### จำนวนของนักวิจัย จะไม่รวม ผู้ช่วยวิจัย
        df = pd.read_csv("""mydj1/static/csv/main_research.csv""", index_col=0)
        df = df.loc[(df.index == int(datetime.now().year+543))]
        
        print(df[['teacher','research_staff','post_doc']].sum(axis=1)[int(datetime.now().year+543)])
        final_df=pd.DataFrame({'total_of_guys':df[['teacher','research_staff','post_doc']].sum(axis=1)[int(datetime.now().year+543)] }, index=[0])
        
        ### รายได้งานวิจัย 
        df = pd.read_csv("""mydj1/static/csv/12types_of_budget.csv""", index_col=0)
        # df = df.rename(columns={"Unnamed: 0" : "budget_year"}, errors="raise")
        
        df = df.loc[(df.index == int(datetime.now().year+543))]
                
        final_df["total_of_budget"] = df.sum(axis=1)[int(datetime.now().year+543)]
        
        ### จำนวนงานวิจัย 
        df_isi = pd.read_csv("""mydj1/static/csv/ranking_isi.csv""", index_col=0)
        df_sco = pd.read_csv("""mydj1/static/csv/ranking_scopus.csv""", index_col=0)
        df_tci = pd.read_csv("""mydj1/static/csv/ranking_tci.csv""", index_col=0)
        
        final_df["num_of_pub_sco"] = df_sco.iloc[-1][0]
        final_df["num_of_pub_isi"] = df_isi.iloc[-1][0]
        final_df["num_of_pub_tci"] = df_tci.iloc[-1][0]
        

        ### หน่วยงานภายนอกที่เข้าร่วม 
        sql_cmd =  """SELECT count(*) as count 
                        from importdb_prpm_r_fund_type 
                        where flag_used = "1" and (fund_source_id = 05 or fund_source_id = 06) """

        df = pm.execute_query(sql_cmd, con_string)
        final_df["num_of_networks"] = df["count"].astype(int)
        print(final_df)
        ########## save to csv ##########      
        if not os.path.exists("mydj1/static/csv"):
                os.mkdir("mydj1/static/csv")
                
        final_df.to_csv ("""mydj1/static/csv/head_page.csv""", index = False, header=True)

        print ("Data is saved")
        print("Ending Query#7 ...")
        
        return checkpoint

    except Exception as e :
        checkpoint = False
        print('At Query#7: Something went wrong :', e)
        return checkpoint

def query8(): # web of science Research Areas
    print("-"*20)
    print("Starting Query#8 ...")
    checkpoint = True
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้
    path = """importDB"""

    try:
        driver = webdriver.Chrome(path+'/chromedriver.exe')  # เปิด chromedriver
    except Exception as e:
        print(e,"โปรดทำการ update เวอร์ชั่นใหม่ของ File chromedriver.exe")
        print("https://chromedriver.chromium.org/downloads")
        return None

    WebDriverWait(driver, 10)
    try:
        df = chrome_driver_get_research_areas_ISI(driver)
        if df is None:
            print("fail to get df, call again...")
            df = chrome_driver_get_research_areas_ISI(driver)
    
        driver.quit()
        ######### Save to DB
        con_string = getConstring('sql')
        pm.save_to_db('research_areas_isi', con_string, df) 

        if not os.path.exists("mydj1/static/csv"):
                os.mkdir("mydj1/static/csv")
        # save to csv        
        df[:20].to_csv ("""mydj1/static/csv/research_areas_20_isi.csv""", index = False, header=True)
                    
        print ("Data is saved")
        print("Ending Query#8 ...")

        return checkpoint

    except Exception as e :
        checkpoint = False
        print('At Query#8: Something went wrong :', e)
        return checkpoint
 
def query9(): # web of science catagories
    print("-"*20)
    print("Starting Query#9 ...")
    checkpoint = True
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้
    path = """importDB"""

    try:
        driver = webdriver.Chrome(path+'/chromedriver.exe')  # เปิด chromedriver
    except Exception as e:
        print(e,"โปรดทำการ update เวอร์ชั่นใหม่ของ File chromedriver.exe")
        print("https://chromedriver.chromium.org/downloads")
        return None

    WebDriverWait(driver, 10)
    
    try: 
        df = chrome_driver_get_catagories_ISI(driver)
        if df is None:
            print("fail to get df, call again...")
            df = chrome_driver_get_catagories_ISI(driver)    

        driver.quit()
        ######### Save to DB
        con_string = getConstring('sql')
        pm.save_to_db('categories_isi', con_string, df) 


        if not os.path.exists("mydj1/static/csv"):
                os.mkdir("mydj1/static/csv")
        # save to csv        
        df[:20].to_csv ("""mydj1/static/csv/categories_20_isi.csv""", index = False, header=True)
        
        print ("Data is saved")
        print("Ending Query#9 ...")

        return checkpoint

    except Exception as e :
        checkpoint = False
        print('At Query#9: Something went wrong :', e)
        return checkpoint

def query10(): # Citation ISI and H-index and avg_per_item
    print("-"*20)
    print("Starting Query#10 ...")
    checkpoint = True
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้
    dt = datetime.now()
    now_year = dt.year+543
        
    cited, h_index, avg = cited_isi()
    
    if(cited is None): 
            print("Get Citation ERROR 1 time, call cited_isi() again....")
            cited, h_index, avg = cited_isi()
            if(cited is None): 
                print("Get Citation ERROR 2 times, break....")
            else:
                print("finished Get Citation")
    else:
        print("finished Get Citation")

    try:   
        cited.set_index('year', inplace=True)
        
        df = pd.read_csv("""mydj1/static/csv/ranking_cited_score.csv""", index_col=0)

        if df[-1:].index.values != cited[0:1].index.values : # เช่น ถ้า เป็นปีใหม่ (ไม่อยู่ใน df มาก่อน) จะต้องใส่ index ปีใหม่ โดยการ append
            df.iloc[-1].update(cited.iloc[1])
            df = df.append(cited.iloc[0])
            
        else :  
            df.iloc[-1].update(cited.iloc[0])  # ปีปัจจุบัน 
            df.iloc[-2].update(cited.iloc[1]) # ปีปัจจุบัน - 1
            
        ########## save df scopus to csv ##########      
        if not os.path.exists("mydj1/static/csv"):
                os.mkdir("mydj1/static/csv")
                
        df.to_csv ("""mydj1/static/csv/ranking_cited_score.csv""", index = True, header=True)
        print("Cited Score is Saved")


        ###### save h-index to csv ######
        df=pd.DataFrame({'h_index':h_index }, index=[0])
        if not os.path.exists("mydj1/static/csv"):
                os.mkdir("mydj1/static/csv")
                
        df.to_csv ("""mydj1/static/csv/ranking_h_index.csv""", index = False, header=True)

        ###### save avg_cite_per_item to csv ######
        df=pd.DataFrame({'avg':avg }, index=[0])
        if not os.path.exists("mydj1/static/csv"):
                os.mkdir("mydj1/static/csv")
                
        df.to_csv ("""mydj1/static/csv/ranking_avg_cite_per_item.csv""", index = False, header=True)

        print ("Data is saved")
        print("Ending Query#10 ...")

        return checkpoint

    except Exception as e :
        checkpoint = False
        print('At Query#10: Something went wrong :', e)
        return checkpoint

def query11(): # จำนวนผู้วิจัยที่ได้รับทุน
    print("-"*20)
    print("Starting Query#11 ...")
    checkpoint = True
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้
    try:    
        now_year = (datetime.now().year)+543
        sql_cmd = """WITH temp1 AS ( SELECT psu_project_id, staff_id, research_position_id
                                FROM importdb_prpm_v_grt_pj_team_eis 
                                where research_position_id = 5),
                                
                    temp2 AS( SELECT distinct(psu_project_id), budget_group,budget_year
                                FROM importdb_prpm_v_grt_pj_budget_eis
                                where budget_group = 4
                                and (budget_source_group_id = 0 
                                    OR budget_source_group_id = 1 
                                    OR budget_source_group_id = 3
                                    OR budget_source_group_id = 4
                                    OR budget_source_group_id = 10)
                                )

                    select B.budget_year as year ,count(A.psu_project_id) as count
                    from temp2 as B
                    join temp1 as A on B.psu_project_id = A.psu_project_id
                    group by 1
                    having B.budget_year = """+str(now_year)+""" or B.budget_year = """+str(now_year-1)+"""
                    order by 1"""
    

        con_string = getConstring('sql')
        re_df = pm.execute_query(sql_cmd, con_string)
        re_df['year'] = re_df['year'].astype('int') 
        re_df.set_index('year', inplace=True)
        
        df = pd.read_csv("""mydj1/static/csv/main_research_revenue.csv""", index_col=0)
        
        if df[-1:].index.values != now_year: # เช่น ถ้า เริ่มปีใหม่ (ไม่อยู่ใน df มาก่อน) จะต้องใส่ index ปีใหม่ โดยการ append
            df.loc[now_year-1:now_year-1].update(re_df.loc[now_year-1:now_year-1])  #ปีใหม่ - 1
            df =  df.append(re_df.loc[now_year:now_year])  # ปีใหม่ 
        else :  
            df.loc[now_year:now_year].update(re_df.loc[now_year:now_year])  # ปีปัจจุบัน 
            df.loc[now_year-1:now_year-1].update(re_df.loc[ now_year-1:now_year-1]) # ปีปัจจุบัน - 1
        
            ########## save df  to csv ##########      
        if not os.path.exists("mydj1/static/csv"):
                os.mkdir("mydj1/static/csv")
                
        df.to_csv ("""mydj1/static/csv/main_research_revenue.csv""", index = True, header=True)

        print ("Data is saved")
        print("Ending Query#11 ...")

        return checkpoint

    except Exception as e :
        checkpoint = False
        print('At Query#11: Something went wrong :', e)
        return checkpoint

def query12(): # จำนวนผู้วิจัยหลัก

    print("-"*20)
    print("Starting Query#12 ...")
    checkpoint = True
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้
    try:
        re_df = pd.DataFrame(columns=['year','teacher','research_staff','post_doc','asst_staff'])
        # print(re_df)
        now_year = (datetime.now().year)+543
        sql_cmd_1_1 = """
                    SELECT count(DISTINCT( staff_id )) as count
                    FROM
                        importdb_hrmis_v_aw_for_ranking 
                    WHERE
                        end_year = """+str(now_year)+"""
                        AND (
                                corresponding = 1 OR corresponding = 2 OR corresponding = 3 OR 
                                (corresponding is Null and type_id=1)
                            ) 
                        AND ( pos_name_thai = 'อาจารย์' OR pos_name_thai = 'รองศาสตราจารย์' OR pos_name_thai = 'ผู้ช่วยศาสตราจารย์' OR pos_name_thai = 'ศาสตราจารย์' ) 
                        AND ( JDB_ID = 1 OR JDB_ID = 4 )"""
        
        sql_cmd_1_2 = """
                    SELECT count(DISTINCT( staff_id )) as count
                    FROM
                        importdb_hrmis_v_aw_for_ranking 
                    WHERE
                        end_year = """+str(now_year-1)+"""
                        AND (
                                corresponding = 1 OR corresponding = 2 OR corresponding = 3 OR 
                                (corresponding is Null and type_id=1)
                            ) 
                        AND ( pos_name_thai = 'อาจารย์' OR pos_name_thai = 'รองศาสตราจารย์' OR pos_name_thai = 'ผู้ช่วยศาสตราจารย์' OR pos_name_thai = 'ศาสตราจารย์' ) 
                        AND ( JDB_ID = 1 OR JDB_ID = 4 )"""

        sql_cmd_2_1 = """
                    SELECT count(DISTINCT( staff_id )) as count
                    FROM
                        importdb_hrmis_v_aw_for_ranking 
                    WHERE
                        end_year = """+str(now_year)+"""
                        AND (
                                corresponding = 1 OR corresponding = 2 OR corresponding = 3 OR 
                                (corresponding is Null and type_id=1)
                            ) 
                        AND ( JDB_ID = 1 OR JDB_ID = 4 )
                        AND pos_name_thai = 'นักวิจัย' """

        sql_cmd_2_2 = """
                    SELECT count(DISTINCT( staff_id )) as count
                    FROM
                        importdb_hrmis_v_aw_for_ranking 
                    WHERE
                        end_year = """+str(now_year-1)+"""
                        AND (
                                corresponding = 1 OR corresponding = 2 OR corresponding = 3 OR 
                                (corresponding is Null and type_id=1)
                            )  
                        AND ( JDB_ID = 1 OR JDB_ID = 4 )
                        AND pos_name_thai = 'นักวิจัย' """          

        sql_cmd_3_1 = """
                        SELECT count(DISTINCT( staff_id )) as count
                    FROM
                        importdb_hrmis_v_aw_for_ranking 
                    WHERE
                        end_year = """+str(now_year)+"""
                        AND (
                                corresponding = 1 OR corresponding = 2 OR corresponding = 3 OR 
                                (corresponding is Null and type_id=1)
                            )  
                        AND ( JDB_ID = 1 OR JDB_ID = 4 )
                        AND pos_name_thai = 'นักวิจัยหลังปริญญาเอก' """

        sql_cmd_3_2 = """
                        SELECT count(DISTINCT( staff_id )) as count
                    FROM
                        importdb_hrmis_v_aw_for_ranking 
                    WHERE
                        end_year = """+str(now_year-1)+"""
                        AND (
                                corresponding = 1 OR corresponding = 2 OR corresponding = 3 OR 
                                (corresponding is Null and type_id=1)
                            ) 
                        AND ( JDB_ID = 1 OR JDB_ID = 4 )
                        AND pos_name_thai = 'นักวิจัยหลังปริญญาเอก' """

        sql_cmd_4_1 = """
                    SELECT count(DISTINCT( staff_id )) as count
                    FROM
                        importdb_hrmis_v_aw_for_ranking 
                    WHERE
                        end_year = """+str(now_year)+"""
                        AND (
                                corresponding = 1 OR corresponding = 2 OR corresponding = 3 OR 
                                (corresponding is Null and type_id=1)
                            ) 
                        AND ( JDB_ID = 1 OR JDB_ID = 4 )
                        AND pos_name_thai = 'ผู้ช่วยวิจัย' """

        sql_cmd_4_2 = """
                    SELECT count(DISTINCT( staff_id )) as count
                    FROM
                        importdb_hrmis_v_aw_for_ranking 
                    WHERE
                        end_year = """+str(now_year-1)+"""
                        AND (
                                corresponding = 1 OR corresponding = 2 OR corresponding = 3 OR 
                                (corresponding is Null and type_id=1)
                            ) 
                        AND ( JDB_ID = 1 OR JDB_ID = 4 )
                        AND pos_name_thai = 'ผู้ช่วยวิจัย' """

        con_string = getConstring('sql')
        re_df_1_1 = pm.execute_query(sql_cmd_1_1, con_string).iloc[0][0]
        re_df_1_2 = pm.execute_query(sql_cmd_1_2, con_string).iloc[0][0]
        re_df_2_1 = pm.execute_query(sql_cmd_2_1, con_string).iloc[0][0]
        re_df_2_2 = pm.execute_query(sql_cmd_2_2, con_string).iloc[0][0]
        re_df_3_1 = pm.execute_query(sql_cmd_3_1, con_string).iloc[0][0]
        re_df_3_2 = pm.execute_query(sql_cmd_3_2, con_string).iloc[0][0]
        re_df_4_1 = pm.execute_query(sql_cmd_4_1, con_string).iloc[0][0]
        re_df_4_2 = pm.execute_query(sql_cmd_4_2, con_string).iloc[0][0]

        # สร้าง dataframe เพื่อเก็บ ผลลัพธ์ จากการ query 
        re_df.loc[0] = [now_year-1, re_df_1_2,re_df_2_2, re_df_3_2, re_df_4_2]
        re_df.loc[1] = [now_year, re_df_1_1,re_df_2_1, re_df_3_1, re_df_4_1]
        
        re_df['year'] = re_df['year'].astype('int')
        re_df['teacher'] = re_df['teacher'].astype('int') 
        re_df['research_staff'] = re_df['research_staff'].astype('int') 
        re_df['post_doc'] = re_df['post_doc'].astype('int')
        re_df['asst_staff'] = re_df['asst_staff'].astype('int') 
        re_df.set_index('year', inplace=True)
        print(re_df)
        # ดึง df จาก csv
        df = pd.read_csv("""mydj1/static/csv/main_research.csv""", index_col=0)
        
        # ทำการ update ค่า ใน  df ที่ดึงมา ด้วย re_df ผลลัพธ์ ที่ได้จากการ query
        if df[-1:].index.values != now_year: # เช่น ถ้า เริ่มปีใหม่ (ไม่อยู่ใน df มาก่อน) จะต้องใส่ index ปีใหม่ โดยการ append
            df.loc[now_year-1:now_year-1].update(re_df.loc[now_year-1:now_year-1])  #ปีใหม่ - 1
            df =  df.append(re_df.loc[now_year:now_year])  # ปีใหม่ 
        else :  
            df.loc[now_year:now_year].update(re_df.loc[now_year:now_year])  # ปีปัจจุบัน 
            df.loc[now_year-1:now_year-1].update(re_df.loc[ now_year-1:now_year-1]) # ปีปัจจุบัน - 1

            ########## save df  to csv ##########      
        if not os.path.exists("mydj1/static/csv"):
                os.mkdir("mydj1/static/csv")        
        df.to_csv ("""mydj1/static/csv/main_research.csv""", index = True, header=True)

        print ("Data is saved")
        print("Ending Query#12 ...")

        return checkpoint

    except Exception as e :
        checkpoint = False
        print('At Query#12: Something went wrong :', e)
        return checkpoint

def query13(): # parameter ของ ARIMA Regression
    
    print("-"*20)
    print("Starting Query#13 ...")
    checkpoint = True
    os.environ["NLS_LANG"] = ".UTF8"  # ทำให้แสดงข้อความเป็น ภาษาไทยได้
    
    try:
        rankings = ["ranking_isi", "ranking_scopus", "ranking_tci"]
        parameters = pd.DataFrame(columns=rankings,index = [0])
        
        for ranking in rankings:
            
            now_year = (datetime.now().year)+543
            
            df = pd.read_csv("""mydj1/static/csv/"""+ranking+""".csv""")
            
            df = df[['year', 'PSU']]
            dataset = df[df['year'] != now_year]
            
            df_x = df["year"][:-1:].to_frame().rename(columns={'year': "x"})
            df_y = df["PSU"][:-1:].to_frame().rename(columns={'PSU': "y"})
    
            df_2 = df[['year','PSU']][:-1:]
            
            # log test : ทำการ take log ฐาน e ให้กับ ค่าจำนวนการตีพิมพ์ เพื่อ ให้เหมาะสมกับการทำ ARIMA_regression
            log = np.log(df_2["PSU"])
            df_log = pd.DataFrame({'year':df.year[:-1],'PSU': log})
            df_log = df_log.set_index('year')
            
            ### สร้าง pdq parameter เพื่อ วน test หา parameter ที่ดีที่สุด
            p=d=q = range(0,3)
            pdq = list(itertools.product(p,d,q))

            ###ทำการ วน test หา parameter ที่ดีที่สุด #####
            warnings.filterwarnings('ignore')
            aics = []
            combs = {}
            for param in pdq:
                try:
                    model = ARIMA(df_log, order=param)
                    model_fit = model.fit(disp=0)
                    combs.update({model_fit.aic : [param]})
                    aics.append(model_fit.aic)
                except:
                    continue

            ## เมื่อได้ parameter ที่ดีที่สุด ทำการ fit model
            print(ranking,": ",combs[min(aics)][0])
            parameters.loc[0][ranking] = combs[min(aics)][0]


        if not os.path.exists("mydj1/static/csv"):
            os.mkdir("mydj1/static/csv") 

        parameters.to_csv ("""mydj1/static/csv/params_arima.csv""", index = True, header=True)
        
        print ("Data is saved")
        print("Ending Query#13 ...")

        return checkpoint

    except Exception as e :
        checkpoint = False
        print('At Query#13: Something went wrong :', e)
        return checkpoint

def get_fiscal_year(): # return ปีงบประมาณ
    date = datetime.now()
    return ((date.year+1)+543) if (date.month >= 10) else ((date.year)+543)
    
    
##################################################################
##### " function หลัก " ในการ สร้าง page html และ อื่นๆ ##############
##################################################################
@login_required(login_url='login')
def pageRevenues(request): # page รายได้งานวิจัย

    selected_year = datetime.now().year+543 # กำหนดให้ ปี ใน dropdown เป็นปีปัจจุบัน
    def get_head_page(): # get 
        df = pd.read_csv("""mydj1/static/csv/head_page.csv""")
        return df.iloc[0].astype(int)

    if request.method == "POST":
        filter_year =  request.POST["year"]   #รับ ปี จาก dropdown 
        print("post = ",request.POST )
        selected_year = int(filter_year)      # ตัวแปร selected_year เพื่อ ให้ใน dropdown หน้าต่อไป แสดงในปีที่เลือกไว้ก่อนหน้า(จาก year)
    
    def graph1():  # แสดงกราฟโดนัด ของจำนวน เงินทั้ง 11 หัวข้อ
        df = pd.read_csv("""mydj1/static/csv/12types_of_budget.csv""")
        df.reset_index(level=0, inplace=False)
        df = df.rename(columns={"Unnamed: 0" : "budget_year"}, errors="raise")
        re_df =df[df["budget_year"]==int(selected_year)]
        newdf = pd.DataFrame({'BUDGET_TYPE' : ["สกอ-มหาวิทยาลัยวิจัยแห่งชาติ (NRU)"
                                       ,"เงินงบประมาณแผ่นดิน"
                                       ,"เงินกองทุนวิจัยมหาวิทยาลัย"
                                       ,"เงินจากแหล่งทุนภายนอก ในประเทศไทย"
                                       ,"เงินจากแหล่งทุนภายนอก ต่างประเทศ"
                                       ,"เงินรายได้มหาวิทยาลัย"
                                       ,"เงินรายได้คณะ (เงินรายได้)"
                                       ,"เงินรายได้คณะ (กองทุนวิจัย)"
                                       ,"เงินกองทุนวิจัยวิทยาเขต"
                                       ,"เงินรายได้วิทยาเขต"
                                       ,"เงินอุดหนุนโครงการการพัฒนาความปลอดภัยและความมั่นคง"
                                       ,"ไม่ระบุ"    
                            ]})
        
        newdf["budget"] = 0.0
        # for n in range(0,11):
        for n in range(0,12):   # สร้างใส่ค่าใน column ใหม่
            newdf.budget[n] = re_df[str(n)]

        fig = px.pie(newdf, values='budget', names='BUDGET_TYPE' 
                ,color_discrete_sequence=px.colors.sequential.haline
                , hole=0.5 ,
        )
            

        fig.update_traces(textposition='inside', textfont_size=14)
        # fig.update_traces(hoverinfo="label+percent+name",
        #           marker=dict(line=dict(color='#000000', width=2)))

        fig.update_layout(uniformtext_minsize=12 , uniformtext_mode='hide')  #  ถ้าเล็กกว่า 12 ให้ hide 
        # fig.update_layout(legend=dict(font=dict(size=16))) # font ของ คำอธิบายสีของกราฟ (legend) ด้านข้างซ้าย
        # fig.update_layout(showlegend=False)  # ไม่แสดง legend
        fig.update_layout(legend=dict(orientation="h"))  # แสดง legend ด้านล่างของกราฟ
        fig.update_layout( height=600)
        fig.update_layout( margin=dict(l=30, r=30, t=30, b=5))

        fig.update_layout( annotations=[dict(text="<b> &#3647; {:,.2f}</b>".format(newdf.budget.sum()), x=0.50, y=0.5,  font_color = "black", showarrow=False)]) ##font_size=20,
        # fig.update_traces(hovertemplate='%{name} <br> %{value}') 
         
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        
        return plot_div

    def get_budget_amount(): #แสดง จำนวนของเงิน 11 ประเภท ในตาราง
        
        df = pd.read_csv("""mydj1/static/csv/12types_of_budget.csv""")
        df.reset_index(level=0, inplace=False)
        df = df.rename(columns={"Unnamed: 0" : "budget_year","0": "col0", "1": "col1", "2": "col2",
                    "3": "col3", "4": "col4", "5": "col5",
                    "6": "col6", "7": "col7", "8": "col8",
                    "9": "col9", "10": "col10", "11": "col11"}
                    , errors="raise")
        
        re_df = df[df["budget_year"]==int(selected_year)]
        # print(re_df)
        return re_df

    def get_budget_gov(): # แสดงเงินภายในประเทศ รัฐ 

        df = pd.read_csv("""mydj1/static/csv/gover&comp.csv""")
        df['budget_year'] = df['budget_year'].astype('str')
        df = df.groupby(['fund_type_group','budget_year'])['final_budget'].sum()
        df = df.to_frame()
        
        try :
            temp_gov = """ fund_type_group == "1" and budget_year == '"""+str(selected_year)+"""'"""
            gov = df.query(temp_gov)['final_budget'][0]
        
        except Exception as e :
            gov = 0

        return gov

    def get_budget_comp(): # แสดงเงินภายในประเทศ เอกชน

        df = pd.read_csv("""mydj1/static/csv/gover&comp.csv""")
        df['budget_year'] = df['budget_year'].astype('str')
        df = df.groupby(['fund_type_group','budget_year'])['final_budget'].sum()
        df = df.to_frame()
        try:
            temp_comp = """ fund_type_group == "2" and budget_year == '"""+str(selected_year)+"""'"""
            comp = df.query(temp_comp)['final_budget'][0]

        except Exception as e :
            comp = 0
        
        return comp

    def get_budget_campas():  # แสดงเงินวิทยาเขต
        df = pd.read_csv("""mydj1/static/csv/budget_of_fac.csv""")
        # print(df)
        index_df = df["camp_name_thai"].unique()

        df = df[(df["budget_year"] == selected_year)]
        df = df[["camp_name_thai","fac_name_thai","sum_final_budget"]]
        df = df.groupby(["camp_name_thai"])['sum_final_budget'].sum()
        df = df.to_frame() 
        
        for i in index_df:
            try:
                print(df["sum_final_budget"][i])
            except Exception as e :
                df.loc[i] = [0]

        re_df = pd.DataFrame(
                            {'col0' : [df["sum_final_budget"]["วิทยาเขตหาดใหญ่"]], 
                            'col1' : [df["sum_final_budget"]["วิทยาเขตปัตตานี"]],
                            'col2' : [df["sum_final_budget"]["วิทยาเขตภูเก็ต"]],
                            'col3' : [df["sum_final_budget"]["วิทยาเขตสุราษฎร์ธานี"]],
                            'col4' : [df["sum_final_budget"]["วิทยาเขตตรัง"]],
                            })
        
        return re_df
    
    def get_sum_budget(): #แสดง จำนวนของเงินรวม ภายนอก ภายใน
        
        df = pd.read_csv("""mydj1/static/csv/12types_of_budget.csv""")
        df.reset_index(level=0, inplace=False)
        df = df.rename(columns={"Unnamed: 0" : "budget_year","0": "col0", "1": "col1", "2": "col2",
                    "3": "col3", "4": "col4", "5": "col5",
                    "6": "col6", "7": "col7", "8": "col8",
                    "9": "col9", "10": "col10", "11": "col11"}
                    , errors="raise")
        
        df = df[df["budget_year"]==int(selected_year)]
        
        list_in=['col0','col1','col3','col4','col10']
        list_out=['col2','col5','col6','col7','col8','col9']

        result_in = df[list_in].sum(axis=1)
        result_out = df[list_out].sum(axis=1)

        result_in = result_in.iloc[0]
        result_out = result_out.iloc[0]
        
        re_df = pd.DataFrame(
                            {'in' : result_in, 
                            'out' : result_out,  
                            }, index=[0])
        
        return re_df

    def get_date_file():
        file_path = """mydj1/static/csv/12types_of_budget.csv"""
        t = time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(file_path)))
        d = datetime.strptime(t,"%m/%d/%Y").date() 

        return str(d.day)+'/'+str(d.month)+'/'+str(d.year+543)

    def get_fiscal_year(): # return ปีงบประมาณ
        date = datetime.now()
        if date.month >= 10:  # ปีงบประมาณใหม่
            return (date.year)+543+1
        else:
            return (date.year)+543  #ปีงบประมาณเดิม

    context={
        ###### Head_page ########################    
        'head_page': get_head_page(),
        'now_year' : (datetime.now().year)+543,
        #########################################
        'budget' : get_budget_amount(),
        'sum' : get_sum_budget(),
        'gov': get_budget_gov(),
        'comp': get_budget_comp(),
        # 'year' :range((datetime.now().year+1)+533,(datetime.now().year+1)+543),
        'year' :range(get_fiscal_year()-9 ,get_fiscal_year()+1),
        'year_show_research_funds_button' :range(get_fiscal_year()-9 ,get_fiscal_year()),
        'filter_year': selected_year,
        'campus' : get_budget_campas(),
        'graph1' :graph1(),
        'date' : get_date_file(),
        'top_bar_title': "รายได้งานวิจัย"
    
    }
    
    return render(request, 'importDB/revenues.html', context)

@login_required(login_url='login')
def revenues_graph(request, value):  # รับค่า value มาจาก url

    def moneyformat(x):  # เอาไว้เปลี่ยน format เป็นรูปเงิน
        return "{:,.2f}".format(x)

    def get_fiscal_year(): # return ปีงบประมาณ
        date = datetime.now()
        return ((date.year+1)+543) if (date.month >= 10) else ((date.year)+543)

    def graph(source):
        
        if  int(source) < 14:
            df = pd.read_csv("""mydj1/static/csv/table_"""+source+""".csv""", index_col=0)
            
            dff2 = pd.read_csv("""mydj1/static/csv/12types_of_budget.csv""", index_col=0)
            now = datetime.now()
            now_year = get_fiscal_year()
            # now_year = 2565
            temp = 0 
            for i, index in enumerate(df.index):  # temp เพื่อเก็บ ว่า ปีปัจจุบัน อยุ่ใน row ที่เท่าไร
                if index == now_year:
                    temp = i+1

            df2 = df[:temp-1]   # กราฟเส้นทึบ
            df3 = df[temp-2:temp]  # กราฟเส้นประ
            df4 = dff2['11'].to_frame()
            
            # กำหนดค่าเริ่มต้น ว่าจะต้องมี กี่ row, col และมี กราฟ scatter + table 
            fig = make_subplots(rows=1, cols=2,
                                column_widths=[0.7, 0.3],
                                specs=[[{"type": "scatter"},{"type": "table"}]]
                                )
            
            ### สร้าง กราฟเส้นสีเทา ####    
            # fig.add_trace(go.Scatter(x=df4.index, y=df4['11']
            #                                 ,line=dict( width=2 ,color='#D5DBDB') )
            #     )

            ### สร้าง กราฟเส้นทึบ ####
            
            fig.add_trace(go.Scatter(x=df2.index, y=df2[source],line=dict( color='royalblue'),name='', ))
            
            ### สร้าง กราฟเส้นประ ####
            fig.add_trace(go.Scatter(x=df3.index, y=df3[source]
                    ,line=dict( width=2, dash='dot',color='royalblue'),
                    name='', )
                )
            
            labels = { "0":"สกอ-มหาวิทยาลัยวิจัยแห่งชาติ (NRU)"
                        ,"1":"เงินงบประมาณแผ่นดิน"
                        ,"2":"เงินกองทุนวิจัยมหาวิทยาลัย"
                        ,"3":"แหล่งทุนภายนอก ในประเทศไทย"
                        ,"4":"แหล่งทุนภายนอก ต่างประเทศ"
                        ,"5":"เงินรายได้มหาวิทยาลัย"
                        ,"6":"เงินรายได้คณะ (เงินรายได้)"
                        ,"7":"เงินรายได้คณะ (กองทุนวิจัย)"
                        ,"8":"เงินกองทุนวิจัยวิทยาเขต"
                        ,"9":"เงินรายได้วิทยาเขต"
                        ,"10":"เงินอุดหนุนโครงการการพัฒนาความปลอดภัยและความมั่นคง"
                        ,"11":"แหล่งทุนภาครัฐ"
                        ,"12":"แหล่งทุนภาคเอกชน"
                        ,"13":"-ไม่ระบุแหล่งงบประมาณ-"}
    
            fig.update_layout(showlegend=False)
            fig.update_layout(title_text=f"<b>รายได้งานวิจัยจาก {labels[source]} 10 ปี ย้อนหลัง </b>",
                            height=500,width=1000,
                            xaxis_title="ปี พ.ศ",
                            yaxis_title="จำนวนเงิน (บาท)",
                            font=dict(
                                size=14,
                            ))
            fig.update_layout(
                plot_bgcolor="#FFF",
                xaxis = dict(
                    tickmode = 'linear',
                    # tick0 = 2554,
                    dtick = 1,
                    showgrid=False,
                    linecolor="#BCCCDC",  # Sets color of X-axis line
                )
                ,
                yaxis = dict(
                    showgrid=False,
                    linecolor="#BCCCDC",  # Sets color of X-axis line
                ),
            )
            fig.update_xaxes(ticks="outside")
            fig.update_yaxes(ticks="outside")

            ### ตาราง ####
            df[source] = df[source].apply(moneyformat)
            
            fig.add_trace(
                go.Table(
                    columnwidth = [100,200],
                    header=dict(values=["<b>Year</b>","<b>Budget\n<b>"],
                                fill = dict(color='#C2D4FF'),
                                align = ['center'] * 5),
                    cells=dict(values=[df.index, df[source]],
                            fill = dict(color='#F5F8FF'),
                            align = ['center','right'] * 5))
                    , row=1, col=2)
                
            fig.update_layout(autosize=True)
            plot_div = plot(fig, output_type='div', include_plotlyjs=False,)

            return  plot_div

        else :
            source = 'sum_national' if  int(source) == 14 else 'sum_international'
            
            df = pd.read_csv("""mydj1/static/csv/table_sum_inter&national.csv""", index_col=0)
            

            df2 = df[:9]   # กราฟเส้นทึบ
            df3 = df[8:]  # กราฟเส้นประ
            
            # กำหนดค่าเริ่มต้น ว่าจะต้องมี กี่ row, col และมี กราฟ scatter + table 
            fig = make_subplots(rows=1, cols=2,
                                column_widths=[0.7, 0.3],
                                specs=[[{"type": "scatter"},{"type": "table"}]]
                                )
            
            ### สร้าง กราฟเส้นสีเทา ####    
            # fig.add_trace(go.Scatter(x=df4.index, y=df4['11']
            #                                 ,line=dict( width=2 ,color='#D5DBDB') )
            #     )

            ### สร้าง กราฟเส้นทึบ ####
            
            fig.add_trace(go.Scatter(x=df2['year'], y=df2[source],line=dict( color='royalblue'), name= ""))
            
            ### สร้าง กราฟเส้นประ ####
            fig.add_trace(go.Scatter(x=df3['year'], y=df3[source]
                    ,line=dict( width=2, dash='dot',color='royalblue'), name ="" )
                )
            
            labels = { "sum_national":"รวมเงินทุนภายนอกมหาวิทยาลัย"
                        ,"sum_international":"รวมเงินทุนภายในมหาวิทยาลัย"
                    }
    
            fig.update_layout(showlegend=False)
            fig.update_layout(title_text=f"<b>{labels[source]} 10 ปี ย้อนหลัง </b>",
                            height=500,width=1000,
                            xaxis_title="ปี พ.ศ",
                            yaxis_title="จำนวนเงิน (บาท)",
                            font=dict(
                                size=14,
                            ))
            fig.update_layout(
                plot_bgcolor="#FFF",
                xaxis = dict(
                    tickmode = 'linear',
                    # tick0 = 2554,
                    dtick = 1,
                    showgrid=False,
                    linecolor="#BCCCDC",  # Sets color of X-axis line
                ),
                yaxis = dict(
                    showgrid=False,
                    linecolor="#BCCCDC",  # Sets color of X-axis line
                )
            )

            ### ตาราง ####
            df[source] = df[source].apply(moneyformat)
            
            fig.add_trace(
                go.Table(
                    columnwidth = [100,200],
                    header=dict(values=["<b>Year</b>","<b>Budget\n<b>"],
                                fill = dict(color='#C2D4FF'),
                                align = ['center'] * 5),
                    cells=dict(values=[df['year'], df[source]],
                            fill = dict(color='#F5F8FF'),
                            align = ['center','right'] * 5))
                    , row=1, col=2)
                
            fig.update_layout(autosize=True)
            fig.update_xaxes(ticks="outside")
            fig.update_yaxes(ticks="outside")
            plot_div = plot(fig, output_type='div', include_plotlyjs=False,)

            return  plot_div   

    
    source = value

    context={
        'plot1' : graph(source)
        
    }
        
    return render(request,'importDB/revenues_graph.html', context)

@login_required(login_url='login')
def revenues_table(request):  # รับค่า value มาจาก url
    
    def moneyformat(x):  # เอาไว้เปลี่ยน format เป็นรูปเงิน
        return "{:,.2f}".format(x)

    def get_table(year,source):
        print('source = ',source)
        if(source < 11 or source == 13):  # เฉพาะ หน่วยงาน ทุกหน่วยงาน (รวมอื่นๆ) ยกเว้น รัฐ และ เอกชน
            s = source
            if s == 13: # ถ้า source = 13 ให้เปลี่ยนเป็น 11 เพราะ หน่วยงาน-->ไม่ระบุเเหล่งงบประมาณ จะอยู่ใน budget_source_group_id = 11
                source = 11 
            df = pd.read_csv("""mydj1/static/csv/budget_of_fac.csv""")
            df = df[(df["budget_year"]==year) & (df["budget_source_group_id"]==source)]
            df[["camp_name_thai","fac_name_thai","sum_final_budget"]]
            df['sum_final_budget'] = df['sum_final_budget'].apply(moneyformat)
            df.reset_index(level=0, inplace=True)
             
        elif(source == 11 or source == 12) :   # เฉพาะ หน่วยงาน รัฐ และ เอกชน
            source2 = 1 if source==11 else 2
            df = pd.read_csv("""mydj1/static/csv/gover&comp.csv""")
            df = df[(df["budget_year"]==year) & (df["fund_type_group"]==source2)]
            df= df[['camp_name_thai', 'fac_name_thai','final_budget' ]]

            df = df.groupby(['camp_name_thai','fac_name_thai'] )['final_budget'].sum()
            df = df.to_frame() 
            nonlocal check 
            check = False    # กำหนดให้เป็น True เพื่อที่จะรู้ว่า เป็น หน่วยงาน รัฐ และ เอกชน    

        elif(source == 14) : # เฉพาะ หน่วยงานภายนอกทั้งหมด
            
            df = pd.read_csv("""mydj1/static/csv/budget_of_fac.csv""")
            df = df[(df['budget_year']==year) & (df['type']=='ภายนอก')]
            df = df[["camp_name_thai","fac_name_thai","sum_final_budget"]]
            df = df.groupby(['camp_name_thai','fac_name_thai']).sum() 
            df['sum_final_budget'] = df['sum_final_budget'].apply(moneyformat)
            df.reset_index( inplace=True)
            
            
        elif(source == 15) : # เฉพาะ หน่วยงานภายในทั้งหมด
           
            df = pd.read_csv("""mydj1/static/csv/budget_of_fac.csv""")
            df = df[(df['budget_year']==year) & (df['type']=='ภายใน')]
      
            df = df[["camp_name_thai","fac_name_thai","sum_final_budget"]]
            df = df.groupby(['camp_name_thai','fac_name_thai']).sum()
            df['sum_final_budget'] = df['sum_final_budget'].apply(moneyformat)
            df.reset_index( inplace=True)
            
        return df
    
    labels = { "0":"สกอ-มหาวิทยาลัยวิจัยแห่งชาติ (NRU)","1":"เงินงบประมาณแผ่นดิน","2":"เงินกองทุนวิจัยมหาวิทยาลัย"
                    ,"3":"เงินจากแหล่งทุนภายนอก ในประเทศไทย","4":"เงินจากแหล่งทุนภายนอก ต่างประเทศ","5":"เงินรายได้มหาวิทยาลัย",
                    "6":"เงินรายได้คณะ (เงินรายได้)","7":"เงินรายได้คณะ (กองทุนวิจัย)","8":"เงินกองทุนวิจัยวิทยาเขต",
                    "9":"เงินรายได้วิทยาเขต","10":"เงินอุดหนุนโครงการการพัฒนาความปลอดภัยและความมั่นคง",
                    "11" : "เงินทุนภายนอกจากหน่วยงานภาครัฐ", "12" : "เงินทุนภายนอกจากหน่วยงานภาคเอกชน",
                    "13" : "อื่นๆ", "14" : "รวมเงินทุนภายนอก", "15" : "รวมเงินทุนภายใน"}

    temp=[]
    for k, v in enumerate(request.POST.keys()):  # รับ key ของตัวแปร dictionary จาก ปุ่ม view มาใส่ในตัวแปร source เช่น source = Goverment
        if(k==1):
            temp = v.split("/")
    year = temp[0] # เก็บค่า ปี
    source = temp[1]  # เก็บหน่วยงาน 

    check = True  # เอาไว้เช็คว่า True = รายได้ 1-10, 13-15  และ False = รายได้ 11-12 (รัฐ เอกชน) #เพราะ การสร้าง column ของตาราง ใน Tamplate ไม่เหมือนกันเลยต้องเเยก

    context={
        'a_table' : get_table(int(year),int(source)) ,    
        'year' : year,
        'source' : labels[source],
        'check': check
    }  
    return render(request,'importDB/revenues_table.html', context)

@login_required(login_url='login')
def revenues_more_info(request):  # แสดงข้อมูลเพิ่มเติม ของ ReachFund

    for k, v in enumerate(request.POST.keys()):  # รับ key ของตัวแปร dictionary จาก ปุ่ม view มาใส่ในตัวแปร source เช่น source = Goverment
        if(k==1):   
            temp = v
    year = temp # เก็บค่า ปี
    print("ปีงบประมาณ :",year)

    def query_data():
        try:
            sql_cmd =  """SELECT leader_name_surname_th, project_name_th,fund_type_id, fund_type_th, sum_budget_plan, project_start_date , RDO_PROJECT_ID
                            from importdb_prpm_v_grt_project_eis
                            where fund_budget_year = """+str(year)+""" and fund_type_id <> 1315 
                                        and leader_name_surname_th <> ""
                                        and PJ_STATUS_ID <> 12
                                        and PJ_STATUS_ID <> 0
                                        and sum_budget_plan is not null
                                        and sum_budget_plan <> 0 		
                            order by 1
                            """

            # print(sql_cmd)
            con_string = getConstring('sql')
            df = pm.execute_query(sql_cmd, con_string)
            
            df =df.fillna(0)
            df["sum_budget_plan"] = df["sum_budget_plan"].apply(moneyformat) 
            df["project_start_date"] = df["project_start_date"].dt.strftime("%d/%m/%y")
            
            return df

        except:
            return None

    context={
        # 'a_table' : get_table(int(year),int(source)) ,  
        'data' : query_data(),
        'year' : year 
        
    }  
    return render(request,'importDB/revenues_more_info.html', context)

@login_required(login_url='login')
def pageExFund(request): # page รายได้จากทุนภายนอกมหาวิทยาลัย

    def get_head_page(): # get จำนวนของนักวิจัย 
        df = pd.read_csv("""mydj1/static/csv/head_page.csv""")
        return df.iloc[0].astype(int)

    # globle var
    selected_i = ""
    queryByselected = ""
    choices = ["----ทั้งหมด----","หน่วยงานภาครัฐ","หน่วยงานภาคเอกชน"]

    # check ตัวเลื่อกจาก dropdown
    if request.method == "POST" and "selected" in request.POST:
        re =  request.POST["selected"]   #รับ ตัวเลือก จาก dropdown 
        # print("post = ",request.POST )
        selected_i = re    # ตัวแปร selected_i เพื่อ ให้ใน dropdown หน้าต่อไป แสดงในปีที่เลือกไว้ก่อนหน้า(จาก selected)   
    else:
        selected_i = "----ทั้งหมด----"
        
    ##########################################################
    ################ เปลี่ยน selected_i เพื่อ นำไปเป็นค่า 1 หรือ 2 ที่สามารถคิวรี่ได้
    if selected_i == "หน่วยงานภาครัฐ":
        queryByselected = "1"
    elif selected_i == "หน่วยงานภาคเอกชน": 
        queryByselected = "2"
    else:
        queryByselected = "3"
    ##########################################################

   
    def getNationalEXFUND():
        
        if queryByselected=="3":
            # ---ทั้งหมด--- ถูกเลือก
            sql_cmd =  """select * from q_ex_fund
                            where fund_source_id = 05
                            order by 6 desc """
        else:  
            # 1 และ 2 ถูกเลือก 
            sql_cmd =  """select * from q_ex_fund    
                            where fund_source_id = 05 and FUND_TYPE_GROUP ="""+ queryByselected +""" 
                            order by 6 desc """

        # print(sql_cmd)
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)
        # print(df)
        return df

    def getInterNationalEXFUND():
        
        sql_cmd =  """select * from q_ex_fund
                            where fund_source_id = 06
                            order by 6 desc """

        # print(sql_cmd)
        con_string = getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)
        return df

    def get_date_file():
        file_path = """mydj1/static/csv/ranking_isi.csv"""
        t = time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(file_path)))
        d = datetime.strptime(t,"%m/%d/%Y").date() 

        return str(d.day)+'/'+str(d.month)+'/'+str(d.year+543)

    context={
        ###### Head_page ########################    
        'head_page': get_head_page(),
        'now_year' : (datetime.now().year)+543,
        'date' : get_date_file(),
        #########################################
        #### tables1 
         'choices' : choices,
         'selected_i' : selected_i,
        'df_Na_Fx_fund' : getNationalEXFUND(),
        #### tables1 
        'df_Inter_Fx_fund':getInterNationalEXFUND(),
        'top_bar_title': "แหล่งทุนภายนอก"

    }

    # return render(request, 'importDB/exFund.html', context)
    return render(request, 'importDB/exFund.html', context)

@login_required(login_url='login')
def pageRanking(request): # page Ranking ISI/SCOPUS/TCI

    def get_head_page(): # 
        df = pd.read_csv("""mydj1/static/csv/head_page.csv""")
        return df.iloc[0].astype(int)

    def tree_map():

        df = pd.read_csv("""mydj1/static/csv/categories_20_isi.csv""")
        
        fig = px.treemap(df, path=['categories'], values='count',
                  color='count', 
                  hover_data=['categories'],
                  color_continuous_scale='Plasma',
                )     
        fig.data[0].textinfo = 'label+text+value'
        fig.update_traces(textfont_size=16)
        fig.data[0].hovertemplate = "<b>categories=%{customdata[0]}<br>count=%{value}<br></b>"
        fig.update_layout( hoverlabel = dict( bgcolor = 'white' ) )
            
        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)
        return  plot_div
    
    def bar_chart1(): #categories

        df = pd.read_csv("""mydj1/static/csv/categories_20_isi.csv""")
        
        fig = px.bar(df[:10].sort_values(by=['count'] ), y = 'categories', x = "count" , text = 'count', orientation='h')
        fig.update_traces(texttemplate = "%{text:,f}", textposition= 'inside' )
        fig.update_layout(uniformtext_minsize = 8, uniformtext_mode = 'hide')
        # fig.update_layout( xaxis_tickangle=-45)    
        fig.update_layout(
            xaxis_title="",
            yaxis_title="",
        )
        fig.update_layout(
            plot_bgcolor="#FFF",
            margin=dict(t=30),
            xaxis = dict(
                showgrid=False,
                linecolor="#BCCCDC", 
            ),
            yaxis = dict(
                showgrid=False,
                linecolor="#BCCCDC", 
            ),
        )
        fig.update_xaxes(ticks="outside")
        
        

        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)
        return  plot_div

    def bar_chart2(): #research_areas

        df = pd.read_csv("""mydj1/static/csv/research_areas_20_isi.csv""")
        
        fig = px.bar(df[:10].sort_values(by=['count']), y = 'categories', x = "count" , text = 'count', orientation='h')
        fig.update_traces(texttemplate = "%{text:,f}", textposition= 'inside' )
        fig.update_layout(uniformtext_minsize = 8, uniformtext_mode = 'hide')
        # fig.update_layout( xaxis_tickangle=-45)    
        fig.update_layout(
            xaxis_title="",
            yaxis_title="",
        )
        fig.update_layout(
            plot_bgcolor="#FFF",
            margin=dict(t=30),
            xaxis = dict(
                showgrid=False,
                linecolor="#BCCCDC", 
            ),
            yaxis = dict(
                showgrid=False,
                linecolor="#BCCCDC", 
            ),
        )
        fig.update_xaxes(ticks="outside")

        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)
        return  plot_div

    def line_chart_total_publications():

        df_isi = pd.read_csv("""mydj1/static/csv/ranking_isi.csv""", index_col=0)
        df_sco = pd.read_csv("""mydj1/static/csv/ranking_scopus.csv""", index_col=0)
        df_tci = pd.read_csv("""mydj1/static/csv/ranking_tci.csv""", index_col=0)

        ####  กราฟเส้นทึบ
        df_isi_line = df_isi[-20:-1]['PSU'].to_frame()
        df_sco_line = df_sco[-20:-1]['PSU'].to_frame()
        df_tci_line = df_tci[-20:-1]['PSU'].to_frame()


        ####  กราฟเส้นทึบ     
        fig = go.Figure(data = go.Scatter(x=df_sco_line.index, y=df_sco_line['PSU'],
                    mode='lines+markers',
                    name='Scopus' ,
                    line=dict( width=2,color='red'),
                    legendgroup = 'sco' ) )

        fig.add_trace(go.Scatter(x=df_isi_line.index, y=df_isi_line['PSU'],
                    mode='lines+markers',
                    name='ISI-WoS',
                    line=dict( width=2,color='royalblue'),
                    legendgroup = 'isi' ))

        fig.add_trace(go.Scatter(x=df_tci_line.index, y=df_tci_line['PSU'],
                    mode='lines+markers',
                    name='TCI',
                    line=dict( width=2,color='#F39C12'),
                    legendgroup = 'tci' ))
        
        # ####  กราฟเส้นประ
        df_isi_dot = df_isi[-2:]['PSU'].to_frame()
        df_sco_dot = df_sco[-2:]['PSU'].to_frame()
        df_tci_dot = df_tci[-2:]['PSU'].to_frame()
        
        # scopus dot line
        fig.add_trace(go.Scatter(x=df_sco_dot.index, y=df_sco_dot["PSU"],
                    mode='lines',
                    line=dict( width=2, dash='dot',color='red'),
                    showlegend=False,
                    hoverinfo='skip',
                    legendgroup = 'sco'))
        fig.add_trace(go.Scatter(x=df_sco_dot.index[-1::], y=df_sco_dot["PSU"][-1::],
                    mode='markers',
                    name='Scopus' ,
                    line=dict(color='red'),
                    showlegend=False,
                    legendgroup = 'sco'))

        # isi dot line
        fig.add_trace(go.Scatter(x=df_isi_dot.index, y=df_isi_dot["PSU"],
                    mode='lines',
                    line=dict( width=2, dash='dot',color='royalblue'),
                    showlegend=False,
                    hoverinfo='skip',
                    legendgroup = 'isi'))
        fig.add_trace(go.Scatter(x=df_isi_dot.index[-1::], y=df_isi_dot["PSU"][-1::],
                    mode='markers',
                    name='ISI-WoS' ,
                    line=dict(color='royalblue'),
                    showlegend=False,
                    legendgroup = 'isi'))

        # tci dot line
        fig.add_trace(go.Scatter(x=df_tci_dot.index, y=df_tci_dot["PSU"],
                    mode='lines',
                    line=dict( width=2, dash='dot',color='#F39C12'),
                    showlegend=False,
                    hoverinfo='skip',
                    legendgroup = 'tci'))
        fig.add_trace(go.Scatter(x=df_tci_dot.index[-1::], y=df_tci_dot["PSU"][-1::],
                    mode='markers',
                    name='TCI' ,
                    line=dict(color='#F39C12'),
                    showlegend=False,
                    legendgroup = 'tci'))
        
        # fig.update_traces(mode='lines+markers')
        fig.update_layout(
            xaxis_title="<b>Year</b>",
            yaxis_title="<b>Number of Publications</b>",
            hovermode="x",
            legend=dict(x=0, y=1.1),
        )
        

        fig.update_layout(
            plot_bgcolor="#FFF"
            ,xaxis = dict(
                tickmode = 'linear',
                # tick0 = 2554,
                dtick = 2,
                showgrid=False,
                linecolor="#BCCCDC",
                showspikes=True, # Show spike line for X-axis
                # Format spike
                spikethickness=2,
                spikedash="dot",
                spikecolor="#999999",
                spikemode="across",
            ),
            yaxis = dict(
                showgrid=False,
                linecolor="#BCCCDC", 
            ),
            hoverdistance=100, # Distance to show hover label of data point
            spikedistance=1000, # Distance to show spike
        )

        fig.update_xaxes(ticks="outside")
        fig.update_yaxes(ticks="outside")

        fig.update_layout(legend=dict(orientation="h"))
        fig.update_layout(
            margin=dict(t=55, ),
        )

        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)
        return  plot_div

    def line_chart_cited_per_year():

        score = pd.read_csv("""mydj1/static/csv/ranking_cited_score.csv""")
        score = score.set_index('year')
        
        score_line = score[-10:-1]['cited'].to_frame()
        
        fig = go.Figure(data = go.Scatter(x=score_line.index, y=score_line["cited"],
                    mode='lines+markers',
                    name='ISI-WoS' ,
                    line=dict( width=2,color='royalblue') ,
                    showlegend=False,
                    ) )

        score_dot = score[-2:]['cited'].to_frame()
        fig.add_trace(go.Scatter(x=score_dot.index, y=score_dot["cited"],
                    mode='markers',
                    name='ISI-WoS',
                    line=dict( width=2, dash='dot',color='royalblue'),
                    showlegend=False,
                    ))

        fig.update_traces(mode='lines+markers')
        fig.update_layout(
            # hovermode="x",
            xaxis = dict(
                tickmode = 'linear',
                dtick = 1,
                showgrid=False,
                linecolor="#BCCCDC",
                
            ),
            yaxis = dict(
                showgrid=False,
                linecolor="#BCCCDC", 
            ),
            margin=dict(t=50, b=10),
            plot_bgcolor="#FFF",
            xaxis_title="<b>Year</b>",
            yaxis_title="<b>Sum of Times Cited</b>",
        )

        fig.update_xaxes( 
                        ticks="outside",
                        showspikes=True,
                        spikethickness=2,
                        spikedash="dot",
                        spikecolor="#999999",)
        fig.update_yaxes(
                        ticks="outside",
                        showspikes=True,
                        spikethickness=2,
                        spikedash="dot",
                        spikecolor="#999999",)


        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)
        return  plot_div
    
    def sum_of_cited():

        score = pd.read_csv("""mydj1/static/csv/ranking_cited_score.csv""")
        score = score.set_index('year')
        
        return score[-1:-11:-1].sum()

    def avg_per_items():

        df = pd.read_csv("""mydj1/static/csv/ranking_avg_cite_per_item.csv""")
        
        return df["avg"]
    
    def avg_per_year():
        
        cited_score = pd.read_csv("""mydj1/static/csv/ranking_cited_score.csv""")
        cited_score = cited_score.set_index('year')
        mean = np.mean(cited_score[-1:-11:-1])[0]
        return mean
    
    def total_publications():
        df_isi = pd.read_csv("""mydj1/static/csv/ranking_isi.csv""", index_col=0)
        df_sco = pd.read_csv("""mydj1/static/csv/ranking_scopus.csv""", index_col=0)
        df_tci = pd.read_csv("""mydj1/static/csv/ranking_tci.csv""", index_col=0)

        isi_sum = np.sum(df_isi["PSU"])
        sco_sum = np.sum(df_sco["PSU"])
        tci_sum = np.sum(df_tci["PSU"])
        

        re_df = pd.DataFrame({'isi': [isi_sum], 'sco': [sco_sum], 'tci':[tci_sum]})
        
        return re_df.iloc[0]

        # return _sum
    
    def h_index():
        df = pd.read_csv("""mydj1/static/csv/ranking_h_index.csv""")
        
        return df["h_index"]

    def get_date_file():
        file_path = """mydj1/static/csv/ranking_isi.csv"""
        t = time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(file_path)))
        d = datetime.strptime(t,"%m/%d/%Y").date() 

        return str(d.day)+'/'+str(d.month)+'/'+str(d.year+543)

    context={
        ###### Head_page ########################    
        'head_page': get_head_page(),
        'now_year' : (datetime.now().year)+543,
        #########################################

        #### Graph
        # 'tree_map' : tree_map(),
        'bar_chart1' : bar_chart1(),
        'bar_chart2' : bar_chart2(),
        'line_chart_publication' :line_chart_total_publications(),
        'line_chart_cited' : line_chart_cited_per_year(),
        'sum_cited' :sum_of_cited(),
        'avg_per_items' :avg_per_items(),
        'avg_per_year' :avg_per_year(),
        'h_index' : h_index(),
        'total_publication' :total_publications(),
        'date' : get_date_file(),
        'top_bar_title': "จำนวนงานวิจัย"
    }

    return render(request,'importDB/ranking.html', context)   

@login_required(login_url='login')
def compare_ranking(request): #page เพื่อเปรียบเทียบ ranking ของ PSU CMU KKU MU
    
    def line_chart_isi():
        df_isi = pd.read_csv("""mydj1/static/csv/ranking_isi.csv""", index_col=0)
        
        columns = df_isi.columns.tolist()  # เก็บ ชื่อ columns (ชื่อย่อมหาลัย) ที่อยุ่ใน ranking_isi  
        # print(columns)

        data = master_ranking_university_name.objects.all() # ดึงรายละเอียดมหาลัยที่จะค้นหา จากฐานข้อมูล Master
        df_names = {}    # ตัวแปร สร้างไว้เก็บ ชื่อย่อ/ชื่อeng/สี ใน dict pattern {short_name : [name_eng, color]}
        df_line = pd.DataFrame()  # ตัวแปร line เก็บ ค่าคะเเนน isi ในแต่ละปี ของแต่ละมหาลัย เพื่อวาดกราฟเส้นทึบ
        df_dot = pd.DataFrame()  # ตัวแปร dot เก็บ ค่าคะเเนน isi ในแต่ละปี ของแต่ละมหาลัย เพื่อวาดกราฟเส้นประ
        for item in data.values('short_name','name_eng','flag_used','color'): # วน for เพื่อตรวจสอบ ว่า มี มหาวิทยาลัยใหม่ ถูกเพิ่ม/หรือ ไม่ได้ใช้ (flag_used = false )มาในฐานข้อมูลหรือไม่
            print(item['flag_used'],' and ',item['short_name'])
            if ((item['flag_used'] == True) | (item['flag_used'] == '1')) & (item['short_name'] in columns) :
                df_line[item['short_name']] = df_isi[-20:-1][item['short_name']]
                df_names[item['short_name']] = [item['name_eng'],item['color']]
                    
        ####  กราฟเส้นทึบ #########
        fig = go.Figure( )
        print(data)
        for item in columns:  # วนวาดกราฟเส้นทึบ ที่ไม่ใช้ PSU เพราะ อยากให้ PSU วาดกราฟอยุ่บนกราฟอื่นๆ ต้องว่างสุดท้าย
            if item != "PSU":
                visible = True if (item == 'CMU') | (item == 'KKU') else "legendonly"  # ทำให้ CMU และ KKU แสดงอยู่บนกราฟ ส่วน ม. อื่น ให้ legendonly ( legendonly หมายความว่า ต้องกด เเล้วจะเเสดงให้เห็นในกราฟ )
                fig.add_trace(go.Scatter(x=df_line.index, y=df_line[item],
                        mode='lines+markers', # กำหนดว่า เป็นเส้นและมีจุด
                        name=item+": "+df_names[item][0] , # กำหนด ชื่อเวลา hover เอา mouse ชี้บนเส้น
                        line=dict( width=2,color=df_names[item][1]), # กำหนดสี และความหนาของเส้น
                        legendgroup = item, # กำหนดกลุ่ม ของเส้น เพื่อ สามารถกด show หรือ ไม่ show กราฟได้
                        visible = visible, # กำหนดว่าให้ เส้นใดๆ แสดงตอนเริ่มกราฟ หรือไม่
                        # hoverinfo='skip',  # กำหนดว่า ไม่มีการแสดงอะไรเมื่อเอาเมาส์ ไปชี้ 
                        # showlegend=False, # กำหนดว่าจะ show legend หรือไม่
                        ))                      

        fig.add_trace(go.Scatter(x=df_line.index, y=df_line['PSU'],  # วาดกราฟ PSU
                        mode='lines+markers',
                        name="PSU: Prince of Songkla University" ,
                        line=dict( width=2,color='royalblue' ),
                        # marker={'size':10},
                        legendgroup = 'PSU'
                        ))
        
        
        
        ######  กราฟเส้นประ  #########
        for item in data.values('short_name','name_eng','flag_used','color'): # วน for เพื่อตรวจสอบ ว่า มี มหาวิทยาลัยใหม่ ถูกเพิ่ม/หรือ ไม่ได้ใช้ (flag_used = false )มาในฐานข้อมูลหรือไม่
            if ((item['flag_used'] == True) | (item['flag_used'] == '1')) & (item['short_name'] in columns) :
                df_dot[item['short_name']] = df_isi[-2:][item['short_name']]
                

        for item in columns:  # วนวาดกราฟเส้นประ ที่ไม่ใช้ PSU เพราะ อยากให้ PSU วาดกราฟอยุ่บนกราฟอื่นๆ ต้องว่างสุดท้าย
            if item != "PSU":
                visible = True if (item == 'CMU') | (item == 'KKU') else "legendonly"  # ทำให้ CMU และ KKU แสดงอยู่บนกราฟ ส่วน ม. อื่น ให้ legendonly ( legendonly หมายความว่า ต้องกด เเล้วจะเเสดงให้เห็นในกราฟ )
                
                fig.add_trace(go.Scatter(x=df_dot.index, y=df_dot[item],
                        mode='lines',
                        # name=item+": "+df_names[item][0] ,
                        line=dict( width=2, dash='dot',color=df_names[item][1]),
                        showlegend=False,
                        hoverinfo='skip', 
                        legendgroup = item,
                        visible = visible
                         ))

                fig.add_trace(go.Scatter(x=df_dot.index[-1::], y=df_dot[item][-1::],
                        mode='markers',
                        name=item+": "+df_names[item][0] ,
                        line=dict(color=df_names[item][1]),
                        showlegend=False,
                        visible = visible,
                        legendgroup = item))

        fig.add_trace(go.Scatter(x=df_dot.index, y=df_dot['PSU'],  # วาดกราฟ เส้นประ PSU
                        mode='lines',
                        name="PSU: Prince of Songkla University" ,
                        line=dict( width=2, dash='dot',color='royalblue'),
                        showlegend=False,
                        hoverinfo='skip',
                        # marker={'size':10},
                        legendgroup = 'PSU'
                        ))
        
        fig.add_trace(go.Scatter(x=df_dot.index[-1::], y=df_dot['PSU'][-1::],
                        mode='markers',
                        name='PSU'+": "+df_names['PSU'][0] ,
                        line=dict(color='royalblue'),
                        showlegend=False,
                        legendgroup = 'PSU'))
         
        fig.update_traces(hovertemplate=None,)
        fig.update_layout(hovermode="x")    
        fig.update_layout(
            xaxis_title="<b>Year</b>",
            yaxis_title="<b>Number of Publications</b>",
        )
        # fig.update_layout(legend=dict(x=0, y=1.1))

        fig.update_layout(
            xaxis = dict(
                tickmode = 'linear',
                # tick0 = 2554,
                dtick = 2,
                showgrid=False,
                linecolor="#BCCCDC",
                showspikes=True, # Show spike line for X-axis
                # Format spike
                spikethickness=2,
                spikedash="dot",
                spikecolor="#999999",
                spikemode="across",
            ),
            yaxis = dict(
              
                showgrid=False,
                linecolor="#BCCCDC",

            )
        )

        fig.update_xaxes(ticks="outside")
        fig.update_yaxes(ticks="outside")

        # fig.update_layout(legend=dict(orientation="h"))
        fig.update_layout(
            margin=dict(t=55),
            plot_bgcolor="#FFF",
        )

        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)
        return  plot_div
    
    def line_chart_sco():
        df_sco = pd.read_csv("""mydj1/static/csv/ranking_scopus.csv""", index_col=0)
        
        columns = df_sco.columns.tolist()  # เก็บ ชื่อ columns (ชื่อย่อมหาลัย) ที่อยุ่ใน ranking_scopus  
        # print(columns)

        data = master_ranking_university_name.objects.all() # ดึงรายละเอียดมหาลัยที่จะค้นหา จากฐานข้อมูล Master
        df_names = {}    # ตัวแปร สร้างไว้เก็บ ชื่อย่อ/ชื่อeng/สี ใน dict pattern {short_name : [name_eng, color]}
        df_line = pd.DataFrame()  # ตัวแปร line เก็บ ค่าคะเเนน scopus ในแต่ละปี ของแต่ละมหาลัย เพื่อวาดกราฟเส้นทึบ
        df_dot = pd.DataFrame()  # ตัวแปร dot เก็บ ค่าคะเเนน scopus ในแต่ละปี ของแต่ละมหาลัย เพื่อวาดกราฟเส้นประ
        for item in data.values('short_name','name_eng','flag_used','color'): # วน for เพื่อตรวจสอบ ว่า มี มหาวิทยาลัยใหม่ ถูกเพิ่ม/หรือ ไม่ได้ใช้ (flag_used = false )มาในฐานข้อมูลหรือไม่
            if ((item['flag_used'] == True) | (item['flag_used'] == '1')) & (item['short_name'] in columns) :
                df_line[item['short_name']] = df_sco[-20:-1][item['short_name']]
                df_names[item['short_name']] = [item['name_eng'],item['color']]
          
        fig = go.Figure( )

        ####  กราฟเส้นทึบ     
        for item in columns:  # วนวาดกราฟเส้นทึบ ที่ไม่ใช้ PSU เพราะ อยากให้ PSU วาดกราฟอยุ่บนกราฟอื่นๆ ต้องว่างสุดท้าย
            if item != "PSU":
                visible = True if (item == 'CMU') | (item == 'KKU') else "legendonly"  # ทำให้ CMU และ KKU แสดงอยู่บนกราฟ ส่วน ม. อื่น ให้ legendonly ( legendonly หมายความว่า ต้องกด เเล้วจะเเสดงให้เห็นในกราฟ )
                fig.add_trace(go.Scatter(x=df_line.index, y=df_line[item],
                        mode='lines+markers',
                        name=item+": "+df_names[item][0] ,
                        line=dict( width=2,color=df_names[item][1]),
                        legendgroup = item,
                        visible = visible,
                        ))

        fig.add_trace(go.Scatter(x=df_line.index, y=df_line['PSU'],  # วาดกราฟ PSU
                        mode='lines+markers',
                        name="PSU: Prince of Songkla University" ,
                        line=dict( width=2,color='royalblue' ),
                        # marker={'size':10},
                        legendgroup = 'PSU'
                        # visible = False
                        ))
        
        # # ####  กราฟเส้นประ
        for item in data.values('short_name','name_eng','flag_used','color'): # วน for เพื่อตรวจสอบ ว่า มี มหาวิทยาลัยใหม่ ถูกเพิ่ม/หรือ ไม่ได้ใช้ (flag_used = false )มาในฐานข้อมูลหรือไม่
            if ((item['flag_used'] == True) | (item['flag_used'] == '1')) & (item['short_name'] in columns) :
                df_dot[item['short_name']] = df_sco[-2:][item['short_name']]
                

        for item in columns:  # วนวาดกราฟเส้นประ ที่ไม่ใช้ PSU เพราะ อยากให้ PSU วาดกราฟอยุ่บนกราฟอื่นๆ ต้องว่างสุดท้าย
            if item != "PSU":
                visible = True if (item == 'CMU') | (item == 'KKU') else "legendonly"  # ทำให้ CMU และ KKU แสดงอยู่บนกราฟ ส่วน ม. อื่น ให้ legendonly ( legendonly หมายความว่า ต้องกด เเล้วจะเเสดงให้เห็นในกราฟ )
                fig.add_trace(go.Scatter(x=df_dot.index, y=df_dot[item],
                        mode='lines',
                        name=item+": "+df_names[item][0] ,
                        line=dict( width=2, dash='dot',color=df_names[item][1]),
                        showlegend=False,
                        hoverinfo='skip',
                        legendgroup = item,
                        visible = visible,
                         ))
                         
                fig.add_trace(go.Scatter(x=df_dot.index[-1::], y=df_dot[item][-1::],
                        mode='markers',
                        name=item+": "+df_names[item][0] ,
                        line=dict(color=df_names[item][1]),
                        showlegend=False,
                        visible = visible,
                        legendgroup = item))

        fig.add_trace(go.Scatter(x=df_dot.index, y=df_dot['PSU'],  # วาดกราฟ เส้นประ PSU
                        mode='lines',
                        name="PSU: Prince of Songkla University" ,
                        line=dict( width=2, dash='dot',color='royalblue'),
                        showlegend=False,
                        hoverinfo='skip',
                        # marker={'size':10},
                        legendgroup = 'PSU'
                        ))
        
        fig.add_trace(go.Scatter(x=df_dot.index[-1::], y=df_dot['PSU'][-1::],
                        mode='markers',
                        name='PSU'+": "+df_names['PSU'][0] ,
                        line=dict(color='royalblue'),
                        showlegend=False,
                        legendgroup = 'PSU'))
        
        fig.update_traces(hovertemplate=None)
        fig.update_layout(hovermode="x")    
        fig.update_layout(
            xaxis_title="<b>Year</b>",
            yaxis_title="<b>Number of Publications</b>",
        )
        # fig.update_layout(legend=dict(x=0, y=1.1))

        fig.update_layout(
            xaxis = dict(
                tickmode = 'linear',
                # tick0 = 2554,
                dtick = 2,
                showgrid=False,
                linecolor="#BCCCDC",
                showspikes=True, # Show spike line for X-axis
                # Format spike
                spikethickness=2,
                spikedash="dot",
                spikecolor="#999999",
                spikemode="across",
            ),
            yaxis = dict(
              
                showgrid=False,
                linecolor="#BCCCDC",

            ),
            plot_bgcolor="#FFF",
        )

        fig.update_xaxes(ticks="outside")
        fig.update_yaxes(ticks="outside")

        # fig.update_layout(legend=dict(orientation="h"))
        fig.update_layout(
            margin=dict(t=55),
        )

        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)
        return  plot_div
    
    def line_chart_tci():
        df_tci = pd.read_csv("""mydj1/static/csv/ranking_tci.csv""", index_col=0)
    
        columns = df_tci.columns.tolist()  # เก็บ ชื่อ columns (ชื่อย่อมหาลัย) ที่อยุ่ใน ranking_isi  
        # print(columns)

        data = master_ranking_university_name.objects.all() # ดึงรายละเอียดมหาลัยที่จะค้นหา จากฐานข้อมูล Master
        df_names = {}    # ตัวแปร สร้างไว้เก็บ ชื่อย่อ/ชื่อeng/สี ใน dict pattern {short_name : [name_eng, color]}
        df_line = pd.DataFrame()  # ตัวแปร line เก็บ ค่าคะเเนน tci ในแต่ละปี ของแต่ละมหาลัย เพื่อวาดกราฟเส้นทึบ
        df_dot = pd.DataFrame()  # ตัวแปร dot เก็บ ค่าคะเเนน tci ในแต่ละปี ของแต่ละมหาลัย เพื่อวาดกราฟเส้นประ
        for item in data.values('short_name','name_eng','flag_used','color'): # วน for เพื่อตรวจสอบ ว่า มี มหาวิทยาลัยใหม่ ถูกเพิ่ม/หรือ ไม่ได้ใช้ (flag_used = false )มาในฐานข้อมูลหรือไม่
            if ((item['flag_used'] == True) | (item['flag_used'] == '1')) & (item['short_name'] in columns) :
                df_line[item['short_name']] = df_tci[-20:-1][item['short_name']]
                df_names[item['short_name']] = [item['name_eng'],item['color']]
                        
        ####  กราฟเส้นทึบ #########
        fig = go.Figure( )

        for item in columns:  # วนวาดกราฟเส้นทึบ ที่ไม่ใช้ PSU เพราะ อยากให้ PSU วาดกราฟอยุ่บนกราฟอื่นๆ ต้องว่างสุดท้าย
            if item != "PSU":
                visible = True if (item == 'CMU') | (item == 'KKU') else "legendonly"  # ทำให้ CMU และ KKU แสดงอยู่บนกราฟ ส่วน ม. อื่น ให้ legendonly ( legendonly หมายความว่า ต้องกด เเล้วจะเเสดงให้เห็นในกราฟ )
                fig.add_trace(go.Scatter(x=df_line.index, y=df_line[item],
                        mode='lines+markers',
                        name=item+": "+df_names[item][0] ,
                        line=dict( width=2,color=df_names[item][1]),
                        legendgroup = item,
                        visible = visible,
                        ))

        fig.add_trace(go.Scatter(x=df_line.index, y=df_line['PSU'],  # วาดกราฟ PSU
                        mode='lines+markers',
                        name="PSU: Prince of Songkla University" ,
                        line=dict( width=2,color='royalblue' ),
                        # marker={'size':10},
                        legendgroup = 'PSU'
                        # visible = False
                        ))
        
        
        
        ######  กราฟเส้นประ  #########
        for item in data.values('short_name','name_eng','flag_used','color'): # วน for เพื่อตรวจสอบ ว่า มี มหาวิทยาลัยใหม่ ถูกเพิ่ม/หรือ ไม่ได้ใช้ (flag_used = false )มาในฐานข้อมูลหรือไม่
            if ((item['flag_used'] == True) | (item['flag_used'] == '1')) & (item['short_name'] in columns) :
                df_dot[item['short_name']] = df_tci[-2:][item['short_name']]
                

        for item in columns:  # วนวาดกราฟเส้นประ ที่ไม่ใช้ PSU เพราะ อยากให้ PSU วาดกราฟอยุ่บนกราฟอื่นๆ ต้องว่างสุดท้าย
            if item != "PSU":
                visible = True if (item == 'CMU') | (item == 'KKU') else "legendonly"  # ทำให้ CMU และ KKU แสดงอยู่บนกราฟ ส่วน ม. อื่น ให้ legendonly ( legendonly หมายความว่า ต้องกด เเล้วจะเเสดงให้เห็นในกราฟ )
                fig.add_trace(go.Scatter(x=df_dot.index, y=df_dot[item],
                        mode='lines',
                        name=item+": "+df_names[item][0] ,
                        line=dict( width=2, dash='dot',color=df_names[item][1]),
                        hoverinfo='skip',
                        showlegend=False,
                        legendgroup = item,
                        visible = visible,
                         ))
                         
                fig.add_trace(go.Scatter(x=df_dot.index[-1::], y=df_dot[item][-1::],
                        mode='markers',
                        name=item+": "+df_names[item][0] ,
                        line=dict(color=df_names[item][1]),
                        showlegend=False,
                        visible = visible,
                        legendgroup = item))

        fig.add_trace(go.Scatter(x=df_dot.index, y=df_dot['PSU'],  # วาดกราฟ เส้นประ PSU
                        mode='lines',
                        name="PSU: Prince of Songkla University" ,
                        line=dict( width=2, dash='dot',color='royalblue'),
                        showlegend=False,
                        hoverinfo='skip',
                        # marker={'size':10},
                        legendgroup = 'PSU'
                        ))
        
        fig.add_trace(go.Scatter(x=df_dot.index[-1::], y=df_dot['PSU'][-1::],
                        mode='markers',
                        name='PSU'+": "+df_names['PSU'][0] ,
                        line=dict(color='royalblue'),
                        showlegend=False,
                        legendgroup = 'PSU'))
         
        fig.update_traces(hovertemplate=None)
        fig.update_layout(hovermode="x")    
        fig.update_layout(
            xaxis_title="<b>Year</b>",
            yaxis_title="<b>Number of Publications</b>",
        )
        # fig.update_layout(legend=dict(x=0, y=1.1))

        fig.update_layout(
            xaxis = dict(
                tickmode = 'linear',
                # tick0 = 2554,
                dtick = 2,
                showgrid=False,
                linecolor="#BCCCDC",
                showspikes=True, # Show spike line for X-axis
                # Format spike
                spikethickness=2,
                spikedash="dot",
                spikecolor="#999999",
                spikemode="across",
            ),
            yaxis = dict(
              
                showgrid=False,
                linecolor="#BCCCDC",

            ),
            plot_bgcolor="#FFF",
        )

        fig.update_xaxes(ticks="outside")
        fig.update_yaxes(ticks="outside")

        # fig.update_layout(legend=dict(orientation="h"))
        fig.update_layout(
            margin=dict(t=55),
        )

        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)
        return  plot_div
    
    def get_date_file():
        file_path = """mydj1/static/csv/ranking_isi.csv"""
        t = time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(file_path)))
        d = datetime.strptime(t,"%m/%d/%Y").date() 

        return str(d.day)+'/'+str(d.month)+'/'+str(d.year+543)

    context={
        ###### Head_page ########################    
        # 'head_page': get_head_page(),
        'now_year' : (datetime.now().year)+543,
        #########################################

        #### Graph
        # 'tree_map' : tree_map(),
        'date' : get_date_file(),
        'line_isi' :line_chart_isi(),
        'line_sco' :line_chart_sco(),
        'line_tci' :line_chart_tci(),
       
    }

    return render(request,'importDB/ranking_comparing.html', context)   

@login_required(login_url='login')
def pridiction_ranking(request): #page เพื่อทำนาย ranking ของ PSU

    def moneyformat(x):  # เอาไว้เปลี่ยน format เป็นรูปเงิน
        return "{:,.2f}".format(x)     

    def linear_regression(ranking, shortname):
        
        now_year = (datetime.now().year)+543

        df = pd.read_csv("""mydj1/static/csv/"""+ranking+""".csv""")
        
        df2 = df[['year', 'PSU']]
        
        df2 = df2[df2['year'] != now_year]
        
        x = df2['year'].to_list()
        x = np.array(x)
        x = x.reshape(-1, 1)

        y = df2['PSU'].to_list()
        y = np.array(y)
        y = y.reshape(-1, 1)

        lin_reg = LinearRegression()
        lin_reg.fit(x, y)
        # print(lin_reg.coef_) # ความชัน
        y_pre = lin_reg.predict(x)

       
        df_x = pd.DataFrame(x).rename(columns={0: 'x'})
        df_y = pd.DataFrame(y).rename(columns={0: 'y'})
        df_y_pre = pd.DataFrame(y_pre).rename(columns={0: 'y_pre'})

        # ทำนาย
        x_test_1 = lin_reg.predict([[now_year]])
        x_test_2 = lin_reg.predict([[now_year+1]])
        x_test_3 = lin_reg.predict([[now_year+2]])
        
        # สร้าง dataframe เก็ยผลลัพธ์การทำนาย
        results_pred = pd.DataFrame()
        results_pred['year'] = [now_year,now_year+1,now_year+2]
        results_pred['pred'] = [x_test_1[0][0], x_test_2[0][0] , x_test_3[0][0]]
        
        # ต่อ dataframe เพื่อให้ วาดกราฟเส้นต่อเนื่องกับค่าปี now_year - 1
        end_row = {'year':now_year-1,'pred':df_y.iloc[-1][0]}
        results_pred = results_pred.append(end_row,ignore_index = True) 
        results_pred = results_pred.sort_values(by=['year'])
        results_pred = results_pred.reset_index(drop=True)


        ### หาค่า R-Square
        r2 = r2_score(df_y,df_y_pre)
        print("Linear: R-Square : ",r2)
        # print(df_y_pre)
        # print(df_y)

        return df_x, df_y, results_pred, df_y_pre
        
        # return  plot_div

    def poly_regression(ranking, shortname):
        now_year = (datetime.now().year)+543
        
        df = pd.read_csv("""mydj1/static/csv/"""+ranking+""".csv""")
        
        df2 = df[['year', 'PSU']]

        df2 = df2[df2['year'] != now_year]
        
        x = df2['year'].to_list()
        x = np.array(x)
        x = x.reshape(-1, 1)

        y = df2['PSU'].to_list()
        y = np.array(y)
        y = y.reshape(-1, 1)

        # Traning the poly regression model on  the whole dataset
        poly_features = PolynomialFeatures(degree=4, include_bias=True)  # y = b0 + b1x1 + b2x1^2 ... + b4x1^4
        X=poly_features.fit_transform(x) 
        poly_reg = LinearRegression()
        poly_reg.fit(X, y)
        # print(poly_reg.coef_) # ความชัน
        y_pre = poly_reg.predict(X)
        
        # print(type( poly_reg.predict([[2563]])))
        df_x = pd.DataFrame(x).rename(columns={0: 'x'})
        df_y = pd.DataFrame(y).rename(columns={0: 'y'})
        df_y_pre = pd.DataFrame(y_pre).rename(columns={0: 'y_pre'})
        
        # ทำนาย
        x_test_1 = poly_features.fit_transform([[now_year]])
        x_test_2 = poly_features.fit_transform([[now_year+1]])
        x_test_3 = poly_features.fit_transform([[now_year+2]])
        

        # สร้าง dataframe เก็ยผลลัพธ์การทำนาย
        results_pred = pd.DataFrame()
        results_pred['year'] = [now_year,now_year+1,now_year+2]
        results_pred['pred'] = [poly_reg.predict(x_test_1)[0][0], poly_reg.predict(x_test_2)[0][0] ,  poly_reg.predict(x_test_3)[0][0]]
        
        # ต่อ dataframe เพื่อให้ วาดกราฟเส้นต่อเนื่องกับค่าปี now_year - 1
        end_row = {'year':now_year-1,'pred':df_y.iloc[-1][0]}
        results_pred = results_pred.append(end_row,ignore_index = True) 
        results_pred = results_pred.sort_values(by=['year'])
        results_pred = results_pred.reset_index(drop=True)
 
        ### หาค่า R-Square
        r2 = r2_score(df_y,df_y_pre)
        print("Poly: R-Square : ",r2)

        return df_x, df_y, results_pred, df_y_pre
        
    def support_vector_regression(ranking, shortname): # Support vector regression 
        now_year = (datetime.now().year)+543
        
        df = pd.read_csv("""mydj1/static/csv/"""+ranking+""".csv""")
        df = df[['year', 'PSU']]
        dataset = df[df['year'] != now_year]
        X = dataset.iloc[:,:1].values
        y = dataset.iloc[:,-1].values
    
        df_x = pd.DataFrame(X).rename(columns={0: 'x'})
        df_y = pd.DataFrame(y).rename(columns={0: 'y'})
        

        y = y.reshape(-1, 1)
        from sklearn.preprocessing import StandardScaler
        sc_X = StandardScaler()
        sc_y = StandardScaler()
        X = sc_X.fit_transform(X)
        y = sc_y.fit_transform(y)

        from sklearn.svm import SVR
        regressor = SVR(kernel = 'rbf')

        regressor.fit(X,y)
        # print(regressor.coef_)  # ความชัน
        # ทำนาย
        x_test_1 = sc_y.inverse_transform(regressor.predict(sc_X.transform([[now_year]])))
        x_test_2 = sc_y.inverse_transform(regressor.predict(sc_X.transform([[now_year+1]])))
        x_test_3 = sc_y.inverse_transform(regressor.predict(sc_X.transform([[now_year+2]])))

        results_pred = pd.DataFrame()
        results_pred['year'] = [now_year,now_year+1,now_year+2]
        results_pred['pred'] = [x_test_1[0],x_test_2[0],x_test_3[0]]
        
        # ต่อ dataframe เพื่อให้ วาดกราฟเส้นต่อเนื่องกับค่าปี now_year - 1
        end_row = {'year':now_year-1,'pred':df_y.iloc[-1][0]}
        results_pred = results_pred.append(end_row,ignore_index = True) 
        results_pred = results_pred.sort_values(by=['year'])
        results_pred = results_pred.reset_index(drop=True)

        df_y_pre = pd.DataFrame(sc_y.inverse_transform( regressor.predict(X)),
                   columns=['y_pre'])

        ### หาค่า R-Square
        r2 = r2_score(df_y,df_y_pre)
        print("Support Vector: R-Square : ",r2)

        return  df_x, df_y, results_pred, df_y_pre 

    def ARIMA_regression(ranking, shortname): # ARIMA regression 
        now_year = (datetime.now().year)+543
        
        df = pd.read_csv("""mydj1/static/csv/"""+ranking+""".csv""")
        params = pd.read_csv("""mydj1/static/csv/params_arima.csv""")  # เปิดไฟล์เก็บ parameter ของ library ARIMA
        
        df = df[['year', 'PSU']]
        dataset = df[df['year'] != now_year]
        
        df_x = df["year"][:-1:].to_frame().rename(columns={'year': "x"})
        df_y = df["PSU"][:-1:].to_frame().rename(columns={'PSU': "y"})
  
        df_2 = df[['year','PSU']][:-1:]
        
        # log test : ทำการ take log ฐาน e ให้กับ ค่าจำนวนการตีพิมพ์ เพื่อ ให้เหมาะสมกับการทำ ARIMA_regression
        log = np.log(df_2["PSU"])
        df_log = pd.DataFrame({'year':df.year[:-1],'PSU': log})
        df_log = df_log.set_index('year')
        
        ## สร้าง pdq parameter เพื่อ วน test หา parameter ที่ดีที่สุด
        # p=d=q = range(0,3)
        # pdq = list(itertools.product(p,d,q))

        # ##ทำการ วน test หา parameter ที่ดีที่สุด #####
        # warnings.filterwarnings('ignore')
        # aics = []
        # combs = {}
        # for param in pdq:
        #     try:
        # #         print(param)
        #         model = ARIMA(df_log, order=param)
        #         model_fit = model.fit(disp=0)
        # #         results = model_fit.plot_predict(dynamic=False)
        # #         plt.show()
        #         print(param,":",model_fit.aic)
        #         combs.update({model_fit.aic : [param]})
        #         aics.append(model_fit.aic)
        #     except:
        #         continue

        ## เมื่อได้ parameter ที่ดีที่สุด ทำการ fit model
        # model = ARIMA(df_log, order=combs[min(aics)][0])
        # print(combs[min(aics)][0])

        #### เเปลง parameter ที่ได้ มาเป็น tuple ของ int########
        tup = tuple(params.loc[0][ranking])
        parameter = (int(tup[1]),int(tup[4]), int(tup[7]))
        ####################################################

        ############ เรียกใช้ ARIMA MODEL และ FIT ###########
        model = ARIMA(df_log, order=parameter)
        model_fit = model.fit() 
        ###################################################

        ## ทำการเตรียม output เพื่อ return ไป plot graph
        now_year = (datetime.now().year)+543
        
        index = df[df['year']==now_year].index.values

        # prediction line 3 ปี ล่วงหน้า
        con_df1 = pd.DataFrame({'year':[now_year-1],'pred':df_2.iloc[index[0]-1][1]})
        con_df2 = pd.DataFrame({'year':[now_year,now_year+1,now_year+2],'pred':model_fit.forecast(steps=3)[0]})
        con_df2['pred'] = con_df2['pred'].apply(lambda x : np.e**x )
        results_pred= pd.concat([con_df1,con_df2], ignore_index=True)

        # trend line
        trend = model_fit.predict(typ='levels')
        results_trend = trend.to_frame()
        results_trend.rename(columns={0: "y_pre"}, inplace=True)
        results_trend_real= results_trend.apply(lambda x : np.e**x )  # แทนค่ากลับ เพราะค่าเดิมถูก logarithm ฐาน e ไว้ 
        df_pred = results_trend_real.reset_index(drop = True)  
        
        ### เนื่องจากแต่ละ dataset จะใช้ ARIMA model โดยจะมีพารามิเตอร์ตัวที่ 2 ต่างกัน (จากทั้งหมด 3 ตัว) 
        ### ดังนั้น ถ้า d = 1 : trend line เริ่มต้นจาก ค่า 0
        ###      ถ้า d = 2 : trend line จะ เริ่มต้น ด้วย 0 และ 0 
        ###       ต่อไปเรื่อยๆ จึงต้องวน for ตรวจสอบค่าเริ่มต้น ว่าเป็น 0 กี่ตัว ตามพารามิเตอร์ ที่ 2 (tup[4])
        first_values = [0 for x in range(0,int(tup[4]))]
        value0 = pd.DataFrame({'y_pre':first_values})

        df_pred= pd.concat([value0 ,df_pred], ignore_index=True) ## รวม first value 0 และ trend_line

        ### หาค่า R-Square
        r2 = r2_score(df_y,df_pred)
        print("ARIMA: R-Square : ",r2)

        return  df_x, df_y, results_pred, df_pred
     
    def plot_graph(ranking, shortname):

        now_year = (datetime.now().year)+543
        df = pd.read_csv("""mydj1/static/csv/"""+ranking+""".csv""")
        
        data = df[['year', 'PSU']]

        data = data[data['year'] != now_year]
        
        x = data['year'].to_list()
        x = np.array(x)
        x = x.reshape(-1, 1)

        y = data['PSU'].to_list()
        y = np.array(y)
        y = y.reshape(-1, 1)

        df_x = pd.DataFrame(x).rename(columns={0: 'x'})
        df_y = pd.DataFrame(y).rename(columns={0: 'y'})
        
        # สร้าง table เพื่อรวมผลลัพธ์ ของทั้งหมด มาวาดตาราง
        table = df[['year', 'PSU']].drop([df.index[-1]]).rename(columns={'PSU': 'pred'})  # ลบปี ปัจจุบัน และ เปลี่ยนชื่อ column เป็น pred เพื่อให้ append กันได้
        table = table.round(2)
        table = table.sort_values(by='year', ascending=False) # เรียงปี จากมากไปน้อย 
        table['pred'] = table['pred'].apply(moneyformat)
        
        fig = make_subplots(rows=1, cols=2,
                                column_widths=[0.7, 0.3],
                                specs=[[{"type": "scatter"},{"type": "table"}]],
                                # start_cell="bottom-left",
                                # horizontal_spacing= 0.1
                                
                                )

        # font_color = ['blue' if i >= len(table.index)-3 else 'rgb(10,10,10)' for i in table.index] # สีตาราง
        fig.add_trace(
                go.Table(
                    columnwidth = [80,100],
                    header=dict(values=["<b>ปี</b>","<b>จำนวนครั้ง<b>"],
                                fill = dict(color='#C2D4FF'),
                                align = ['center'] * 5,
                                font = dict( size = 14),),
                    cells=dict(values=[table.year, table.pred],
                            fill = dict(color='#F5F8FF'),
                            align = ['center','right'] * 5,
                            # font=dict(color=[font_color])
                            ))
                    , row=1, col=2)

        label = ""
        df_x, df_y, results_pred, df_y_pre = [],[],[],[]
        color = ""
        visible = True
        
        for n in range(4):
            try:
                
                if n ==0: # ARIMA_regression
                    df_x, df_y, results_pred, df_y_pre = ARIMA_regression(ranking, shortname)
                    label = "ARIMA Regression"
                    color_dot = "#2ECC71"
                    color_line = "#82E0AA"
                    visible = True

                elif n == 1: # poly_regression
                    df_x, df_y, results_pred, df_y_pre = poly_regression(ranking, shortname)
                    label = "Polynomial Regression" 
                    color_dot = "#9B59B6"
                    color_line = "#D2B4DE"
                    visible = "legendonly"  # ไม่ใช้แสดง legend ตอนเริ่มแรก

                elif n == 2: # linear_regression
                    df_x, df_y, results_pred, df_y_pre = linear_regression(ranking, shortname)
                    label = "Linear Regression"
                    color_dot = "#E74C3C"   
                    color_line = "#F5B7B1"
                    visible = "legendonly"  # ไม่ใช้แสดง legend ตอนเริ่มแรก

                elif n == 3: # support_vector_regression
                    df_x, df_y, results_pred, df_y_pre = support_vector_regression(ranking, shortname)
                    label = "Support Vector Regression"
                    color_dot = "#F1C40F"
                    color_line = "#F9E79F"
                    visible = "legendonly"  # ไม่ใช้แสดง legend ตอนเริ่มแรก
                
                # เเก้ไข dataframe ของ prediction line (เส้นประ) นิดหน่อย เพื่อให้ เป็นเส้นต่อเนื่องกันกับ trend line (เส้นทึบ)
                # if(graph_type == "bar"):
                results_pred.loc[results_pred['year']==now_year-1,['pred']] = df_y_pre.iloc[-1][0] 
                
                fig.add_trace(go.Scatter(x=df_x['x'], y=df_y_pre['y_pre'],  # วาด Trend Line 
                                mode='lines',
                                line=dict( width=3,color=color_line),
                                name=label+'| Trend Line',
                                legendgroup = label,
                                visible = visible
                                ))

                fig.add_trace(go.Scatter(x=results_pred['year'], y=results_pred['pred'],  # เส้นผลลัพธ์การทำนาย เส้นประ
                                mode='markers+lines',
                                line=dict( width=3, dash='dot',color=color_dot),
                                name=label+'| Predicted Line',
                                legendgroup = label,
                                visible = visible
                                ))
            except:
                continue
        
        # วาด bar Actual line สีฟ้า
        fig.add_trace(go.Bar(x=df_x['x'], y=df_y['y'],  
                                visible = 'legendonly',
                                marker_color='royalblue',
                                name='Actual Bar Graph',
                                # width=2,
                                # text=df_y['y'],
                                # textposition='auto',
                                marker_line_color='rgb(8,48,107)',
                                marker_line_width=1.5, opacity=0.6
                                )
                    , row=1, col=1)
        # วาดเส้น Actual line สีฟ้า
        fig.add_trace(go.Scatter(x=df_x['x'], y=df_y['y'],  
            mode='markers+lines',
            line=dict( width=2,color='royalblue'),
            name='Actual Line Graph',
            visible = True
            ), row=1, col=1)

          
        fig.update_layout(autosize=True
                        # ,height=500,width=1100,
        )
        # fig.update_layout(legend=dict(x=1, y=1))
        fig.update_layout(
            title_text=f"""<b>ฐานข้อมูล :</b> """+shortname,        
            plot_bgcolor="#FFF",
            xaxis = dict(
                    tickmode = 'linear',
                    dtick = 2,
                    showgrid=False,
                    linecolor="#BCCCDC",
                ),
                yaxis = dict(
                    showgrid=False,
                    linecolor="#BCCCDC", 
                ),
            xaxis_title="<b>ปี พ.ศ.</b>",
            yaxis_title="<b>จำนวนครั้งของการตีพิมพ์</b>",
        )

        fig.update_xaxes( 
                        ticks="outside",
                        showspikes=True,
                        spikethickness=2,
                        spikedash="dot",
                        spikecolor="#999999",)
        fig.update_yaxes(
                        ticks="outside",
                        showspikes=True,
                        spikethickness=2,
                        spikedash="dot",
                        spikecolor="#999999",)

        # fig.update_layout(
            # margin=dict(l=20, r=200, t=50, b=20),
        # )
        fig.update_layout(legend_title_text='<b>Models</b>')
        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)
        
        return plot_div

    filter_ranking = 'ranking_isi'
    selected_ranking = 'ISI-WoS'
    ranking_name = {'ISI-WoS':'ranking_isi' ,'Scopus':'ranking_scopus',"TCI":'ranking_tci'}
    
    if request.method == "POST":
        filter_ranking =  ranking_name[request.POST["data"]]   #รับ ชื่อ ranking จาก dropdown 
        selected_ranking = request.POST["data"]


    context={
        ###### Head_page ########################    
        # 'head_page': get_head_page(),
        'now_year' : (datetime.now().year)+543,
        #########################################

        #### 
        'ranking_name'  :ranking_name.keys(),
        'filter_ranking' : selected_ranking,
        'graph' : plot_graph(filter_ranking, selected_ranking),
        
        

    }
    
    return render(request,'importDB/ranking_prediction.html',context)  

@login_required(login_url='login')
def pageResearchMan(request):
    
    selected_year = datetime.now().year+543 # กำหนดให้ ปี ใน dropdown เป็นปีปัจจุบัน
    
    def get_head_page(): # get 
        df = pd.read_csv("""mydj1/static/csv/head_page.csv""")
        return df.iloc[0].astype(int)

    if request.method == "POST":
        filter_year =  request.POST["year"]   #รับ ปี จาก dropdown 
        print("post = ",request.POST )
        selected_year = int(filter_year)      # ตัวแปร selected_year เพื่อ ให้ใน dropdown หน้าต่อไป แสดงในปีที่เลือกไว้ก่อนหน้า(จาก year)
    
    # print(type(selected_year))
    
    def num_main_research():

        df = pd.read_csv("""mydj1/static/csv/main_research.csv""", index_col=0)
        df = df.loc[(df.index == selected_year)]
        
        teacher = df.teacher[selected_year]
        res_staff = df.research_staff[selected_year]
        post_doc = df.post_doc[selected_year]
        asst_staff = df.asst_staff[selected_year]
        re_df = pd.DataFrame({'teacher': [teacher], 'res_staff': [res_staff], 'post_doc':[post_doc], 'asst_staff':[asst_staff]})
        
        return re_df.iloc[0]

    def graph_revenue_research():  # กราฟ ผู้วิจัยที่ได้รับทุน

        df = pd.read_csv("""mydj1/static/csv/main_research_revenue.csv""", index_col=0)
        
        ####  plot กราฟ เฉพาะ 10 ปีย่อนหลัง
        df_1 = df[-10:]

        colors = ['royalblue',] * 9  # สีกราฟปี9ย้อนหลัง
        colors.append('lightslategray') # สีกราฟปีปัจุบัน 

        fig = go.Figure(data=[go.Bar(
            x=df_1.index,
            y=df_1['count'],
            name="",
            marker_color=colors, # marker color can be a single color value or an iterable
            textposition="inside",
            textfont_color="white",
            textangle=0,
            texttemplate="%{y}",
            hovertemplate="<br>".join([
                "ปี พ.ศ.: %{x}",
                "จำนวน: %{y}",

            ])
        )])

        fig.update_traces( textposition= 'auto' )
        fig.update_traces( marker_line_color='black',
                  marker_line_width=1.5,opacity=0.9 )
        fig.update_layout(
            xaxis_title="<b>ปี พ.ศ.</b>",
            yaxis_title="<b>จำนวน (คน)</b>",
        )
        
        fig.update_xaxes(ticks="outside")
        fig.update_yaxes(ticks="outside")
        fig.update_layout(hovermode="x")   
        fig.update_layout(
            margin=dict(t=50),
            plot_bgcolor="#FFF",
            xaxis = dict(
                tickmode = 'linear',
                dtick = 1,
                showgrid=False,
                linecolor="#BCCCDC", 
            ),
            yaxis = dict(
                showgrid=False,
                linecolor="#BCCCDC", 
            ),
        )

        plot_div = plot(fig, output_type='div', include_plotlyjs=False,)
        return  plot_div

    def get_date_file():
        file_path = """mydj1/static/csv/ranking_isi.csv"""
        t = time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(file_path)))
        d = datetime.strptime(t,"%m/%d/%Y").date() 

        return str(d.day)+'/'+str(d.month)+'/'+str(d.year+543)
        
    context={
        ###### Head_page ########################    
        'head_page': get_head_page(),
        'now_year' : (datetime.now().year)+543,
        'date' : get_date_file(),
        #########################################

        #### Graph
        # 'tree_map' : tree_map(),
        'year' :(range((datetime.now().year-9)+543,(datetime.now().year+1)+543)),
        'filter_year' : selected_year,
        'num_main_research' : num_main_research(),
        'graph_revenue_research' : graph_revenue_research(),
        'top_bar_title': "จำนวนผู้วิจัย"
        
       
    }

    
    
    return render(request,'importDB/research_man.html',context)  


@login_required(login_url='login')
def test_page(request):
    context={
        
       
    }


    return render(request,'importDB/test-page.html',context) 
##################################################################
##### " function Login ##############
##################################################################
def login_(request):
    print("---login---")
    username = ""
    passowrd = ""
    default_pass = 'pass11111' #รหัสหลอก เพื่อให้ เข้า auth ของ Django ได้
    
    if request.method == "POST":
        username = request.POST.get('username') # RO ใช้ username = request.POST['username']
        password = request.POST.get('password')

        # password = "\""+password+"\""  # ทำการ ใส่ "  " ให้กับ password เพราะ อาจจะมี charactor พิเศษ ที่ทำให้เกิด error เช่น มี & | not ใน password
        
        # ทำการ ตรวจสอบ user และ pass จาก index.php และ ldappsu.php โดย ถ้ามี user ใน psupassport จะ Return เป็น "1,รหัสพนักงาน" ถ้าไม่มีจะ return 0 
        # print("user = ",username)
        # print("pass = ",password)
        
        #####################################
        ############## PSU Ldap.php##########
        #####################################
        # proc = subprocess.Popen("""php importDB/index.php """+username+""" """+password , shell=True, stdout=subprocess.PIPE) #Call function authentication from PHP
        # script_response = proc.stdout.read()

        # decode = script_response.decode("utf-8")  # ทำการ decode จาก bit เป็น string

        # user_list = decode.split(",") # split ข้อมูล ด้วย , 
        # # print(script_response)
        # # print("list --> ",decode)
        # # print(user_list[0])
        # # print(user_list[1])
        
        # #Call function authentication from django
        # # user_list[1]
        # user = authenticate(request, username = '0111111' , password = default_pass) # นำ รหัสพนักงาน (user_list[1]) มาตรวจสอบว่าอยู่ใน ฐานข้อมูล django หรือไม่ โดยใช้รหัส default
        user = authenticate(request, username = username , password = password)

        # if ((user_list[0] == "1") & (user is not None)):  # ถ้า เจอ user ใน ระบบ psupassport และ เจอ user ใน ฐานข้อมูล django ให้ทำการเข้าสู่ระบบได้
        if (user is not None):
            login(request, user)  # ทำการเข้าสู่ระบบ
            return redirect('home-page')  # เมื่อเข้าสู่ระบบเเล้ว ทำการเปิดหน้าแรกของ page
            
        else:
            # print("ไม่พบ user")
            messages.info(request, 'Username หรือ password ไม่ถูกต้อง')


    context={
        
    }
    return render(request,'importDB/login.html',context)

def login_2(request):
    print("---login---")
    username = ""
    passowrd = ""
    default_pass = 'pass11111' #รหัสหลอก เพื่อให้ เข้า auth ของ Django ได้
    
    if request.method == "POST":
        username = request.POST.get('username') # RO ใช้ username = request.POST['username']
        password = request.POST.get('password')

        password = "\""+password+"\""  # ทำการ ใส่ "  " ให้กับ password เพราะ อาจจะมี charactor พิเศษ ที่ทำให้เกิด error เช่น มี & | not ใน password
        
        # ทำการ ตรวจสอบ user และ pass จาก index.php และ ldappsu.php โดย ถ้ามี user ใน psupassport จะ Return เป็น "1,รหัสพนักงาน" ถ้าไม่มีจะ return 0 
        # print("user = ",username)
        # print("pass = ",password)
        proc = subprocess.Popen("""php importDB/index.php """+username+""" """+password , shell=True, stdout=subprocess.PIPE) #Call function authentication from PHP
        script_response = proc.stdout.read()

        decode = script_response.decode("utf-8")  # ทำการ decode จาก bit เป็น string

        user_list = decode.split(",") # split ข้อมูล ด้วย , 
        print(script_response)
        print("list --> ",decode)
        # print(user_list[0])
        # print(user_list[1])
        
        #Call function authentication from django
        # user_list[1]
        user = authenticate(request, username = '0111111' , password = default_pass) # นำ รหัสพนักงาน (user_list[1]) มาตรวจสอบว่าอยู่ใน ฐานข้อมูล django หรือไม่ โดยใช้รหัส default

        if ((user_list[0] == "1") & (user is not None)):  # ถ้า เจอ user ใน ระบบ psupassport และ เจอ user ใน ฐานข้อมูล django ให้ทำการเข้าสู่ระบบได้
            login(request, user)  # ทำการเข้าสู่ระบบ
            return redirect('home-page')  # เมื่อเข้าสู่ระบบเเล้ว ทำการเปิดหน้าแรกของ page
            
        else:
            # print("ไม่พบ user")
            messages.info(request, 'Username หรือ password ไม่ถูกต้อง')


    context={
        
    }
    return render(request,'importDB/login.html',context)


# %%
print("Running")

