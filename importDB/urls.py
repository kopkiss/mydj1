from django.urls import path, include
from . import views  # . คือ อยู่ใน folder เดียวกัน



urlpatterns = [
    path('', views.home, name = 'home-page'),
    # path('', include("django.contrib.auth.urls")),
    # path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('showdbsql/', views.showdbsql),
    path('showdboracle/', views.showdbOracle),
    path('rodreport/', views.rodReport),

    path('dump-data/',views.dump,name = 'dump-page'),
    path('query-data/',views.query ,name = 'query-page'),

    path('research_man/',views.pageResearchMan, name = 'research-man-page' ),

    path('revenues/',views.pageRevenues, name = 'revenues-page'),
    path('revenues/graph/<str:value>/', views.revenues_graph, name = 'revenues-graph-page'),
    path('revenues/show_table', views.revenues_table, name = 'revenues-show-table-page'),
    path('revenues/more-info', views.revenues_more_info, name = 'revenues-more-info'),

    path('ranking/',views.pageRanking, name = 'ranking-page' ),
    path('ranking/comparing', views.ranking_comparison , name = 'ranking-comparing'),
    path('ranking/prediction', views.ranking_prediction , name = 'ranking-pridiction'),
    path('ranking/research_area_moreinfo', views.ranking_research_area_moreinfo , name = 'ranking-area-moreinfo'),
    path('ranking/cite_info/<str:value>/', views.ranking_cite_info , name = 'ranking-cite-info'),

    path('exFund/',views.pageExFund, name = 'exFund-page'),

    path('test-page', views.test_page, name = 'test-page'),
    
    
    
]