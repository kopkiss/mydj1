from django.urls import path, include
from . import views  # . คือ อยู่ใน folder เดียวกัน
from django.views.generic import TemplateView



urlpatterns = [
    path('', views.pageResearchMan, name = 'home-page'),
    # path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('showdbsql/', views.showdbsql),
    path('showdboracle/', views.showdbOracle),
    path('rodreport/', views.rodReport),
    path('prpmdump/',views.prpmdump), 
    path('prpmdump/prpmdumpResults',views.dump,name = 'dump-page'),
    path('dQueryReports/',views.dQueryReports),
    path('dQueryReports/queryDumpResults',views.dQuery, name = 'query-page'),
    path('revenues/',views.pageRevenues, name = 'revenues-page'),
    path('exFund/',views.pageExFund, name = 'exFund-page'),
    path('ranking/',views.pageRanking, name = 'ranking-page' ),
    path('research_man/',views.pageResearchMan, name = 'research-man-page' ),
    path('ranking/comparing', views.compare_ranking , name = 'ranking-comparing'),
    path('ranking/prediction', views.pridiction_ranking , name = 'ranking-pridiction'),
    path('revenues/graph/<str:value>/', views.revenues_graph, name = 'revenues-graph-page'),
    path('revenues/show_table', views.revenues_table, name = 'revenues-show-table-page'),
    
    
]