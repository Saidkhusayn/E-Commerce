from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("categoryBased", views.categoryBased, name="categoryBased"),
    path("listing/<slug:slug>", views.listing, name="listing"),
    path("addWatchlist/<slug:slug>", views.addWatchlist, name="addWatchlist"),
    path("removeWatchlist/<slug:slug>", views.removeWatchlist, name="removeWatchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("comment/<slug:slug>", views.comment, name="comment"),
    path("bid/<slug:slug>", views.bid, name="bid"),
    path("closeAuction/<slug:slug>", views.closeAuction, name="closeAuction"),
]
