from django.shortcuts import render, redirect
from .models import Category, Post, Comment
from django.db.models import F, Q
from .forms import PostAddForm, LoginForm, RegistrationForm, CommentForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from .serializers import PostSerializer, CategorySerializer
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from django.views.generic import TemplateView


class Index(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'cooking/index.html'
    extra_context = {'title': 'Главная страница'}


class ArticleByCategory(Index):
    def get_queryset(self):
        return Post.objects.filter(category_id=self.kwargs['pk'], is_published=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        category = Category.objects.get(pk=self.kwargs['pk'])
        context['title'] = category.title
        return context


#def post_detail(request, pk):
    #article = Post.objects.get(pk=pk)
    #Post.objects.filter(pk=pk).update(watched=F('watched') + 1)
    #ext_post = Post.objects.all().exclude(pk=pk).order_by('-watched')
    #context = {
        #'title': article.title,
        #'post': article,
        #'ext_posts': ext_post
    #}
    #return render(request, 'cooking/article_detail.html', context)


class PostDetail(DetailView):
    template_name = 'cooking/article_detail.html'

    def get_queryset(self):
        return Post.objects.filter(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        Post.objects.filter(pk=self.kwargs['pk']).update(watched=F('watched') + 1)
        context = super().get_context_data()
        post = Post.objects.get(pk=self.kwargs['pk'])
        posts = Post.objects.all().exclude(pk=self.kwargs['pk']).order_by('-watched')[:5]
        context['title'] = post.title
        context['ext_posts'] = posts
        context['comments'] = Comment.objects.filter(post=post)
        if self.request.user.is_authenticated:
            context['comment_form'] = CommentForm
        return context


class AddPost(CreateView):
    form_class = PostAddForm
    template_name = 'cooking/article_add_form.html'
    extra_context = {'title': 'Добавить статью'}

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdate(UpdateView):
    model = Post
    form_class = PostAddForm
    template_name = 'cooking/article_add_form.html'


class PostDelete(DeleteView):
    model = Post
    success_url = reverse_lazy('index')
    context_object_name = 'post'
    extra_context = {'title': 'Изменить статью'}


class SearchResults(Index):
    def get_queryset(self):
        word = self.request.GET.get('q')
        posts = Post.objects.filter(
            Q(title__icontains=word) | Q(content__icontains=word)
        )
        return posts


def add_comment(request, post_id):
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.post = Post.objects.get(pk=post_id)
        comment.save()
        messages.success(request, 'Ваш комментарий успешно добавлен')
    return redirect('post_detail', post_id)


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вы успешно вошли в аккаунт')
            return redirect('index')
    else:
        form = LoginForm()
    context = {
        'title': 'Авторизация пользователя',
        'form': form
    }
    return render(request, 'cooking/login_form.html', context)


def user_logout(request):
    logout(request)
    return redirect('index')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistrationForm()

    context = {
        'title': 'Регистрация пользователя',
        'form': form
    }
    return render(request, 'cooking/register.html', context)


def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    posts = Post.objects.filter(author=user)
    context = {
        'user': user,
        'posts': posts
    }
    return render(request, 'cooking/profile.html', context)


class UserChangePassword(PasswordChangeView):
    template_name = 'cooking/password_change_form.html'
    success_url = reverse_lazy('index')


class CookingAPI(ListAPIView):
    queryset = Post.objects.filter(is_published=True)
    serializer_class = PostSerializer


class CookingAPIDetail(RetrieveAPIView):
    queryset = Post.objects.filter(is_published=True)
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)


class CookingCategoryAPI(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CookingCategoryAPIDetail(RetrieveAPIView):
    queryset = Post.objects.filter(is_published=True)
    serializer_class = CategorySerializer


class SwaggerApiDoc(TemplateView):
    template_name = 'swagger/swagger_ui.html'
    extra_context = {
        'schema_url': 'openapi-schema'
    }





