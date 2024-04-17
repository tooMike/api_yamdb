import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.apps import apps

User = get_user_model()


class Command(BaseCommand):
    help = ('Загрузка данных из csv-файлов в модели. ',
            'Пример команды: python manage.py import_data ',
            '"Model1:path/to/file1.csv" "Model2:path/to/file2.csv"')

    def add_arguments(self, parser):
        parser.add_argument(
            'app_model_file_triples',
            nargs='+', type=str,
            help=('Перечислите: приложения, модели и пути к файлам csv ',
                  '(app_name:model_name:path/to/file.csv)')
        )

    def handle(self, *args, **options):
        triples = options['app_model_file_triples']

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
