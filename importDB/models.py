from django.db import models
from django.utils import timezone
from datetime import datetime
# Create your models here.

class Get_db(models.Model):  #สร้างตาราง
    customer_id = models.IntegerField()
    first_name = models.CharField(max_length = 200)
    last_name = models.CharField(max_length = 200)

class Get_db_oracle(models.Model):
    customer_id = models.CharField(max_length = 3)
    fullname = models.CharField(max_length = 200)
    email = models.EmailField()
    country_code = models.CharField(max_length = 2)
    budget = models.IntegerField()
    used = models.FloatField()

class Prpm_v_grt_project_eis(models.Model):
    psu_project_id = models.CharField(max_length = 5)
    submit_name_surname_th = models.CharField(max_length = 500)
    pj_status_th = models.CharField(max_length = 500)
    fund_budget_year = models.IntegerField()
    fund_source_th = models.CharField(max_length = 500)
    fund_type_th = models.CharField(max_length = 300)
    faculty_owner = models.CharField(max_length = 300)
    camp_owner = models.CharField(max_length = 300)
    sum_budget_plan = models.DecimalField(max_digits=19, decimal_places=10)

    def __str__(self):  # def นี้ ทำให้ ชื่อของ model ไปแสดงในหน้า /admin 
        return self.psu_project_id


class PRPM_v_grt_pj_team_eis(models.Model):
    staff_id = models.IntegerField()
    user_real_name_th = models.CharField(max_length = 300)
    user_last_name_th = models.CharField(max_length = 300)

    def __str__(self):  # def นี้ ทำให้ ชื่อของ model ไปแสดงในหน้า /admin 
        return self.staff_id 

class PRPM_v_grt_pj_budget_eis(models.Model):
    psu_project_id = models.IntegerField()
    budget_group_desc = models.CharField(max_length = 50)
    budget_type_th = models.CharField(max_length = 50)
    budget_source_th =models.CharField(max_length = 50)
    budget_year = models.IntegerField()
    budget_amount = models.IntegerField()

    def __str__(self):  # def นี้ ทำให้ ชื่อของ model ไปแสดงในหน้า /admin 
        return self.psu_project_id   

class HRMIS_V_AW_FOR_RANKING(models.Model):
    STAFF_ID = models.CharField(max_length = 5)
    FNAME_THAI = models.CharField(max_length = 300)
    LNAME_THAI = models.CharField(max_length = 300)
    FNAME_ENG = models.CharField(max_length = 300)
    LNAME_ENG = models.CharField(max_length = 300)
    POS_NAME_THAI = models.CharField(max_length = 300)
    TYPE_ID = models.IntegerField()
    CORRESPONDING = models.IntegerField()
    END_YEAR = models.IntegerField()
    JDB_ID = models.IntegerField()
    JDB_NAME = models.CharField(max_length = 500)
    AT_PERCENT = models.IntegerField()

    def __str__(self):  # def นี้ ทำให้ ชื่อของ model ไปแสดงในหน้า /admin 
        return self.STAFF_ID+" "+self.FNAME_THAI+" "+self.LNAME_THAI


class PRPM_r_fund_type(models.Model):
    fund_type_id = models.IntegerField()
    fund_type_th = models.CharField(max_length = 300)
    fund_source_id = models.CharField(max_length = 2)
    fund_type_group = models.IntegerField()

    def __str__(self):  # def นี้ ทำให้ ชื่อของ model ไปแสดงในหน้า /admin 
        return str(self.fund_type_id)+" "+self.fund_type_th 


class master_ranking_university_name(models.Model):
    BOOL_CHOICES = ((True,'ใช้'),
            (False, 'ไม่ใช้'))
    short_name = models.CharField(max_length = 5)
    name_eng = models.CharField(max_length = 300)
    name_th = models.CharField(max_length = 300)
    af_id = models.CharField(max_length = 100, blank = True, null = True)   # blank = True, null = True จะใช้คู่กัน เพื่อบอกว่า field นี้สามารถเป็นค่าว่างได้
    color = models.CharField(max_length = 10, blank = True, null = True)
    flag_used = models.BooleanField(choices=BOOL_CHOICES, default=True)

    def __str__(self):  # def นี้ ทำให้ ชื่อของ model ไปแสดงในหน้า /admin 
        return self.short_name+" "+self.name_eng 

class Science_park_rawdata(models.Model):
    kpi_number = models.IntegerField()
    kpi_name = models.CharField(max_length = 300)
    year = models.IntegerField(default = int(datetime.now().year)+543)
    number = models.IntegerField(default=0,)
    modified = models.DateTimeField(blank = True, null = True)
  
    def __str__(self):  # def นี้ ทำให้ ชื่อของ model ไปแสดงในหน้า /admin 
        return self.kpi_name+", "+str(self.year)

    def save(self, *args, **kwargs): ### บันทึกวันที่ อัตโนมัติ
        #''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()

        return super(Science_park_rawdata, self).save(*args, **kwargs)


class Science_park_PITI(models.Model):
    request_no = models.CharField(max_length = 100)
    title = models.CharField(max_length = 1000)
    rcv_date = models.CharField(max_length = 2)
    type_group = models.CharField(max_length = 15)

    def __str__(self):  # def นี้ ทำให้ ชื่อของ model ไปแสดงในหน้า /admin 
        return str(self.request_no)+" "+self.title 