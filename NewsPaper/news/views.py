from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin  # модуль Д5, чтоб ограничить права доступа
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.views.generic import ListView, UpdateView, CreateView, DetailView, DeleteView
from django.core.cache import cache
from .models import Post, Category
from .filters import PostFilter
from datetime import datetime
from .forms import PostForm

from django.http import HttpResponse
from django.views import View
from .tasks import hello, send_mail_for_sub_test


class PostList(ListView):
    model = Post
    template_name = 'flatpages/news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-dateCreation')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['filter'] = PostFilter(
            self.request.GET, queryset=self.get_queryset())
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'flatpages/post.html'
    queryset = Post.objects.all()

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'product-{self.kwargs["pk"]}', None)
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'product-{self.kwargs["pk"]}', obj)

        return obj


class PostSearch(PostList):
    template_name = 'flatpages/search.html'
    context_object_name = 'search'
    filter_class = PostList

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # вписываем наш фильтр в контекст странички
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


class PostCreate(PermissionRequiredMixin, CreateView):
    template_name = 'flatpages/add.html'
    form_class = PostForm
    permission_required = ('news.add_post',)


class PostUpdate(PermissionRequiredMixin, UpdateView):
    template_name = 'flatpages/edit.html'
    form_class = PostForm
    permission_required = ('news.change_post',)

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте, который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


# дженерик для удаления товара
class PostDelete(DeleteView):
    template_name = 'flatpages/delete.html'
    queryset = Post.objects.all()
    success_url = '/news/delete/'


@login_required
def add_subscribe(request, **kwargs):
    pk = request.GET.get('pk', )
    print('Пользователь', request.user, 'добавлен в подписчики категории:', Category.objects.get(pk=pk))
    Category.objects.get(pk=pk).subscribers.add(request.user)
    return redirect('/news/')


@login_required
def del_subscribe(request, **kwargs):
    pk = request.GET.get('pk', )
    print('Пользователь', request.user, 'удален из подписчиков категории:', Category.objects.get(pk=pk))
    Category.objects.get(pk=pk).subscribers.remove(request.user)
    return redirect('/news/')


class AddNews(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add',)


class ChangeNews(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.edit',)


class DeleteNews(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete',)


class IndexView(View):
    def get(self, request):
        # printer.apply_async([10], countdown=10)
        # hello.delay()
        send_mail_for_sub_test.delay()
        return HttpResponse('Hello!')
