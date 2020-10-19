from django.urls import path, include
from . import views  # . คือ อยู่ใน folder เดียวกัน



urlpatterns = [
    path('', views.pageResearchMan, name = 'home-page'),
    # path('', include("django.contrib.auth.urls")),
    # path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('showdbsql/', views.showdbsql),
    path('showdboracle/', views.showdbOracle),
    path('rodreport/', views.rodReport),

    path('dump-data/',views.dump,name = 'dump-page'),
    path('query-data/',views.query ,name = 'query-page'),
    path('revenues/',views.pageRevenues, name = 'revenues-page'),
    path('exFund/',views.pageExFund, name = 'exFund-page'),
    path('ranking/',views.pageRanking, name = 'ranking-page' ),
    path('research_man/',views.pageResearchMan, name = 'research-man-page' ),
    path('ranking/comparing', views.compare_ranking , name = 'ranking-comparing'),
    path('ranking/prediction', views.pridiction_ranking , name = 'ranking-pridiction'),
    path('revenues/graph/<str:value>/', views.revenues_graph, name = 'revenues-graph-page'),
    path('revenues/show_table', views.revenues_table, name = 'revenues-show-table-page'),
    path('revenues/more-info', views.revenues_more_info, name = 'revenues-more-info'),
    
    
    
]