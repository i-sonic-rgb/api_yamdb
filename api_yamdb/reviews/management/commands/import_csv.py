import os
from csv import DictReader

from django.core.management import BaseCommand
from django.shortcuts import get_object_or_404
from reviews.models import (Category, Comment, Genre, Review, Title,
                            TitleGenre, User)

from api_yamdb.settings import BASE_DIR

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the  data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""


class Command(BaseCommand):
    # Show this when the user types help
    help = "Loads data from /api_yamdb/static/data"

    def handle(self, *args, **options):
        # Show this if the data already exist in the database
        if (
            Category.objects.exists()
            or Comment.objects.exists()
            or Genre.objects.exists()
            or Review.objects.exists()
            or Title.objects.exists()
            or TitleGenre.objects.exists()
            or User.objects.exists()
        ):
            print('Data already loaded...exiting.')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return

        # Show this before loading the data into the database
        print("Loading data")

        # Code to load the data into database
        for row in DictReader(open(
            os.path.join(BASE_DIR, 'static/data/users.csv'),
            'r', encoding='utf-8'
        )):
            User.objects.create(**row)

        for row in DictReader(open(
            os.path.join(BASE_DIR, 'static/data/category.csv'),
            'r', encoding='utf-8'
        )):
            Category.objects.create(**row)

        for row in DictReader(open(
            os.path.join(BASE_DIR, 'static/data/genre.csv'),
            'r', encoding='utf-8'
        )):
            Genre.objects.create(**row)

        for row in DictReader(open(
            os.path.join(BASE_DIR, 'static/data/titles.csv'),
            'r', encoding='utf-8'
        )):
            Title.objects.create(
                name=row['name'],
                year=row['year'],
                category=get_object_or_404(Category, id=row['category'])
            )

        for row in DictReader(open(
            os.path.join(BASE_DIR, 'static/data/genre_title.csv'),
            'r', encoding='utf-8'
        )):
            TitleGenre.objects.create(
                title_id=get_object_or_404(Title, id=row['title_id']),
                genre_id=get_object_or_404(Genre, id=row['genre_id']),
            )

        for row in DictReader(open(
            os.path.join(BASE_DIR, 'static/data/review.csv'),
            'r', encoding='utf-8'
        )):
            Review.objects.create(
                title_id=row['title_id'],
                text=row['text'],
                author=get_object_or_404(User, id=row['author']),
                score=row['score'],
                pub_date=row['pub_date']
            )

        for row in DictReader(open(
            os.path.join(BASE_DIR, 'static/data/comments.csv'),
            'r', encoding='utf-8'
        )):
            Comment.objects.create(
                review_id=row['review_id'],
                text=row['text'],
                author=get_object_or_404(User, id=row['author']),
                pub_date=row['pub_date']
            )
        print("Data upload finished.")
