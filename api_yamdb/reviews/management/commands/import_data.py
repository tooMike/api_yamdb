import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.apps import apps


triples = [
    "users:YamdbUser:static/data/users.csv",
    "reviews:Category:static/data/category.csv",
    "reviews:Genre:static/data/genre.csv",
    "reviews:Title:static/data/titles.csv",
    "reviews:GenreTitle:static/data/genre_title.csv",
    "reviews:Review:static/data/review.csv",
    "reviews:Comment:static/data/comments.csv",
]


class Command(BaseCommand):
    help = ('Загрузка данных из csv-файлов в модели. ',
            'Пример команды: python manage.py import_data ',
            '"Model1:path/to/file1.csv" "Model2:path/to/file2.csv"')

    def handle(self, *args, **options):
        for triple in triples:
            parts = triple.split(':')
            if len(parts) == 3:
                app_name, model_name, csv_file_path = parts
                model = apps.get_model(app_name, model_name)
                self.import_data(model, csv_file_path)
            else:
                self.stdout.write(
                    self.style.ERROR(f"Неверный формат: '{triple}'")
                )

    def import_data(self, model, csv_file_path):
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            field_names = next(reader)  # Получение заголовков
            for row in reader:
                data = {field_names[i]: row[i] for i in range(
                    len(field_names))}
                # Распаковываем словарь и создаем объект модели
                model.objects.create(**data)

        self.stdout.write(self.style.SUCCESS('Successfully imported data'))
