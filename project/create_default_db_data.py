import django
import os
from dotenv import find_dotenv, load_dotenv
os.environ["DJANGO_SETTINGS_MODULE"] = 'project.settings'
from django.conf import settings

load_dotenv(find_dotenv())

if not settings.configured:
    django.setup()

from accounts.models import User
from accounts.models import StudyField


def create_superuser_for_adminpanel():
    User.objects.create_superuser(username=os.getenv("DJANGO_SUPERUSER_USERNAME", "Iteen.Admin"),
                                  password=os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin1admin1"))


def create_study_fields():
        StudyField(study_field="БПЛА", short_study_field="БПЛА").save()
        StudyField(study_field="Веб-технологии", short_study_field="Веб-технологии").save()
        StudyField(study_field="Дизайн", short_study_field="Дизайн").save()
        StudyField(study_field="Практическое программирование (Лаборатория)", short_study_field="IT-Лаборатория").save()
        StudyField(study_field="Программирование и GameDev", short_study_field="GameDev").save()
        StudyField(study_field="Робототехника", short_study_field="Робототехника").save()
        StudyField(study_field="Техномейкерство", short_study_field="Техномейкерство").save()
        StudyField(study_field="Computer Science", short_study_field="Computer Science").save()
        StudyField(study_field="3D-моделирование", short_study_field="3D").save()


if __name__ == '__main__':
    try:
        create_superuser_for_adminpanel()
    except django.db.utils.IntegrityError:
        print('User already exist!')

    all_fields = StudyField.objects.all()
    if len(all_fields) == 0:
        create_study_fields()
