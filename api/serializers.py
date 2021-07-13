from django.contrib.auth import get_user_model
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from .models import Categories, Comment, Genres, Review, Titles

User = get_user_model()


class AuthStartSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class AuthConfirmationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    confirmation_code = serializers.UUIDField(required=True)

    def validate(self, data):
        email = data.get('email')
        confirmation_code = data.get('confirmation_code')
        user = User.objects.filter(confirmation_code=confirmation_code,
                                   email=email)
        if not user.first():
            raise serializers.ValidationError('Not correct confirmation code')
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name',
                  'username', 'bio', 'email', 'role')
        extra_kwargs = {
            'username': {'required': True},
            'email': {
                'required': True,
                'validators': [UniqueValidator(queryset=User.objects.all())],
            },
        }

    def validate_role(self, value):
        request = self.context.get('request')
        if hasattr(request, 'user') and request.user.is_user():
            raise serializers.ValidationError('You can`t change your role')
        return value


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Categories
        extra_kwargs = {
            'name': {'required': True}
        }

    def validate_slug(self, data):
        category = Categories.objects.filter(slug=data).exists()
        if category:
            raise serializers.ValidationError(
                {'slug': 'This slug already exists'})
        return data

    def create(self, data):
        if not data.get('slug'):
            data['slug'] = slugify(data.get('name'))
        return super(CategoriesSerializer, self).create(data)


class GenresSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False)

    class Meta:
        fields = ('name', 'slug')
        model = Genres
        extra_kwargs = {
            'name': {'required': True}
        }

    def validate_slug(self, data):
        category = Genres.objects.filter(slug=data).exists()
        if category:
            raise serializers.ValidationError(
                {'slug': 'This slug already exists'})
        return data

    def create(self, data):
        if data.get('slug') is None:
            data['slug'] = slugify(data.get('name'))
        return super(GenresSerializer, self).create(data)


class TitlesSerializer(serializers.ModelSerializer):
    year = serializers.IntegerField(required=False)
    description = serializers.CharField(required=False)
    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug', queryset=Genres.objects.all())
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Categories.objects.all())

    class Meta:
        fields = '__all__'
        model = Titles

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Titles.objects.create(**validated_data)
        for genre in genres:
            title.genre.add(genre)
        return title

    def to_representation(self, instance):
        representation = super(TitlesSerializer, self).to_representation(
            instance)
        genres_array = []
        for genre in representation['genre']:
            existed_genre = Genres.objects.get(slug=genre)
            dict_genre = {
                'name': existed_genre.name,
                'slug': existed_genre.slug
            }
            genres_array.append(dict_genre)
        representation['genre'] = genres_array
        category = Categories.objects.get(slug=representation['category'])
        dict_category = {
            'name': category.name,
            'slug': category.slug
        }
        representation['category'] = dict_category
        return representation


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ['author']
        model = Comment


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ['author']
        model = Review

    def validate(self, data):
        request = self.context['request']
        if request.method == 'POST' and Review.objects.filter(
            author=request.user,
            title=request.parser_context['kwargs']['title_id'],
        ).exists():
            raise serializers.ValidationError("You can write only one review.")
        return data
