from __future__ import absolute_import, unicode_literals

from celery import shared_task
import time
from . import views
from celery.schedules import crontab
from celery.task import periodic_task

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
def dump1():
    try:

        dt = datetime.now()
        timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6

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
                    where budget_year between YEAR(date_add(NOW(), INTERVAL 543 YEAR))-10 and YEAR(date_add(NOW(), INTERVAL 543 YEAR))
                    group by 1,2,3 """

        con_string = views.getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)

        ############## build dataframe for show in html ##################
        index_1 = df["budget_year"].unique()
        df2 = pd.DataFrame(columns=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],index = index_1)    
        for index, row in df.iterrows():
            df2[row['budget_source_group_id']][row["budget_year"]] = row['sum_final_budget']
        df2 = df2.fillna(0.0)
        df2 = df2.sort_index(ascending=False)
        df2 = df2.head(10).sort_index()
            
        
        ########## save to csv ตาราง เงิน 12 ประเภท ##########      
        if not os.path.exists("mydj1/static/csv"):
                os.mkdir("mydj1/static/csv")
                
        df2.to_csv ("""mydj1/static/csv/12types_of_budget.csv""", index = True, header=True)

        ##################################################
        ################## save ตาราง แยกคณะ #############
        ##################################################
        sql_cmd =  '''WITH temp1 AS (
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
                            WHERE budget_year between YEAR(date_add(NOW(), INTERVAL 543 YEAR))-10 and YEAR(date_add(NOW(), INTERVAL 543 YEAR))      
                            GROUP BY 1, 2, 3, 4, 5, 6
                                '''

        con_string = views.getConstring('sql')
        df = pm.execute_query(sql_cmd, con_string)
        df.to_csv ("""mydj1/static/csv/budget_of_fac.csv""", index = False, header=True)
    

        print ("Saved")

    except Exception as e :
        checkpoint = False
        print('Something went wrong :', e)

    print("end Dump1")
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

def dump3():
    ranking = " "
    dt = datetime.now()
    now_year = dt.year+543

    try: 
        ########################
        #### สร้าง df เพื่อ บันทึก ISI #########
        ########################
        print("Start Dump3")
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

    # try:
    #     ########################
    #     #### สร้าง df เพื่อ บันทึก scopus #########
    #     ########################
    #     print("start SCOPUS update")
    #     sco_df = sco(now_year-543)  # get scopus dataframe จาก API scopus_search
        
    #     if(sco_df is None): 
    #         print("Scopus can't scrap")
    #     else:
    #         print("finished_web_scraping_Scopus")

    #     sco_df.set_index('year', inplace=True)
    #     df = pd.read_csv("""mydj1/static/csv/ranking_scopus.csv""", index_col=0)
        
    #     if df[-1:].index.values != now_year: # เช่น ถ้า เป็นปีใหม่ (ไม่อยู่ใน df มาก่อน) จะต้องใส่ index ปีใหม่ โดยการ append
    #         df.loc[now_year-1:now_year-1].update(sco_df.loc[now_year-1:now_year-1])  #ปีใหม่ - 1
    #         df =  df.append(sco_df.loc[now_year:now_year])  # ปีใหม่
            
    #     else :  
    #         df.loc[now_year:now_year].update(sco_df.loc[now_year:now_year])  # ปีปัจจุบัน 
    #         df.loc[now_year-1:now_year-1].update(sco_df.loc[ now_year-1:now_year-1]) # ปีปัจจุบัน - 1
            
    #     ########## save df scopus to csv ##########      
    #     if not os.path.exists("mydj1/static/csv"):
    #             os.mkdir("mydj1/static/csv")
                
    #     df.to_csv ("""mydj1/static/csv/ranking_scopus.csv""", index = True, header=True)
    #     print("Scopus saved")
    #     ranking = ranking + "SCO Ok!, "

    # except Exception as e:
    #     print("SCO Error: "+str(e))
    #     ranking = ranking + "SCO Error, "
    
    # try:
    #     ########################
    #     #### สร้าง df เพื่อ บันทึก TCI #########
    #     ########################
    #     print("start TCI update")
    #     tci_df = tci()  # get TCI dataframe จาก web Scraping
    #     if(tci_df is None): 
    #         print("TCI'web scraping ERROR 1 time, call TCI() again....")
    #         tci_df = tci()
    #         if(tci_df is None): 
    #             print("TCI'web scraping ERROR 2 times, break....")
    #     else:
    #         print("finished_web scraping_TCI")

    #     tci_df.set_index('year', inplace=True)

    #     df = pd.read_csv("""mydj1/static/csv/ranking_tci.csv""", index_col=0)
    
    #     if df[-1:].index.values != now_year: # เช่น ถ้า เป็นปีใหม่ (ไม่อยู่ใน df มาก่อน) จะต้องใส่ index ปีใหม่ โดยการ append
    #         df.loc[now_year-1:now_year-1].update(tci_df.loc[now_year-1:now_year-1])  #ปีใหม่ - 1
    #         df =  df.append(tci_df.loc[now_year:now_year])  # ปีใหม่
    #     else :  
    #         df.loc[now_year:now_year].update(tci_df.loc[now_year:now_year])  # ปีปัจจุบัน 
    #         df.loc[now_year-1:now_year-1].update(tci_df.loc[ now_year-1:now_year-1]) # ปีปัจจุบัน - 1
        
    #     ########## save df TCI  to csv ##########      
    #     if not os.path.exists("mydj1/static/csv"):
    #             os.mkdir("mydj1/static/csv")
                
    #     df.to_csv ("""mydj1/static/csv/ranking_tci.csv""", index = True, header=True)
    #     print("TCI saved")
    #     ranking = ranking + "TCI Ok!, "

    except Exception as e:
        print("TCI Error: "+str(e))
        ranking = ranking + "TCI Error, "

    #############  end #####################

    print("End dump3")
    return None

def dump_RawData_1(): #project
    try:
        print("Start dump RawData ---> importdb_prpm_v_grt_project_eis")
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

        engine = create_engine(ENGINE_PATH_WIN_AUTH, encoding="latin1" )
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
        
        dt = datetime.now()
        timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
        print(type(timestamp))
        print("Finished dump RawData---> importdb_prpm_v_grt_project_eis : at "+str(timestamp))

    except Exception as e :
        print('Something went wrong :', e)

def dump_RawData_2(): #team
    try:
        print("Start dump RawData ---> cleaned_prpm_team_eis")
        sql_cmd =""" select * from research60.v_grt_pj_team_eis"""
        DIALECT = 'oracle'
        SQL_DRIVER = 'cx_oracle'
        USERNAME = 'pnantipat' #enter your username
        PASSWORD = urllib.parse.quote_plus('sfdgr4g4') #enter your password
        HOST = 'delita.psu.ac.th' #enter the oracle db host url
        PORT = 1521 # enter the oracle port number
        SERVICE = 'delita.psu.ac.th' # enter the oracle db service name
        ENGINE_PATH_WIN_AUTH = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + PASSWORD +'@' + HOST + ':' + str(PORT) + '/?service_name=' + SERVICE

        engine = create_engine(ENGINE_PATH_WIN_AUTH, encoding="latin1" )
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
        dt = datetime.now()
        timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
        print("Finished dump RawData---> cleaned_prpm_team_eis")

    except Exception as e :
        print('Something went wrong :', e)

def dump_RawData_3(): #budget
    try:
        print("Start dump RawData ---> cleaned_prpm_budget_eis")
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

        engine = create_engine(ENGINE_PATH_WIN_AUTH, encoding="latin1" )
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
        dt = datetime.now()
        timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
        print("Finished dump RawData---> cleaned_prpm_budget_eis")

    except Exception as e :
        print('Something went wrong :', e)

def dump_RawData_4():
    try:
        print("Start dump RawData ---> importdb_prpm_r_fund_type")
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
        print("Finished dump RawData ---> importdb_prpm_r_fund_type")

    except Exception as e :
        print('Something went wrong :', e)

def dump_RawData_5():
    try:
        print("Start dump RawData ---> importdb_PRPM_v_grt_pj_assistant_eis")
        whichrows = 'row5'
        sql_cmd =  """SELECT 
                    *
                FROM research60.v_grt_pj_assistant_eis
                """

        con_string = views.getConstring('oracle')
        engine = create_engine(con_string, encoding="latin1" )
        df = pd.read_sql_query(sql_cmd, engine)
        # df = pm.execute_query(sql_cmd, con_string)
        

        ###################################################
        # save path
        con_string2 = views.getConstring('sql')
        pm.save_to_db('importdb_PRPM_v_grt_pj_assistant_eis', con_string2, df)

        dt = datetime.now()
        timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
        print("Finished dump RawData ---> importdb_PRPM_v_grt_pj_assistant_eis")

    except Exception as e :
        print('Something went wrong :', e)

def dump_RawData_6():
    try:
        print("Start dump RawData ---> importdb_hrmis_v_aw_for_ranking")
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

        con_string = views.getConstring('oracle')
        engine = create_engine(con_string, encoding="latin1" )
        df = pd.read_sql_query(sql_cmd, engine)
        print(df.head())
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
        con_string2 = views.getConstring('sql')
        pm.save_to_db('importdb_hrmis_v_aw_for_ranking', con_string2, df)

        # get date
        dt = datetime.now()
        timestamp = time.mktime(dt.timetuple()) + dt.microsecond/1e6
        print("Finished dump RawData ---> importdb_hrmis_v_aw_for_ranking")

    except Exception as e :
        print('Something went wrong :', e)


@shared_task
def tasks_dump():
    # dt = datetime.now()
    print("Starting Dump Data at")
    dump_RawData_1()
    dump_RawData_2()
    dump_RawData_3()
    dump_RawData_4()
    dump_RawData_5()
    dump_RawData_6()
    return None