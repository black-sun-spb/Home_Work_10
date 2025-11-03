# lms/tests_full.py
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Course, Lesson, Subscription

User = get_user_model()


class CourseLessonTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # создаём пользователей
        self.user = User.objects.create_user(email='user@test.com', password='password')
        self.moderator = User.objects.create_user(email='mod@test.com', password='password')
        self.moderator.groups.create(name='moderators')

        # создаём курс
        self.course = Course.objects.create(title='Test Course', owner=self.user)
        # создаём урок
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            course=self.course,
            owner=self.user,
            video_url='https://youtube.com/watch?v=abc123'
        )

    # -----------------------------------
    # CRUD для курсов
    # -----------------------------------
    def test_create_course_as_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('lms:course-list')
        data = {'title': 'New Course'}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['title'], data['title'])

    def test_create_course_as_moderator_forbidden(self):
        self.client.force_authenticate(user=self.moderator)
        url = reverse('lms:course-list')
        data = {'title': 'Mod Course'}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # -----------------------------------
    # CRUD для уроков
    # -----------------------------------
    def test_create_lesson_as_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('lms:lesson-list')
        data = {'title': 'New Lesson', 'course': self.course.id}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['title'], data['title'])

    def test_create_lesson_as_moderator_forbidden(self):
        self.client.force_authenticate(user=self.moderator)
        url = reverse('lms:lesson-list')
        data = {'title': 'Mod Lesson', 'course': self.course.id}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # -----------------------------------
    # Валидатор видео URL
    # -----------------------------------
    def test_lesson_with_invalid_url(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('lms:lesson-list')
        data = {'title': 'Bad Lesson', 'course': self.course.id, 'video_url': 'https://vimeo.com/123'}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_url', resp.data)

    def test_lesson_with_empty_url(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('lms:lesson-list')
        data = {'title': 'Empty URL Lesson', 'course': self.course.id, 'video_url': ''}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['video_url'], '')

    # -----------------------------------
    # Подписка на курс
    # -----------------------------------
    def test_subscribe_unsubscribe(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('lms:course-subscribe', args=[self.course.id])

        # подписка
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

        # отписка
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_course_serializer_has_is_subscribed_flag(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('lms:course-detail', args=[self.course.id])
        # изначально False
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(resp.data['is_subscribed'])

        # создаём подписку
        Subscription.objects.create(user=self.user, course=self.course)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['is_subscribed'])

    # -----------------------------------
    # Пагинация
    # -----------------------------------
    def test_courses_pagination(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('lms:course-list')
        # создаём много курсов
        for i in range(15):
            Course.objects.create(title=f'Course {i}', owner=self.user)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['results']), 10)  # page_size по умолчанию

    def test_lessons_pagination(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('lms:lesson-list')
        # создаём много уроков
        for i in range(15):
            Lesson.objects.create(title=f'Lesson {i}', course=self.course, owner=self.user)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['results']), 10)  # page_size по умолчанию
