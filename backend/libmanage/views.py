import json
import base64
from datetime import datetime, timedelta 

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import Http404 # 新增 Http404 引入，用於 book_detail_api

# 圖像處理和條碼辨識庫
import cv2
import numpy as np
from pyzbar.pyzbar import decode as pyzbar_decode, ZBarSymbol

from .models import Book, User, BorrowRecord 

# 錯誤處理輔助函數
def error_response(message, status=400):
    return JsonResponse({'message': message}, status=status)

# API Views for React Frontend
@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    try:
        data = json.loads(request.body)
        account = data.get('username')
        password = data.get('password')
    except json.JSONDecodeError:
        return error_response('Invalid JSON', status=400)

    if not account or not password:
        return error_response('請輸入帳號與密碼', status=400)

    user = User.objects.filter(username=account).first()

    if not user or not check_password(password, user.password):
        return error_response('帳號或密碼錯誤', status=401)
    
    return JsonResponse({
        'message': f"歡迎：{user.username}",
        'user_id': user.id,
        'username': user.username
    }, status=200)

@csrf_exempt
@require_http_methods(["POST"])
def register_api(request):
    try:
        data = json.loads(request.body)
        account = data.get('username')
        password = data.get('password')
    except json.JSONDecodeError:
        return error_response('Invalid JSON', status=400)

    if not account or not password:
        return error_response('請輸入帳號與密碼', status=400)

    if User.objects.filter(username=account).exists():
        return error_response('帳號已存在', status=409)

    try:
        new_user = User.objects.create(
            username=account,
            password=make_password(password)
        )
        return JsonResponse({
            'message': '註冊成功', 
            'user_id': new_user.id, 
            'username': new_user.username}, status=201)
    except Exception as e:
        return error_response(f'註冊失敗：{str(e)}', status=500)

@csrf_exempt
@require_http_methods(["POST"])
def logout_api(request):
    return JsonResponse({'message': '已登出'}, status=200)

