from django.shortcuts import render, reverse, redirect
from django.views.generic import ListView, DeleteView, CreateView, DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.mail import send_mail
from .models import Post, PostCategory, Response
from .forms import PostForm
from .filters import ResponseFilter


class PostList(ListView):
    model = Post
    template_name = "posts.html"
    context_object_name = "posts"
    queryset = Post.objects.all()
    paginate_by = 10
    form_class = PostForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'post_create.html'
    form_class = PostForm
    permission_required = ('posts.add_post',)


class PostDetail(DetailView):
    model = Post
    template_name = "post.html"
    context_object_name = "post"
    queryset = Post.objects.all()

    def post(self, request, *args, **kwargs):
        post_obj = Post.objects.get(id=self.kwargs["pk"])
        response = Response(user=request.user, post=post_obj, text=request.POST.get('text-response'), accepted=False)
        response.save()

        return super().get(request, *args, **kwargs)


class ResponsesList(ListView):
    model = Post
    template_name = "responses.html"
    context_object_name = "responses"
    queryset = Response.objects.all()
    paginate_by = 10
    form_class = PostForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = ResponseFilter(self.request.GET, queryset=self.get_queryset())
        context['form'] = PostForm()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

        return super().get(request, *args, **kwargs)


def RespopnseDelete(request, pk):
    response = Response.objects.get(id=pk).delete()

    return redirect('/posts/responses')


def RespopnseAccept(request, pk):
    response = Response.objects.get(id=pk)
    response.accepted = True
    response.save()

    return redirect('/posts/responses')