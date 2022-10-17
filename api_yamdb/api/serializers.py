from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import validate_username, validate_year

from api_yamdb.settings import EMAIL_MAX_LENGTH, NAME_MAX_LENGTH

VALDATE_SCORE = 'Come On! Поставьте оценку от 1 до 10!'
UNIQUE_EMAIL_MESSAGE = 'Пользователь с таким email уже существует'


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(
        max_length=NAME_MAX_LENGTH,
        required=True,
        validators=[
            validate_username, UniqueValidator(queryset=User.objects.all())])

    class Meta:
        fields = ('username', 'email')


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=NAME_MAX_LENGTH,
        required=True,
        validators=[
            validate_username, UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class ReviewSerializer(serializers.ModelSerializer):
    '''Serializer for Review model - RETRIEVE, UPDATE or DESTROY actions.'''
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    score = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta:
        fields = ('id', 'author', 'text', 'pub_date', 'score')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    '''Serializer for Comment model.'''
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        fields = ('id', 'author', 'text', 'pub_date')
        model = Comment


class GenreSerializer(serializers.ModelSerializer):
    '''Serializer for Genre model.'''

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    '''Serializer for Category model.'''

    class Meta:
        fields = ('name', 'slug')
        model = Category


class TitleSerializerWritable(serializers.ModelSerializer):
    '''Serializer for Title model for writing data.'''
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    year = serializers.IntegerField(
        validators=[validate_year, ]
    )

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = ('rating',)


class TitleSerializerReadOnly(serializers.ModelSerializer):
    '''Serializer for Title model for reading data.'''
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = ('category', 'rating')
