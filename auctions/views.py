from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.contrib import messages

from .models import *


def index(request):
    activeListings = Listing.objects.filter(isActive=True)
    dropdown = Category.objects.all()
    return render(request, "auctions/index.html", {
        "activeListings": activeListings,
        "options": dropdown
    })

def categoryBased(request):
    if request.method=="POST":
        category_name = request.POST['category']
        category = Category.objects.get(categoryName=category_name)
        dropdown = Category.objects.all()
        if category_name == "All Listings":
            activeListings = Listing.objects.filter(isActive=True)
            return render(request, "auctions/index.html", {
                "activeListings": activeListings,
                "options": dropdown
            })
        else:
            activeListings = Listing.objects.filter(isActive=True, category=category)
            return render(request, "auctions/index.html", {
                "activeListings": activeListings,
                "options": dropdown
            })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
@login_required(login_url='login')
def create(request):
    dropdown = Category.objects.all()
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        price = request.POST['price']
        category_name = request.POST['category']
        url = request.POST['url']

        category = get_object_or_404(Category, categoryName=category_name)
        slug = slugify(title)


        new_listing = Listing(
            title=title,
            description=description,
            price=price,
            url=url,
            owner=request.user,
            category = category,
            slug=slug,
            )
        
        new_listing.save()
        return redirect('index')
    
    return render(request, "auctions/create.html", {
        "options": dropdown
    })

def listing(request, slug):
    listingData = get_object_or_404(Listing, slug=slug)
    inWatchlist = request.user in listingData.watchlist.all()
    isOwner = listingData.owner.username == request.user.username
    comments = listingData.comments.all().order_by('-created_at')
    bidsInListing = listingData.bids.count()
    highest_bid = listingData.bids.order_by('-amount').first().amount if listingData.bids.exists() else listingData.price

    highest_bid_object = listingData.bids.order_by('-amount').first()

    context = {
        'listing': listingData,
        'inWatchlist': inWatchlist,
        'comments': comments,
        'bidsInListing': bidsInListing,
        'lastBid': highest_bid,
        'isOwner': isOwner,
        "highest_bid_object": highest_bid_object
    }
    
    return render(request, "auctions/listing.html", context)

def addWatchlist(request, slug):
    listingInWatchlist = Listing.objects.get(slug=slug)
    currentUser = request.user
    listingInWatchlist.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(slug, )))

def removeWatchlist(request, slug):
    listingInWatchlist = Listing.objects.get(slug=slug)
    currentUser = request.user
    listingInWatchlist.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(slug, )))
    

def watchlist(request):
    currentUser = request.user
    listings = currentUser.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

def comment(request, slug):
    if request.method == "POST":
        comment = request.POST['comment']

        listing_name = Listing.objects.get(slug=slug)

        new_comment = Comment(
            listing=listing_name,
            user=request.user,
            content=comment,
        )

        new_comment.save()
        return HttpResponseRedirect(reverse("listing", args=(slug, )))
    
def bid(request, slug):
    listing_name = get_object_or_404(Listing, slug=slug)
    highest_bid = listing_name.bids.order_by('-amount').first().amount if listing_name.bids.exists() else listing_name.price
    highest_bid_object = listing_name.bids.order_by('-amount').first()
    if request.method == "POST":
        bid_amount = float(request.POST['bid'])
        
        if listing_name.bids.count() == 0:
            if bid_amount < listing_name.price:
                return render(request, "auctions/listing.html", {
                    "listing": listing_name,
                    "inWatchlist": request.user in listing_name.watchlist.all(),
                    "comments": listing_name.comments.all().order_by('-created_at'),
                    "bidsInListing": listing_name.bids.count(),
                    "message": "Your bid must be at least as large as the starting bid.",
                    "update": False, 
                    'lastBid': highest_bid,
                    "highest_bid_object": highest_bid_object,
                })
        else:
            highest_bid = listing_name.bids.order_by('-amount').first().amount
            if bid_amount <= highest_bid:
                return render(request, "auctions/listing.html", {
                    "listing": listing_name,
                    "inWatchlist": request.user in listing_name.watchlist.all(),
                    "comments": listing_name.comments.all().order_by('-created_at'),
                    "bidsInListing": listing_name.bids.count(),
                    "message": "Your bid must be greater than any other bids.",
                    "update": False, 
                    'lastBid': highest_bid, 
                    "highest_bid_object": highest_bid_object,
                })

        # If bid is valid, save it
        new_bid = Bid(
            listing=listing_name,
            user=request.user,
            amount=bid_amount,
        )
        new_bid.save()
        return redirect('listing', slug=slug)

    return redirect('listing', slug=slug)

def closeAuction(request, slug):
    listing_name = get_object_or_404(Listing, slug=slug)
    if request.method == "POST":
        listing_name.isActive = False
        listing_name.save()
        messages.success(request, 'Congratulations! You closed the auction')
        return redirect('listing', slug=slug)
    