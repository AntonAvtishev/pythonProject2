from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Appointment, Category
from datetime import datetime
from pprint import pprint
from .filters import PostFilter
from .forms import AddPostForm
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.views import View
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core.mail import mail_admins



class PostList(ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'
    ordering = '-time_in'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        print(**kwargs)
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['next_sale'] = None
        print(context)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs


class PostDetail(DetailView):
    model = Post
    template_name = 'new.html'
    context_object_name = 'new'


class PostSearch(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'posts'
    ordering = ['-time_in']


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


class PostCreate(CreateView):
    template_name = 'post_create.html'
    form_class = AddPostForm
    model = Post

    def form_valid(self, form):
        post = form.save(commit=False)
        print(post)
        if 'news' in self.request.path:
            post_type = 'NE'
        elif 'articles' in self.request.path:
            post_type = 'AR'
        post.type = post_type
        post.save()
        return super().form_valid(form)


class PostUpdate(UpdateView):
    template_name = 'post_create.html'
    form_class = AddPostForm
    model = Post

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class PostDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    queryset = Post.objects.all()
    success_url = reverse_lazy('news')


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'news/category_detail.html'
    context_object_name = 'category_detail'


@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)

    if request.user in category.subscribers.all():
        category.subscribers.remove(user)
        message = 'Вы успешно отписались на рассылку новостей категории'

    else:
        category.subscribers.add(user)
        message = 'Вы успешно подписались на рассылку новостей категории'
    return render(request, 'news/subscribe.html', {'category': category, 'message': message})


class AppointmentView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'make_appointment.html', {})


    def post(self, request, *args, **kwargs):
        appointment = Appointment(
            date=datetime.strptime(request.POST['date'], '%Y-%m-%d'),
            client_name=request.POST['client_name'],
            message=request.POST['message'],
        )
        appointment.save()

        html_content = render_to_string(
            'category/appointment_created.html',
            {
                'category': appointment,
            }
        )

        msg = EmailMultiAlternatives(
            subject=f'{appointment.client_name} {appointment.date.strftime("%Y-%M-%d")}',
            body=appointment.message,
            from_email='Scotcher2@yandex.ru',
            to=['avtishev@list.ru']
        )
        msg.attach_alternative(html_content, "category/appointment_created.html")  # добавляем html

        mail_admins(
            subject=f'{appointment.client_name} {appointment.date.strftime("%d %m %Y")}',
            message=appointment.message,
        )

        msg.send()  # отсылаем

        return redirect('category:make_appointment')