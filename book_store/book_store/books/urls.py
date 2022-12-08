from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import (
    BookDetailView,
    BooksListView,
    CategoryBookListView,
    confirm_rent_view,
    contact_form,
    HomeListView,
    login_to_comment_redirect,
    rate_book_view,
    return_book_view,
    rent_book_view,
    SearchBookListView,
    install_book
)


urlpatterns = [
    path('', HomeListView.as_view(), name='home'),
    path('search-book-results/', SearchBookListView.as_view(), name='search'),
    path('books', BooksListView.as_view(), name='books'),
    path('book/<int:pk>',
         BookDetailView.as_view(), name='bookDetail'),
    path('install/<int:pk>', install_book, name='install_book'),
    path('confirm-rent-a-book/<int:pk>',
         confirm_rent_view, name="confirm_rent_view"),
    path('book/rent-book/<int:pk>', rent_book_view, name='rent_book'),
    path('book/return-book/<int:pk>', return_book_view, name='return_book'),
    path('books-by-category/<int:pk>',
         CategoryBookListView.as_view(), name='category_books_view'),
    path('book/<int:pk>/<rating>', rate_book_view, name='rate_book'),
    path('contact', contact_form, name='contact'),
    path('redirect-to-detail/<int:pk>', login_to_comment_redirect,
         name='login_to_comment_redirect')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
