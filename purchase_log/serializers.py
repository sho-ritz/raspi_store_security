from rest_framework import serializers
from .models import PurchaseLog, User, Item

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # 全フィールドを含める

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'  # 全フィールドを含める

class PurchaseLogSerializer(serializers.ModelSerializer):
    # 外部キーの詳細情報も含める場合、シリアライザをネスト
    item_id = ItemSerializer(read_only=True)
    user_id = UserSerializer(read_only=True)

    class Meta:
        model = PurchaseLog
        fields = '__all__'  # 全フィールドを含める

# 外部キーIDだけを送信可能にしたい場合のオプション
class PurchaseLogWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseLog
        fields = '__all__'
