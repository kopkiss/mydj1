from django.contrib import admin
from .models import Get_db
from .models import Get_db_oracle
from .models import Prpm_v_grt_project_eis
from .models import PRPM_v_grt_pj_team_eis
from .models import PRPM_v_grt_pj_budget_eis

from .models import PRPM_r_fund_type
from .models import master_ranking_university_name
from .models import HRMIS_V_AW_FOR_RANKING
from .models import Science_park_rawdata
from .models import Science_park_PITI

from import_export.admin import ImportExportModelAdmin


# Register your models here.
admin.site.register(Get_db)
class ora(admin.ModelAdmin):  
    list_display = ['customer_id', 'fullname','email','budget']   # ใส่ชื่อ ฟิวล์ ที่ต้องการแสดง
    list_filter = ['customer_id']  # สามารถเพิ่ม ตัว filter ได้
    list_editable = ['fullname','budget']  # สามารถ เพิ่ม การแก้ไข ฟิวล์ได้ 

admin.site.register(Get_db_oracle,ora)
admin.site.register(Prpm_v_grt_project_eis)
admin.site.register(PRPM_v_grt_pj_team_eis)
admin.site.register(PRPM_v_grt_pj_budget_eis)
admin.site.register(PRPM_r_fund_type)
admin.site.register(HRMIS_V_AW_FOR_RANKING)


# ตัวอย่าง ถ้าต้องการให้แสดง ตาราง ในหน้า admin 
# 1. สร้าง class ที่ต้องการให้แสดง
# class ranking(admin.ModelAdmin):  
#     list_display = ['year', 'sco', 'isi', 'tci']   # ใส่ชื่อ ฟิวล์ ที่ต้องการแสดง
#     list_display_links = ('year',)  # ใส่ชื่อ ฟิลล์ ลิงค์ ที่จะให้กดเข้าไปแก้ไข ฟิวล์ ทั้งหมด
#     list_filter = ['year']  # สามารถเพิ่ม ตัว filter ได้
#     list_editable = ['sco','tci']  # สามารถ เพิ่ม การแก้ไข ฟิวล์ได้ ในหน้าแรกเลย ไมต้องกดเข้าไปจาก list_display_links
# 2. register ชื่อ ฐานข้อมูล และ ชื่อ class 
# admin.site.register(PRPM_ranking, ranking )


# 1. สร้าง class ที่ต้องการให้แสดง
class master_university_name(admin.ModelAdmin):  
    list_display = ['short_name', 'name_eng', 'flag_used']   # ใส่ชื่อ ฟิวล์ ที่ต้องการแสดง
    list_display_links = ('short_name',)
    list_filter = ['short_name']  # สามารถเพิ่ม ตัว filter ได้
    # list_editable = ['name_eng']  # สามารถ เพิ่ม การแก้ไข ฟิวล์ได้ ในหน้าแรกเลย ไม่ต้องกดเข้าไปข้างใน
# 2. register ชื่อ ฐานข้อมูล และ ชื่อ class 
admin.site.register(master_ranking_university_name, master_university_name )

@admin.register(Science_park_rawdata)
class ViewAdmin(ImportExportModelAdmin):
    pass








