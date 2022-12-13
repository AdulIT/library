from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import Http404, HttpResponseForbidden
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.views.generic.edit import FormMixin
import yadisk
from django.core.mail import send_mail, BadHeaderError
from .test import publik
y = yadisk.YaDisk(token="y0_AgAAAAA80jYJAAjfvQAAAADWo2ShwEEwbZRLRSe_ys_viVgBVK-U4Mg")


from django.views.generic import (
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView)

from .forms import (
    ContactForm,
    CommentForm,
    Test,
    BookForms)
from .models import (
    Book,
    BookComment,
    BookRentHistory,
    BookReview,
    Category,
    InBoxMessages,
    BookTest
)
# Create your views here.
import requests
from urllib.parse import urlencode
from pathlib import Path


def tesing_upload(file):
    y.upload(file, f"/{file.name}")
    y.publish(file.name)
    a = y.get_download_link(file.name)
    return a

# def install(url, title):
#     base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
#     public_key = url  
#     final_url = base_url + urlencode(dict(public_key=public_key))
#     response = requests.get(final_url)
#     download_url = response.json()['href']
#     download_response = requests.get(download_url)
#     with open(title+'.pdf', 'wb') as f: 
#         f.write(download_response.content)


class HomeListView(ListView):
    template_name = 'books/home.html'
    model = Book

    def get_queryset(self):
        queryset = super(HomeListView, self).get_queryset()
        return queryset.all().order_by('-id')[:9]

def install_book(request, pk):
    book = get_object_or_404(Book, id=pk)
    return redirect('bookDetail', pk=book.id)



class BooksListView(ListView):
    template_name = 'books/books.html'
    model = Book

    def get_context_data(self, **kwargs):
        context = super(BooksListView, self).get_context_data(**kwargs)
        context.update({
            'top_3_books': Book.objects.order_by('-last_rating')[:3],
            'most_reviews': Book.objects.annotate(reviews_count=Count('reviews')).order_by('-reviews_count')[:3],
            'most_comments': Book.objects.annotate(comments_count=Count('comments')).order_by('-comments_count')[:3],
        })
        return context

    def get_queryset(self):
        return Book.objects.order_by('-id')[:3]


class SearchBookListView(ListView):
    template_name = "books/book_search_result.html"
    model = Book

    def get_queryset(self):
        queryset = super(SearchBookListView, self).get_queryset()
        q = self.request.GET.get("q")
        if q:
            books_by_title = queryset.filter(title__icontains=q)
            books_by_author = queryset.filter(author__icontains=q)
            return books_by_author | books_by_title
        return queryset


class BookDetailView(FormMixin, DetailView):
    model = Book
    form_class = CommentForm

    def get_success_url(self):
        return reverse('bookDetail', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['comments'] = BookComment.objects.filter(
            book=self.object).order_by('-id')
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        b = self.get_object()
        text = form.cleaned_data['text']
        new_comment = BookComment(text=text, book=b, user=self.request.user)
        new_comment.save()
        messages.success(self.request, "Your comment is added, thank you")
        return super().form_valid(form)


@login_required(login_url='login')
def login_to_comment_redirect(request, pk):
    return redirect('bookDetail', id=pk)


@login_required(login_url='login')
def confirm_rent_view(request, pk):
    try:
        b = Book.objects.get(id=pk)
        if b.book_amount <= 0:
            messages.warning(
                request, f'You cant rent this book')
            return redirect('bookDetail', pk=b.id)
    except Book.DoesNotExist:
        raise Http404("We ont have this book")
    return render(request, 'books/confirm_rent_view.html', {'book': b})


@login_required(login_url='login')
def rent_book_view(request, pk):
    try:
        b = Book.objects.get(id=pk)
        if b:
            if b.book_amount > 0:
                b.book_amount -= 1
                b.save()
                log_history = BookRentHistory(user=request.user, book=b)
                log_history.save()
                messages.success(
                    request, f'You rent a book: {b.title}')
            else:
                messages.warning(
                    request, f'You cant rent this book')
                return redirect('bookDetail', pk=b.id)
    except Book.DoesNotExist:
        raise Http404("Book is unavailable")
    return redirect('UserProfile')


@login_required(login_url='login')
def return_book_view(request, pk):
    try:
        b = Book.objects.filter(id=pk)[0]
        if b:
            b.book_amount += 1
            b.save()
            log_history = BookRentHistory.objects.filter(book=b)[0]
            log_history.delete()
            messages.success(
                request, f'You successfully returned a book: {b.title}')
        else:
            messages.warning(
                request, f'Error occurs, sorry')
            return redirect('UserProfile')
    except Book.DoesNotExist:
        raise Http404("Book is unavailable now ")
    return redirect('UserProfile')


class CategoryBookListView(ListView):
    template_name = "books/books_by_category.html"
    model = Book

    def get_queryset(self):
        category = Category.objects.get(id=self.kwargs['pk'])
        return Book.objects.filter(category=category)


@login_required(login_url='login')
def rate_book_view(request, pk, rating):
    try:
        b = Book.objects.get(id=pk)
        if b and not(BookReview.objects.filter(user=request.user).filter(book=b)):
            review = BookReview(book=b, user=request.user, rating=rating)
            review.save()
            b.last_rating = b.calc_rating
            b.save()
            messages.success(
                request, f'You rated a book: {b.title}')

        else:
            messages.warning(
                request, f'You already rated this book')
        return redirect('bookDetail', pk=b.id)
    except Book.DoesNotExist:
        raise Http404("Book is unavailable")
    return redirect('bookDetail', pk=b.id)

def message_show(request):
    messages = InBoxMessages.objects.all()[:7]
    return render(request, 'books/messages.html', {'messages' : messages})

def delete_message(request, pk):
    message = get_object_or_404(InBoxMessages, id=pk)
    message.delete()
    return redirect('messages')

def create_book(request):
    if request.method == 'POST':
        form = BookForms(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.download_url = tesing_upload(form.file)
            form.read_url = publik(form.file)
            form.file.delete()
            form.save()
            return redirect('home')
    else:
        form = BookForms()
    return render(request, 'books/create_book.html', {'form' : form})

def contact_form(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            new_message = InBoxMessages()
            new_message.name = name
            new_message.email = email
            new_message.message = message
            new_message.save()
            messages.success(request, "Your message is sent")
            return redirect('home')
    if request.user.is_authenticated:
        form = ContactForm()
        form.fields['name'].initial = request.user.username
        form.fields['email'].initial = request.user.email
        form.fields['message'].widget.attrs['placeholder'] = 'Write your message here'
        form.fields['name'].label = 'Login'
        form.fields['name'].widget.attrs['readonly'] = True
        form.fields['email'].widget.attrs['readonly'] = True
        return render(request, 'books/contact.html', {'form': form})
    else:
        form = ContactForm()
        form.fields['name'].widget.attrs['placeholder'] = 'Your name'
        form.fields['email'].widget.attrs['placeholder'] = 'Your email'
        form.fields['message'].widget.attrs['placeholder'] = 'Write your message here'
        return render(request, 'books/contact.html', {'form': form})

def test(request):
    if request.method == 'POST':
        form = Test(request.POST, request.FILES)
        if form.is_valid():
            form =  form.save(commit=False)
            tesing_upload(form.file)
            form.name = publik(form.file)
            form.save()
            return redirect('home')
    else:
        form = Test()

    return render(request, 'test.html', {'form' : form})

