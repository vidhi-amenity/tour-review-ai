from rest_framework import viewsets
from api.serializers import ExportScheduleSerializer, ScheduleEmailAddressSerializer
from api.models import ExportSchedule, ScheduleEmailAddress
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import pytz
from datetime import datetime
import json


class ExportScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ExportScheduleSerializer
    pagination_class = None

    def get_queryset(self):
        client = self.request.user.created_by if self.request.user.created_by else self.request.user
        return ExportSchedule.objects.filter(client=client)

    def perform_create(self, serializer):
        client = self.request.user.created_by if self.request.user.created_by else self.request.user
        email_addresses_data = self.request.data.get('email_addresses', [])
        schedule = self.request.data.get('schedule', [])

        by_rating = self.request.data.get('by_rating')
        by_agency = self.request.data.get('by_agency')
        by_tour = self.request.data.get('by_tour')
        by_country = self.request.data.get('by_country')
        by_responded = self.request.data.get('by_responded')

        instance = serializer.save()
        instance.email_addresses.set(email_addresses_data)
        instance = serializer.save()
        instance.client = client

        task_id = self.create_schedule(instance, schedule, by_rating, by_agency, by_tour, by_country, by_responded)
        instance.schedule_id = task_id
        instance.save()

    def perform_update(self, serializer):
        email_addresses_data = self.request.data.get('email_addresses', [])
        schedule = self.request.data.get('schedule', [])
        instance = serializer.save()
        instance.email_addresses.set(email_addresses_data)

        by_rating = self.request.data.get('by_rating')
        by_agency = self.request.data.get('by_agency')
        by_tour = self.request.data.get('by_tour')
        by_country = self.request.data.get('by_country')
        by_responded = self.request.data.get('by_responded')

        if instance.schedule_id:
            try:
                task = PeriodicTask.objects.get(id=instance.schedule_id)
                task.delete()

                task_id = self.create_schedule(instance, schedule, by_rating, by_agency, by_tour, by_country, by_responded)
                instance.schedule_id = task_id
                instance.save()

            except PeriodicTask.DoesNotExist:
                print('')

    def perform_destroy(self, instance):
        instance.delete()
        if instance.schedule_id:
            try:
                task = PeriodicTask.objects.get(id=instance.schedule_id)
                task.delete()
            except PeriodicTask.DoesNotExist:
                print('')

    def create_schedule(self, export_schedule, schedule, by_rating, by_agency, by_tour, by_country, by_responded):
        print("Schedule = ", schedule)
        print("Export Schedule ID = ", export_schedule.id)
        schedule_name = f'Export {export_schedule.id}'

        # Scomponi l'orario in componenti
        minute, hour, day_of_month, month_of_year, day_of_week = schedule.split()

        # Crea un datetime con l'orario dell'utente
        today = datetime.now()
        user_time = today.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
        print("USER TIME = ", user_time)
      
        # Ottieni il fuso orario dell'utente
        # tz = pytz.timezone(self.request.user.timezone)

        # Localizza il datetime con il fuso orario dell'utente
        # localized_user_time = tz.localize(user_time)

        # Converti l'orario in UTC
        # utc_time = localized_user_time.astimezone(pytz.UTC)

        # import tour_reviews_ai.tasks
        # test_email = tour_reviews_ai.tasks.task_schedule_email_report(export_schedule.id, by_rating, by_agency, by_tour, by_country, by_responded)
        # print("TEST EMAIL = ", test_email)

        crontab_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=minute,
            hour=hour,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
        )

        print(crontab_schedule)

        task = PeriodicTask.objects.create(
            crontab=crontab_schedule,
            name=schedule_name,
            task='tour_reviews_ai.tasks.task_schedule_email_report',
            # args=[export_schedule.id]
            # args=[export_schedule.id, by_rating, by_agency, by_tour, by_country, by_responded],
            args= json.dumps([export_schedule.id, by_rating, by_agency, by_tour, by_country, by_responded]),
        )
        print(task)

        return task.id


class ScheduleEmailAddressViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduleEmailAddressSerializer
    pagination_class = None

    def perform_create(self, serializer):
        client = self.request.user.created_by if self.request.user.created_by else self.request.user
        serializer.save(client=client)

    def get_queryset(self):
        # print(self.request.user.firstname)
        client = self.request.user.created_by if self.request.user.created_by else self.request.user
        return ScheduleEmailAddress.objects.filter(client=client)

    