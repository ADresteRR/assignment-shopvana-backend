from django.http import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from .models import Product, Option, OptionList, CartItem, TemporaryUserID
import json

'''
    returns temporary user_id, each session: to bypass the requirement of registration to store cart item details
'''
def generate_temporary_user_id(request):
    temporary_user_id = request.session.get('temporary_user_id')
    if not temporary_user_id:
        temporary_user = TemporaryUserID.objects.create()
        request.session['temporary_user_id'] = str(temporary_user.user_id)
        temporary_user_id = str(temporary_user.user_id)
    return JsonResponse({"temporary_user_id" : temporary_user_id})

'''
    add product to the database
'''
def add_product(request):
    if (request.POST):
        try:
            data = request.POST.dict()
            product_name = data.get("name")
            product_price = data.get("price")
            product_description = data.get("description")
            product_image = request.FILES.get('image')
            print(product_name, product_price, product_description, product_image)
            new_product = Product(name = product_name, price= product_price, description = product_description, image=product_image)
            new_product.save()
            return JsonResponse({
                "success": True,
                "data": 'data is stored'
            })
        except:
            return JsonResponse({
                "success": False,
                "msg": 'error occured data is not saved'
            })
    else:
        return JsonResponse({
            "success" : False,
            "msg": "No Data was found"
        })

'''
    add option list
    - two types SINGLE, and MULTIPLE
'''
def add_option_list(request):
    if (request.POST):
        data = request.POST.dict()
        print(data)
        option_list_name = data.get('name')
        option_list_selection_type = data.get('selection_type')
        new_option_list = OptionList(name = option_list_name , selection_type = option_list_selection_type)
        new_option_list.save()
        return JsonResponse({"success": True, "msg" : "new options list is created " + option_list_name})
    else:
        return JsonResponse({
            "success": False,
            "msg" : "no data found"
        })

'''
    Add Option in Option List
'''
def add_option(request):
    try:
        if (request.POST):
            data = request.POST.dict();
            option_name = data.get('name')
            option_surcharge = data.get('surcharge')
            option_list_id = data.get('option_list')
            option_list = OptionList.objects.get(pk=option_list_id)
            if not option_list:
                return JsonResponse({
                    "success" :False,
                    "msg" : "invalid option list id"
                })
            new_option = Option(name= option_name, surcharge=option_surcharge, option_list=option_list)
            new_option.save()
            return JsonResponse({
                "success": True,
                "data" : data
            })
        
        else:
            return JsonResponse({
                "success": False,
                "msg" : "no data is found"
            })
    except:
        return JsonResponse({
            "success" : False,
            "msg": "some system error occured"
        })
'''
    returns available options 
'''
def get_all_options(request):
    
    option_lists = OptionList.objects.all()
    all_options = []
    for option_list in option_lists:
        print(option_list)
        data = {
            'option_list_id': option_list.id,
            'option_list': option_list.name,
            'options': [],
            'selection_type': option_list.selection_type
        }
        options = Option.objects.filter(option_list_id = option_list.id)
        for option in options:
            option_data = {
                'id': option.id,
                'name': option.name,
                'surcharge': option.surcharge
            }
            data['options'].append(option_data)
        all_options.append(data)
    return JsonResponse({
        'success': True,
        'data' : all_options
    })
    
'''
    returns all available products
'''
        
def get_all_products(request):
    products = Product.objects.all()
    serialized_data = []
    for product in products:
        serialized_data.append({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description,
            "image": request.build_absolute_uri(product.image.url)
        })
    return JsonResponse({'data' : serialized_data})
    
    
'''
    returns cart items, taking temporary_user_id generated for each session
'''
def get_cart_items(request, temporary_user_id):
    print('get_cart_items is being called with user_id:  ', temporary_user_id)
    cart_items = CartItem.objects.filter(temporary_user_id=temporary_user_id)
    serialized_data = []
    for item in cart_items:
        serialized_data.append({
            "id": item.id,
            'product': item.product.name,
            'image': request.build_absolute_uri(item.product.image.url),
            'quantity': item.quantity,
            'price': item.product.price,
            'options': [{"name": option.name, "id" : option.id, "surcharge": option.surcharge} for option in item.options.all()]
        })
    
    return JsonResponse({"cart_items" : serialized_data})

'''
    Add new item in the cart
'''
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        temporary_user_id1 = data.get('temporary_user_id')
        print(data)
        try:
            data.pop('temporary_user_id')
        except:
            print('this is the first time user is here')
        product_id = data.get('product_id')
        quantity = int(data.get('quantity' , 1))
        selected_options = data.get('selected_options', [])
        print(product_id, quantity, selected_options, temporary_user_id1)
        
        product = get_object_or_404(Product, pk=product_id )
        temporary_user_id = get_object_or_404(TemporaryUserID, user_id=temporary_user_id1)
        
        cart_item, created = CartItem.objects.get_or_create(
            temporary_user=temporary_user_id, product=product
        )
        cart_item.quantity = quantity

        
        cart_item.options.clear()
        for key,value in selected_options.items():
            if  type(value) is not list:
                opt = Option.objects.get(pk=value)
                cart_item.options.add(opt)
            else:
                for option in value:
                    opt = Option.objects.get(pk=option)
                    cart_item.options.add(opt)
        
        cart_item.save()
        print(cart_item)
        return JsonResponse({"msg" : 'Item is being added successfully', "temporary_user_id" : temporary_user_id1});
    except:
        return JsonResponse({"success" : False  , "msg": 'Item failed to add'})
    

def remove_from_cart(request):
    data = json.loads(request.body);
    temporary_user_id = data.get('temporary_user_id');
    cart_item_id = data.get('cart_item_id')
    
    try:
        cart_item = CartItem.objects.get(pk=cart_item_id, temporary_user_id=temporary_user_id)
        cart_item.delete()
        return JsonResponse({'message': 'Item removed from cart'})
    except CartItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found in cart'})

