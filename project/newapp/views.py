from datetime import datetime

from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.mail import mail_managers, mail_admins
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView, UpdateView, CreateView, DetailView, \
    DeleteView  # импортируем необходимые дженерики

from .filters import NewsFilter  # импортируем написанный нами фильтр (с файла filters.py)
from .forms import NewsForm
from .models import Category, Post
from appointments.models import Appointment


class SubscribeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        appointment = Appointment(
            date=datetime.strptime(request.POST['date'], '%Y-%m-%d'),
            client_name=request.POST['client_name'],
            message=request.POST['message'],
        )
        appointment.save()

        # отправляем письмо всем админам по аналогии с send_mail, только здесь получателя указывать не надо
        mail_admins(
            subject=f'{appointment.client_name} {appointment.date.strftime("%d %m %Y")}',
            message=appointment.message,
        )

        mail_managers(
            subject=f'{appointment.client_name} {appointment.date.strftime("%d %m %Y")}',
            message=appointment.message,
        )

        return redirect('appointments:make_appointment')

    # связывает объекты категории и текущего пользователя
    def get(self, request, category_id, *args, **kwargs):
        print(request.GET)
        user = self.request.user
        category = Category.objects.get(pk=category_id)
        if not category.subscribers.filter(pk=user.pk):
            is_subscriber = False
            category.subscribers.add(user)
        else:
            is_subscriber = True

        context = {
            'categories': Category.objects.all(),
            'category': Category.objects.get(pk=category_id),
            'is_subscriber': is_subscriber
        }
        return render(request, 'subscribe_category.html', context)

    # def post(self, request, *args, **kwargs):
    #     user = self.request.user
    #     print(user)
    #     return render(request, 'subscribe_category.html', context)


class NewsList(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'news_list.html'  # указываем имя шаблона, в котором будет лежать HTML, в котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'posts'  # это имя списка, в котором будут лежать все объекты, его надо указать, чтобы обратиться к самому списку объектов через HTML-шаблон
    ordering = ['-dateCreation']
    paginate_by = 5

    def get_context_data(self, **kwargs):  # забираем отфильтрованные объекты переопределяя метод get_context_data у наследуемого класса
        context = super().get_context_data(**kwargs)
        context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset())  # вписываем наш фильтр в контекст
        return context


class NewsOfCategory(NewsList):
    template_name = 'news_category.html'

    def get_queryset(self):
        return Post.objects.filter(category=self.kwargs['category_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = None
        return context


# дженерик для поиска постов
class NewsSearch(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'news_searsh.html'  # указываем имя шаблона, в котором будет лежать HTML, в котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'posts'  # это имя списка, в котором будут лежать все объекты, его надо указать, чтобы обратиться к самому списку объектов через HTML-шаблон
    ordering = ['-dateCreation']
    paginate_by = 5


    def get_context_data(self, **kwargs):  # забираем отфильтрованные объекты переопределяя метод get_context_data у наследуемого класса
        context = super().get_context_data(**kwargs)
        context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset())  # вписываем наш фильтр в контекст
        return context


# дженерик для получения деталей о товаре
class NewsDetailView(DetailView):
    template_name = 'news_detail.html'
    queryset = Post.objects.all()


# дженерик для создания объекта. Надо указать только имя шаблона и класс формы, который мы написали в прошлом юните. Остальное он сделает за вас
class NewsAddView(CreateView):
    template_name = 'news_add.html'
    form_class = NewsForm
    success_url = '/news/'


# дженерик для редактирования объекта
class NewsEditView(UpdateView):
    template_name = 'news_edit.html'
    form_class = NewsForm
    success_url = '/news/'  # после редактирования нашей статьи нас будет перебрасывать по указанному адресу

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте, который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


# дженерик для удаления новости
class NewsDeleteView(DeleteView):
    template_name = 'news_delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'  # после удаления нашей статьи нас будет перебрасывать по указанному адресу


class AddNews(PermissionRequiredMixin, NewsAddView):
    permission_required = ('newapp.add_post',)


class ChangeNews(PermissionRequiredMixin, NewsEditView):
    permission_required = ('newapp.change_post',)


class DeleteNews(PermissionRequiredMixin, NewsDeleteView):
    permission_required = ('newapp.delete_post',)