@csrf_exempt
@require_http_methods(["POST"]) # 這裡可以使用 PUT
def update_profile_api(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        new_password = data.get('new_password')
    except json.JSONDecodeError:
        return error_response('Invalid JSON', status=400)

    if not user_id:
        return error_response('User ID is required', status=401)
    
    if not new_password:
        return error_response('新密碼不可為空', status=400)

    try:
        user = get_object_or_404(User, id=user_id)
        
        user.password = make_password(new_password)
        user.save()

        return JsonResponse({'message': '密碼更新成功！'}, status=200)
    except User.DoesNotExist:
        return error_response('用戶不存在', status=404)
    except Exception as e:
        return error_response(f'更新個人資料失敗：{str(e)}', status=500)

@require_http_methods(["GET"]) # 使用 GET 請求 
def user_home_api(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return error_response('User ID is required', status=401)
    
    try:
        user = get_object_or_404(User, id=user_id)
    except User.DoesNotExist:
        return error_response('User not found', status=404)
    
    current_date = timezone.now().date() # 獲取當前日期

    borrowed_books_records = BorrowRecord.objects.filter(user=user, returned=False).select_related('book')
    borrowed_books_data = [{
        'id': record.id,
        'book_title': record.book.title,
        'borrow_date': record.borrow_date.isoformat(),
        'due_date': record.due_date.isoformat(),
        'is_overdue': current_date > record.due_date
    } for record in borrowed_books_records]

    all_records_queryset = BorrowRecord.objects.filter(user=user).order_by('-borrow_date').select_related('book')
    all_records_data = []
    for record in all_records_queryset:
        is_overdue = False
        if record.returned:
            if record.return_date and record.return_date > record.due_date: # 確保日期比較
                is_overdue = True
        else:
            if current_date > record.due_date:
                is_overdue = True

        all_records_data.append({
            'id': record.id,
            'book_title': record.book.title,
            'borrow_date': record.borrow_date.isoformat(),
            'due_date': record.due_date.isoformat(),
            'return_date': record.return_date.isoformat() if record.return_date else None,
            'returned': record.returned,
            'is_overdue': is_overdue
        })
    
    return JsonResponse({
        'username': user.username,
        'borrowed_books': borrowed_books_data,
        'all_records': all_records_data,
        'now': timezone.now().isoformat()
    }, status=200)

@require_http_methods(["GET"]) # 使用 GET 請求 
def book_list_api(request):
    # 從資料庫中獲取所有書籍的資訊
    books = Book.objects.all().values('id', 'title', 'author', 'isbn', 'is_borrowed', 'category', 'status')
    return JsonResponse({'books': list(books)}, status=200)

@csrf_exempt
@require_http_methods(["POST"])
def book_create_api(request):
    try:
        data = json.loads(request.body)
        title = data.get('title')
        author = data.get('author')
        isbn = data.get('isbn')
        category = data.get('category', 'OTHER') 
        status = data.get('status', 'AVAILABLE') 
    except json.JSONDecodeError:
        return error_response('Invalid JSON', status=400)

    if not title or not author or not isbn:
        return error_response('請填寫所有必填欄位 (書名、作者、ISBN)', status=400)
    
    # 檢查 ISBN 是否重複
    if Book.objects.filter(isbn=isbn).exists():
        return error_response('ISBN 已存在，請確認ISBN 是否有誤。', status=409)

    try:
        new_book = Book.objects.create(title=title, author=author, isbn=isbn, category=category, status=status)
        return JsonResponse({'message': '書籍新增成功', 'book_id': new_book.id}, status=201)
    except Exception as e:
        return error_response(f'新增失敗：{str(e)}', status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def book_delete_api(request, book_id):
    try:
        book = get_object_or_404(Book, id=book_id)
        # 檢查書籍是否被借出或有其他狀態，如果被借出則不能刪除
        if book.is_borrowed:
            return error_response('此書已被借出，無法刪除。', status=409)
        # 根據 status 判斷是否可刪除
        if book.status == 'DAMAGED' or book.status == 'LOST':
             # 允許刪除損壞或遺失的書籍
             pass
        elif book.status != 'AVAILABLE':
            return error_response(f'此書狀態為 "{book.get_status_display()}"，無法刪除。', status=409)
            
        book.delete()
        return JsonResponse({'message': '書籍已成功刪除'}, status=200)
    except Exception as e:
        return error_response(f'刪除失敗：{str(e)}', status=500)

@csrf_exempt
@require_http_methods(["POST"])
def borrow_book_api(request, book_id):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
    except json.JSONDecodeError:
        return error_response('Invalid JSON', status=400)

    if not user_id:
        return error_response('User ID is required', status=401)
    
    user = get_object_or_404(User, id=user_id)
    book = get_object_or_404(Book, id=book_id)

    if book.is_borrowed:
        return error_response('此書已被借出', status=409)
    
    # 檢查書籍狀態是否為 AVAILABLE
    if book.status != 'AVAILABLE':
        return error_response(f'此書狀態為 "{book.get_status_display()}"，無法借閱。', status=409)
    
    if BorrowRecord.objects.filter(user=user, book=book, returned=False).exists():
        return error_response('您已借閱此書且尚未歸還', status=409)

    due_date = timezone.now() + timedelta(days=60) 
    due_date = due_date.date()

    BorrowRecord.objects.create(
        user=user, 
        book=book, 
        borrow_date=timezone.now(),
        due_date=due_date
    )
    
    book.is_borrowed = True
    book.save()
    
    return JsonResponse({
        'message': f"{book.title} 借閱成功，歸還日期：{due_date.strftime('%Y-%m-%d')}"
    }, status=200)

@csrf_exempt
@require_http_methods(["POST"])
def return_book_api(request, record_id):
    try:
        record = get_object_or_404(BorrowRecord, id=record_id)
        if record.returned:
            return error_response('此書已歸還', status=409)

        record.returned = True
        record.return_date = timezone.now()
        record.book.is_borrowed = False
        
        # 歸還後將書籍狀態設為 AVAILABLE，除非原本是損壞或遺失
        if record.book.status not in ['DAMAGED', 'LOST']: # 不修改已損壞或遺失的狀態
             record.book.status = 'AVAILABLE'
        
        record.book.save()
        record.save()
        
        return JsonResponse({'message': f"{record.book.title} 已成功歸還"}, status=200)
    except Exception as e:
        return error_response(f'歸還失敗：{str(e)}', status=500)

@csrf_exempt
@require_http_methods(["PUT", "POST"])
def update_book_api(request, book_id):
    """
    更新單本書籍的所有資訊（書名、作者、ISBN、分類、狀態）。
    """
    try:
        book = get_object_or_404(Book, id=book_id)
        data = json.loads(request.body)

        title = data.get('title')
        author = data.get('author')
        isbn = data.get('isbn')
        category = data.get('category')
        status = data.get('status')

        if not all([title, author, isbn, category, status]): # 檢查所有必填欄位
            return error_response('書名、作者、ISBN、分類、狀態均為必填', status=400)

        # 檢查新的 ISBN 是否與其他書籍重複（除了當前正在編輯的書籍）
        if Book.objects.filter(isbn=isbn).exclude(id=book_id).exists():
            return error_response('此 ISBN 已被其他書籍使用，請輸入獨特的 ISBN', status=409)

        book.title = title
        book.author = author
        book.isbn = isbn
        book.category = category
        book.status = status
        book.save()

        return JsonResponse({'message': f'書籍 "{book.title}" 更新成功！'}, status=200)

    except Book.DoesNotExist:
        return error_response('書籍不存在', status=404)
    except json.JSONDecodeError:
        return error_response('無效的 JSON 數據', status=400)
    except Exception as e:
        return error_response(f'更新書籍過程中發生錯誤：{str(e)}', status=500)

@csrf_exempt
@require_http_methods(["PUT"]) # 專門用於更新書籍狀態的API
def update_book_status_api(request, book_id):
    """
    僅更新單本書籍的狀態。使用 PUT 請求。
    """
    try:
        book = get_object_or_404(Book, id=book_id)
        data = json.loads(request.body)
        new_status = data.get('status')

        if not new_status:
            return error_response('請提供要更新的書籍狀態', status=400)
        
        # 驗證狀態是否在 STATUS_CHOICES 中
        valid_statuses = [choice[0] for choice in Book.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return error_response('無效的書籍狀態', status=400)

        book.status = new_status
        book.save()

        return JsonResponse({'message': f'書籍 "{book.title}" 狀態已更新為 "{book.get_status_display()}"'}, status=200)

    except Book.DoesNotExist:
        return error_response('書籍不存在', status=404)
    except json.JSONDecodeError:
        return error_response('無效的 JSON 數據', status=400)
    except Exception as e:
        return error_response(f'更新書籍狀態時發生錯誤：{str(e)}', status=500)


@require_http_methods(["GET"]) # 獲取單本書籍資訊的API
def book_detail_api(request, identifier): # 修改：參數從 book_id 改為 identifier
    try:
        # 嘗試將 identifier 轉換為整數，如果成功則按 ID 查詢
        try:
            book_id = int(identifier)
            book = get_object_or_404(Book, pk=book_id)
        except ValueError:
            # 如果不是整數，則按 ISBN 查詢
            book = get_object_or_404(Book, isbn=identifier)

        book_data = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'is_borrowed': book.is_borrowed,
            'category': book.category,
            'status': book.status,
            # 移除以下行，因為您的模型中可能不存在這些屬性
            # 'publisher': book.publisher, 
            # 'publication_year': book.publication_year,
            # 'description': book.description,
        }
        return JsonResponse({'book': book_data}, status=200)
    except Book.DoesNotExist: # 處理書籍不存在的情況
        return error_response('書籍不存在', status=404)
    except Exception as e:
        return error_response(f'獲取書籍詳細信息失敗：{str(e)}', status=500)

@csrf_exempt
@require_http_methods(["POST"])
def return_book_by_book_and_user_api(request): # 新增：根據書籍ID和用戶ID歸還
    try:
        data = json.loads(request.body)
        book_id = data.get('book_id')
        user_id = data.get('user_id')

        if not book_id or not user_id:
            return error_response('缺少書籍ID或用戶ID', status=400)

        # 找到最近一條該用戶借閱該書籍且未歸還的記錄
        borrow_record = BorrowRecord.objects.filter(
            book__id=book_id,
            user__id=user_id,
            returned=False
        ).order_by('-borrow_date').first() # 獲取最新一條未歸還記錄

        if not borrow_record:
            return error_response('未找到該用戶借閱此書籍的未歸還記錄', status=404)

        borrow_record.return_date = timezone.now()
        borrow_record.returned = True
        borrow_record.save()

        # 更新書籍狀態為 AVAILABLE，除非原本是損壞或遺失
        book = borrow_record.book
        if book.status not in ['DAMAGED', 'LOST']:
             book.status = 'AVAILABLE'
        book.save()

        return JsonResponse({'message': '書籍歸還成功'}, status=200)

    except json.JSONDecodeError:
        return error_response('無效的 JSON 格式', status=400)
    except Exception as e:
        return error_response(f'歸還書籍失敗：{str(e)}', status=500)

@require_http_methods(["GET"])
def get_book_by_isbn(request, isbn):
    try:
        book = Book.objects.get(isbn=isbn)
        return JsonResponse({'book': {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'category': book.category,
            'status': book.status,
            # ...其他欄位...
        }})
    except Book.DoesNotExist:
        return JsonResponse({'message': '查無此書籍'}, status=404)
    except Exception as e:
        return JsonResponse({'message': f'伺服器錯誤: {str(e)}'}, status=500)
# @csrf_exempt
# @require_http_methods(["POST"]) 
# def scan_code_api(request):
#     try:
#         data = json.loads(request.body)
#         image_b64 = data.get('image')
        
#         if not image_b64:
#             return error_response('未提供圖像數據', status=400)

#         img_bytes = base64.b64decode(image_b64)
#         np_arr = np.frombuffer(img_bytes, np.uint8)
#         img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

#         if img is None:
#             return error_response('無法解碼圖像', status=400)

#         gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#         decoded_objects = pyzbar_decode(gray_img)

#         if decoded_objects:
#             decoded_text = decoded_objects[0].data.decode('utf-8')
#             # 提取邊界框資訊
#             rect = decoded_objects[0].rect
#             bounding_box = {
#                 'x': rect.left,
#                 'y': rect.top,
#                 'width': rect.width,
#                 'height': rect.height
#             }
#             return JsonResponse({'message': '成功辨識', 'decoded_text': decoded_text, 'bounding_box': bounding_box}, status=200)
#         else:
#             return JsonResponse({'message': '未找到條碼或QR碼'}, status=200)
#     except json.JSONDecodeError:
#         return error_response('無效的 JSON 數據', status=400)
#     except Exception as e:
#         return error_response(f'掃描過程中發生錯誤：{str(e)}', status=500)
