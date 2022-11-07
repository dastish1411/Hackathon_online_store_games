from email.policy import default
from rest_framework import serializers
from django.db.models import Avg

from .models import (
    Products,
    Rating,
    Comment,
    ProductsImage,
    Like
)


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ('user', 'title', 'image', 'slug')

class ProductSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Products
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['comments'] = CommentSerializer(
            instance.comments.all(), many=True
        ).data
        rating = instance.ratings.aggregate(Avg('rating'))['rating__avg']
        representation['likes'] = instance.likes.all().count()
        representation['liked_by'] = LikeSerializer(
            instance.likes.all().only('user'), many=True).data
        if rating:
            representation['rating'] = round(rating, 1)
        else:
            representation['rating'] = 0.0
        return representation


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsImage
        fields = 'image',


class ProductCreateSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(
        default=serializers.CurrentUserDefault(),
        source='user.username'
    )
    
    class Meta:
        model = Products
        fields = '__all__'

    def create(self, validated_data):
        products = Products.objects.create(**validated_data)
        return products

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(
        default=serializers.CurrentUserDefault(),
        source='user.username'
    )

    class Meta:
        model = Comment
        exclude = ['products']


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(
        source='user.username'
    )

    class Meta:
        model = Rating
        fields = ('rating', 'user', 'products')

    def validate(self, attrs):
        user = self.context.get('request').user
        attrs['user'] = user
        rating = attrs.get('rating')
        if rating not in (1, 2, 3, 4, 5):
            raise serializers.ValidationError(
                'Wrong value! Rating must be between 1 and 5'
            )
        return attrs

    def update(self, instance, validated_data):
        instance.rating = validated_data.get('rating')
        instance.save()
        return super().update(instance, validated_data)


class CurrentProductsDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['products']


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    products = serializers.HiddenField(default=CurrentProductsDefault())

    class Meta:
        model = Like
        fields = '__all__'

    def create(self, validated_data):
        user = self.context.get('request').user
        products = self.context.get('products').pk
        like = Like.objects.filter(user=user, products=products).first()
        if like:
            raise serializers.ValidationError('Already liked')
        return super().create(validated_data)

    def unlike(self):
        user = self.context.get('request').user
        products = self.context.get('products').pk
        like = Like.objects.filter(user=user, products=products).first()
        if like:
            like.delete()
        else:
            raise serializers.ValidationError('Not liked yet')


class LikedProductsSerializer(serializers.ModelSerializer):
    url = serializers.URLField(source='products.get_absolute_url')
    products = serializers.ReadOnlyField(source='products.title')

    class Meta:
        model = Like
        fields = ['products', 'user', 'url']