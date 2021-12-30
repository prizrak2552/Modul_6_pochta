from django.urls import path

from .views import NewsList, NewsDetailView, ChangeNews, NewsSearch, AddNews, DeleteNews, NewsOfCategory, SubscribeView

urlpatterns = [
    path('', NewsList.as_view()),
    path('<int:pk>/', NewsDetailView.as_view(), name='news_detail'),  # Ссылка на детали новости
    path('add/', AddNews.as_view(), name='news_add'),  # Ссылка на создание новости
    path('edit/<int:pk>', ChangeNews.as_view(), name='news_edit'),
    path('delete/<int:pk>', DeleteNews.as_view(), name='news_delete'),
    path('search/', NewsSearch.as_view(), name='news_searsh'),
    path('category/<int:category_id>/', NewsOfCategory.as_view(), name='news_category'),
    path('category/<int:category_id>/subscribe/', SubscribeView.as_view(), name='subscribe_category'),
]
