from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from ..models import Product, TemporaryUserID, CartItem, Option, OptionList
from django.core.files.uploadedfile import SimpleUploadedFile
import json
import uuid
class AddProductTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('add_product')  

    def test_add_product_with_valid_data(self):
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(self.url, {
            'name': 'Test Product',
            'price': '10.99',
            'description': 'Test Description',
            'image': image
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True, "data": 'data is stored'})
        self.assertTrue(Product.objects.filter(name='Test Product').exists())


    def test_add_product_with_no_post_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": False, "msg": "No Data was found"})

    def test_add_product_with_exception(self):
        with self.assertRaises(Exception):
            response = self.client.post(self.url, {
                'name': 'Test Product',
                'price': '10.99',
                'description': 'Test Description',
                'image': None  
            })
            self.assertEqual(response.status_code, 200)
            self.assertJSONEqual(response.content, {"success": False, "msg": 'error occured data is not saved'})



class GetAllProductsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.url = reverse('get_all_products')  

    def test_get_all_products_with_no_products(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'data': []})

    def test_get_all_products_with_multiple_products(self):
        image1 = SimpleUploadedFile("test_image1.jpg", b"file_content", content_type="image/jpeg")
        image2 = SimpleUploadedFile("test_image2.jpg", b"file_content", content_type="image/jpeg")
        product1 = Product.objects.create(name='Product 1', price='10.99', description='Description 1', image=image1)
        product2 = Product.objects.create(name='Product 2', price='20.99', description='Description 2', image=image2)
        
        request = self.factory.get(self.url)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'data': [
                {
                    "id": product1.id,
                    "name": product1.name,
                    "price": product1.price,
                    "description": product1.description,
                    "image": request.build_absolute_uri(product1.image.url)
                },
                {
                    "id": product2.id,
                    "name": product2.name,
                    "price": product2.price,
                    "description": product2.description,
                    "image": request.build_absolute_uri(product2.image.url)
                }
            ]
        })








class AddToCartTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('add_to_cart')  
        self.product = Product.objects.create(name='Test Product', price='10.99', description='Test Description')
        self.temporary_user_id = uuid.uuid4()  
        self.temporary_user = TemporaryUserID.objects.create(user_id=self.temporary_user_id)
        self.option_list = OptionList.objects.create(name='Test Option List', selection_type='SINGLE')
        self.option = Option.objects.create(name='Test Option', option_list=self.option_list)

    def test_add_to_cart_with_valid_data(self):
        data = {
            'temporary_user_id': str(self.temporary_user.user_id),
            'product_id': self.product.id,
            'quantity': 2,
            'selected_options': {str(self.option.id): self.option.id}
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"msg": 'Item is being added successfully', "temporary_user_id": str(self.temporary_user.user_id)})
        self.assertTrue(CartItem.objects.filter(temporary_user=self.temporary_user, product=self.product).exists())

    def test_add_to_cart_with_nonexistent_product(self):
        data = {
            'temporary_user_id': str(self.temporary_user.user_id),
            'product_id': 999,  
            'quantity': 2,
            'selected_options': {}
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": False, "msg": 'Item failed to add'})

    def test_add_to_cart_with_nonexistent_temporary_user(self):
        data = {
            'temporary_user_id': str(uuid.uuid4()), 
            'product_id': self.product.id,
            'quantity': 2,
            'selected_options': {}
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": False, "msg": 'Item failed to add'})

    def test_add_to_cart_with_exception(self):
        data = {
            'temporary_user_id': str(self.temporary_user.user_id),
            'product_id': self.product.id,
            'quantity': 'invalid_quantity', 
            'selected_options': {}
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": False, "msg": 'Item failed to add'})


class RemoveFromCartTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('remove_from_cart')  
        self.product = Product.objects.create(name='Test Product', price='10.99', description='Test Description')
        self.temporary_user_id = uuid.uuid4()  
        self.temporary_user = TemporaryUserID.objects.create(user_id=self.temporary_user_id)
        self.option_list = OptionList.objects.create(name='Test Option List', selection_type='SINGLE')
        self.option = Option.objects.create(name='Test Option', option_list=self.option_list)
        self.cart_item = CartItem.objects.create(product=self.product, quantity=1, temporary_user=self.temporary_user)
        self.cart_item.options.add(self.option)

    def test_remove_from_cart_with_valid_data(self):
        data = {
            'temporary_user_id': str(self.temporary_user.user_id),
            'cart_item_id': self.cart_item.id
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Item removed from cart'})
        self.assertFalse(CartItem.objects.filter(pk=self.cart_item.id).exists())

    def test_remove_from_cart_with_nonexistent_cart_item(self):
        data = {
            'temporary_user_id': str(self.temporary_user.user_id),
            'cart_item_id': 999
        }
        response = self.client.post(self.url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'error': 'Item not found in cart'})





class GetCartItemsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.temporary_user_id = uuid.uuid4()  
        self.temporary_user = TemporaryUserID.objects.create(user_id=self.temporary_user_id)
        self.product = Product.objects.create(name='Test Product', price='10.99', description='Test Description', image="/media/images/temp.jpg")
        self.option_list = OptionList.objects.create(name='Test Option List', selection_type='SINGLE')
        self.option = Option.objects.create(name='Test Option', option_list=self.option_list)
        self.cart_item = CartItem.objects.create(product=self.product, quantity=1, temporary_user=self.temporary_user)
        self.cart_item.options.add(self.option)
        self.url = reverse('get_cart_items', args=[self.temporary_user_id])  

    def test_get_cart_items_with_no_cart_items(self):
        # Clear all cart items
        CartItem.objects.all().delete()
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"cart_items": []})





class AddOptionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('add_option')  
        self.option_list = OptionList.objects.create(name='Test Option List', selection_type='SINGLE')


    def test_add_option_with_invalid_option_list_id(self):
        data = {
            'name': 'Test Option',
            'surcharge': '5.00',
            'option_list': 999  
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200) 

    def test_add_option_with_no_post_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": False, "msg": "no data is found"})

    def test_add_option_with_exception(self):
        data = {
            'name': 'Test Option',
            'surcharge': 'invalid_surcharge', 
            'option_list': self.option_list.id
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": False, "msg": "some system error occured"})

