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
    serializer_class = serializers.ItemsSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class ItemListView(generics.ListAPIView):
    queryset = models.Item.objects.all()
    serializer_class = serializers.ItemsSerializer
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

def send_to_line_group(user_name, item_name, price, purchased_at):
    message = f"{purchased_at}: {user_name}さんが{item_name}を{price}円で購入しました。"

    # LINEグループにメッセージを送信
    line_bot_api.push_message(
        LINE_GROUP_ID, TextSendMessage(text=message)
    )

    return JsonResponse({"status": "Message sent to LINE group"}, status=200)


@csrf_exempt
@require_POST
def check_user(request):
    try:
        body = json.loads(request.body)
        student_id = body.get('student_id')

        if not student_id:
            return JsonResponse({'error': 'student_id is required'}, status=400)
        
        exists = models.User.objects.filter(student_id=student_id).exists()

        return JsonResponse({'exists': exists})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

@csrf_exempt
@require_POST
def create_purchase_log(request):
    try:
        body = json.loads(request.body)
        student_id = body.get('student_id')
        price = body.get('price')
        purchased_at = body.get('purchased_at')

        if not student_id:
            return JsonResponse({'error': 'student_id is required'}, status=400)
        
        if not price:
            return JsonResponse({'error': 'price is required'}, status=400)
        
        if not purchased_at:
            return JsonResponse({'error': 'purchased_at is required'}, status=400)
        
        item = models.User.objects.filter(price=price, is_sales=True)

        if not item.exists():
            return JsonResponse({'error': 'Item not found'}, status=404)
        
        user = models.User.objects.get(student_id=student_id)

        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        models.PurchaseLog.objects.create(user_id=user.id, item_id=item.id)

        send_to_line_group(user.name, item.name, price, purchased_at)
        
        return JsonResponse({'success': True})
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)