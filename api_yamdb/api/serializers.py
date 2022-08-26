from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from reviews.models import Title, Category, Genre, Comment, Review

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, validators=[])
    email = serializers.EmailField(validators=[])

    def validate_username(self, data):
        username = User.objects.filter(username=data).exists()
        if data == 'me' or username:
            raise serializers.ValidationError('Невалидный username.')
        return data

    def validate_email(self, data):
        email_db = User.objects.filter(email=data).exists()
        if email_db:
            raise serializers.ValidationError('Email существует.')
        return data

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'bio', 'first_name',
                  'last_name')

        def validate_username(self, data):
            username = User.objects.filter(username=data).exists()
            if data == 'me' or username:
                raise serializers.ValidationError('Невалидный username.')
            return data

        def validate_email(self, data):
            email_db = User.objects.filter(email=data).exists()
            if email_db:
                raise serializers.ValidationError('Email существует.')
            return data


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug',)
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(required=False)
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'category', 'genre',
                  'rating')
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(required=False)
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'category', 'genre',
                  'rating')
        model = Title


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        exclude = ('review',)
        model = Comment


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )
    title = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name',
    )

    def validate(self, attrs):
        is_exist = Review.objects.filter(
            author=self.context['request'].user,
            title=get_object_or_404(
                Title,
                pk=self.context['view'].kwargs.get('title_id'))).exists()
        if is_exist and self.context['request'].method == 'POST':
            raise serializers.ValidationError(
                'Вы можете написать только один отзыв на произведение'
            )
        return attrs

    class Meta:
        fields = '__all__'
        model = Review
