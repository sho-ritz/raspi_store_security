from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from . import models
from linebot import LineBotApi
from linebot.models import TextSendMessage
import os
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from . import serializers
from django.db.models import F

class UserCreateView(generics.CreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class UserListView(generics.ListAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated]

class ItemCreateView(generics.CreateAPIView):
    queryset = models.Item.objects.all()
    serializer_class = serializers.ItemSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class ItemListView(generics.ListAPIView):
    queryset = models.Item.objects.all()
    serializer_class = serializers.ItemSerializer
    permission_classes = [IsAuthenticated]

class PurchaseLogCreateView(generics.CreateAPIView):
    queryset = models.PurchaseLog.objects.all()
    serializer_class = serializers.PurchaseLogSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class PurchaseLogListView(generics.ListAPIView):
    queryset = models.PurchaseLog.objects.all()
    serializer_class = serializers.PurchaseLogSerializer
    permission_classes = [IsAuthenticated]

# LINE Messaging APIのアクセストークン
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_GROUP_ID = os.getenv("LINE_GROUP_ID")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def send_to_line_group(status, user_name="", item_name="", price=0, time="00:00", error_message=""):
    if status == 200:
        message = f"{time}: {user_name}さんが{item_name}を{price}円で購入しました。"
    elif status == 400:
        message = f"{time}: {user_name}さんが購入を試みようとしたところ、{error_message}というエラーが発生しました。"
    else:
        message = f"{time}: {error_message}というエラーが発生しました。"

    # LINEグループにメッセージを送信
    line_bot_api.push_message(
        LINE_GROUP_ID, TextSendMessage(text=message)
    )

def hex_to_shiftjis(hex_string):
    try:
        # 16進数文字列をバイトデータに変換
        byte_data = bytes.fromhex(hex_string)

        # バイトデータをShift_JIS文字列にデコード
        shiftjis_string = byte_data.decode('shift_jis')

        return shiftjis_string
    except ValueError as e:
        return f"変換エラー: {e}"
    except UnicodeDecodeError as e:
        return f"Shift_JISデコードエラー: {e}"


@csrf_exempt
@require_POST
def check_user(request):
    try:
        body = json.loads(request.body)
        student_id = body.get('student_id')
        checked_at = body.get('checked_at')
        
        user_name = hex_to_shiftjis(student_id)
        
        exists = models.User.objects.filter(student_id=student_id).exists()

        if not exists:
            error_message = '学生情報が見つからない'
            send_to_line_group(400, error_message=error_message, user_name=user_name, time=checked_at)
            return JsonResponse({'error': error_message}, status=404)

        return JsonResponse({'exists': exists})
    except json.JSONDecodeError:
        error_message = 'JSONの形式が間違っている'
        send_to_line_group(404, error_message=error_message)
        return JsonResponse({'error': error_message}, status=400)

@csrf_exempt
@require_POST
def create_purchase_log(request):
    try:
        body = json.loads(request.body)
        student_id = body.get('student_id')
        price = body.get('price')
        purchased_at = body.get('purchased_at')
        user = models.User.objects.get(student_id=student_id)
        user_name = user.name

        item = models.Item.objects.filter(price=price, is_sales=True).first()

        if item:  # 結果が存在するか確認
            item_id = item.id
        else:
            error_message = '商品が売り切れ、もしくは未販売'
            send_to_line_group(400, error_message=error_message, user_name=user_name, time=purchased_at)
            return JsonResponse({'error': error_message}, status=404)
        
        if item.stock == 1:
            models.Item.objects.filter(id=item_id).update(is_sales=False)
        
        models.Item.objects.filter(id=item_id).update(stock=F('stock') - 1)
        
        models.PurchaseLog.objects.create(user_id=user, item_id=item)

        send_to_line_group(
            status=200,
            user_name=user_name,
            item_name=item.name,
            price=price,
            time=purchased_at,
            error_message=''
        )

        
        return JsonResponse({'success': True})
    
    except json.JSONDecodeError:
        error_message = 'JSONの形式が間違っている'
        send_to_line_group(404, error_message=error_message)
        return JsonResponse({'error': error_message}, status=400)