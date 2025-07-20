import os
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen
from django.core.files.storage import default_storage
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .llama_utils import llama_scout_poem, llama_maverick_describe
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from services.ebay_service import EbayService
from .models import EbayItem, SearchHistory, UserFavorite
import json
from django.utils import timezone


# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')

def welcome(request):
    return render(request, 'welcome.html')


@login_required
def product(request):
    return render(request, 'product.html')

@login_required
def camera(request):
    if request.method == 'POST':
        image_path = request.POST["src"]
        image = NamedTemporaryFile()
        urlopen(image_path).read()
        image.write(urlopen(image_path).read())
        image.flush()
        image = File(image)
        name = str(image.name).split('\\')[-1]
        name += '.jpg'  
        image.name = name
        with open('image.txt', 'w+') as file:
            file.write(str(name))
        default_storage.save('C:/Users/George Brian/repos/SNAPSHOP/snapapp/static/images/a.jpg', ContentFile(urlopen(image_path).read()))
        return HttpResponse('Done!')
    return render(request, 'index.html')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def scout_poem(request):
    prompt = request.data.get('prompt', 'Write a short poem about AI.')
    poem = llama_scout_poem(prompt)
    return Response({"poem": poem})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def maverick_describe(request):
    image_url = request.data.get('image_url')
    if not image_url:
        return Response({"detail": "image_url is required"}, status=400)
    desc = llama_maverick_describe(image_url)
    return Response({"description": desc})

@login_required
def product_search(request):
    """Main product search view - requires authentication"""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    page = request.GET.get('page', 1)
    
    items = []
    total_items = 0
    
    if query:
        try:
            ebay_service = EbayService()
            
            
            filters = {}
            if category:
                filters['category_ids'] = category
                
            
            results = ebay_service.search_items(
                query=query, 
                limit=50, 
                filters=filters
            )
            
            
            if 'itemSummaries' in results:
                items = process_search_results(results['itemSummaries'])
                total_items = results.get('total', 0)
                
            
            save_search_history(request.user, query, category, len(items))
                
        except Exception as e:
            messages.error(request, f"Search error: {str(e)}")
    
    
    paginator = Paginator(items, 12)  
    page_obj = paginator.get_page(page)
    
    context = {
        'items': page_obj,
        'query': query,
        'category': category,
        'total_items': total_items,
        'categories': get_categories(),
        'user': request.user
    }
    
    return render(request, 'search.html', context)

def process_search_results(item_summaries):
    
    processed_items = []
    
    for item in item_summaries:
        processed_item = {
            'ebay_id': item.get('itemId'),
            'title': item.get('title'),
            'price': item.get('price', {}).get('value', 0),
            'currency': item.get('price', {}).get('currency', 'USD'),
            'condition': item.get('condition', 'Unknown'),
            'image_url': item.get('image', {}).get('imageUrl', ''),
            'item_url': item.get('itemWebUrl', ''),
            'seller_username': item.get('seller', {}).get('username', ''),
            'location': item.get('itemLocation', {}).get('country', ''),
            'shipping_cost': item.get('shippingOptions', [{}])[0].get('shippingCost', {}).get('value', 0) if item.get('shippingOptions') else 0
        }
        processed_items.append(processed_item)
        
        
        cache_item_in_db(processed_item)
    
    return processed_items

def cache_item_in_db(item_data):
    
    try:
        EbayItem.objects.update_or_create(
            ebay_id=item_data['ebay_id'],
            defaults=item_data
        )
    except Exception as e:
        print(f"Error caching item: {e}")

def save_search_history(user, query, category, results_count):

    try:
        SearchHistory.objects.create(
            user=user,
            query=query,
            category=category,
            results_count=results_count,
            timestamp=timezone.now()
        )
    except Exception as e:
        print(f"Error saving search history: {e}")

def get_categories():
    
    return [
        {'id': '58058', 'name': 'Electronics'},
        {'id': '11450', 'name': 'Clothing'},
        {'id': '6028', 'name': 'Home & Garden'},
        {'id': '2984', 'name': 'Sports'},
        {'id': '267', 'name': 'Books'},
        {'id': '550', 'name': 'Art'},
    ]

@login_required
def item_detail(request, item_id):
    
    try:
        ebay_service = EbayService()
        item_details = ebay_service.get_item_details(item_id)
        
        
        is_favorited = UserFavorite.objects.filter(
            user=request.user, 
            ebay_id=item_id
        ).exists()
        
        context = {
            'item': item_details,
            'is_favorited': is_favorited,
            'user': request.user
        }
        
        return render(request, 'search.html', context)
        
    except Exception as e:
        messages.error(request, f"Error loading item: {str(e)}")
        return redirect('product_search')

@login_required
def toggle_favorite(request, item_id):
    """Toggle item favorite status"""
    if request.method == 'POST':
        try:
            favorite, created = UserFavorite.objects.get_or_create(
                user=request.user,
                ebay_id=item_id
            )
            
            if not created:
                favorite.delete()
                favorited = False
            else:
                favorited = True
                
            return JsonResponse({
                'favorited': favorited,
                'message': 'Added to favorites' if favorited else 'Removed from favorites'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def user_favorites(request):
    
    favorites = UserFavorite.objects.filter(user=request.user).order_by('-created_at')
    
    
    paginator = Paginator(favorites, 12)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    context = {
        'favorites': page_obj,
        'user': request.user
    }
    
    return render(request, 'search.html', context)

@login_required
def search_history(request):
    
    history = SearchHistory.objects.filter(user=request.user).order_by('-timestamp')
    
   
    paginator = Paginator(history, 20)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    context = {
        'history': page_obj,
        'user': request.user
    }
    
    return render(request, 'search.html', context)

@login_required
def user_dashboard(request):
    
    recent_searches = SearchHistory.objects.filter(user=request.user).order_by('-timestamp')[:5]
    recent_favorites = UserFavorite.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'user': request.user,
        'recent_searches': recent_searches,
        'recent_favorites': recent_favorites,
        'total_searches': SearchHistory.objects.filter(user=request.user).count(),
        'total_favorites': UserFavorite.objects.filter(user=request.user).count()
    }
    
    return render(request, 'search.html', context)