# lms/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from .models import Course, Lesson, Subscription
from django.core.exceptions import ValidationError
from .validators import validate_video_url


class LessonCRUDTests(APITestCase):
    def setUp(self):
        # создаём двух пользователей: owner и other
        self.owner = User.objects.create_user(email='owner@example.com', password='pass1234')
        self.other = User.objects.create_user(email='other@example.com', password='pass1234')

        # создаём курс, привязанный к owner
        self.course = Course.objects.create(title='Test Course', owner=self.owner)

        # логиним owner через force_authenticate
        self.client.force_authenticate(user=self.owner)

    def test_create_lesson_as_owner(self):
        url = reverse('api:lesson-list')
        data = {
            'title': 'Lesson 1',
            'course': self.course.id,
            'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 1)
        lesson = Lesson.objects.first()
        self.assertEqual(lesson.owner, self.owner)

    def test_create_lesson_invalid_external_url(self):
        url = reverse('api:lesson-list')
        data = {
            'title': 'Bad link',
            'course': self.course.id,
            'video_url': 'https://somecourse.com/video/1'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_url', response.data)

    def test_update_lesson_only_owner_or_moder(self):
        # создаём урок владельцем
        lesson = Lesson.objects.create(title='Lesson', course=self.course, owner=self.owner)
        url = reverse('api:lesson-detail', args=[lesson.id])
        data = {'title': 'Changed'}
        # другой пользователь не может редактировать
        self.client.force_authenticate(user=self.other)
        response = self.client.patch(url, data, format='json')
        self.assertIn(response.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))
        # владелец может
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_lesson_only_owner(self):
        lesson = Lesson.objects.create(title='LessonDel', course=self.course, owner=self.owner)
        url = reverse('api:lesson-detail', args=[lesson.id])
        # другой пользователь — нельзя
        self.client.force_authenticate(user=self.other)
        resp = self.client.delete(url)
        self.assertIn(resp.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))
        # владелец может
        self.client.force_authenticate(user=self.owner)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class SubscriptionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='subuser@example.com', password='pass1234')
        self.course_owner = User.objects.create_user(email='owner2@example.com', password='pass1234')
        self.course = Course.objects.create(title='CourseSub', owner=self.course_owner)
        self.client.force_authenticate(user=self.user)

    def test_subscribe_unsubscribe(self):
        subscribe_url = reverse('api:course-subscribe', args=[self.course.id])
        unsubscribe_url = reverse('api:course-unsubscribe', args=[self.course.id])
        url = reverse('api:course-detail', args=[self.course.id])

        # подписка
        resp = self.client.post(subscribe_url)
        self.assertIn(resp.status_code, (status.HTTP_201_CREATED, status.HTTP_200_OK))
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

        # повторная подписка вернёт 200 and not duplicate
        resp = self.client.post(subscribe_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # отписка
        resp = self.client.delete(unsubscribe_url)
        self.assertIn(resp.status_code, (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK))
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_course_serializer_has_is_subscribed_flag(self):
        url = reverse('api:course-detail', args=[self.course.id])

        # сначала не подписан
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('is_subscribed', resp.data)
        self.assertFalse(resp.data['is_subscribed'])

        # подписываемся
        self.client.post(reverse('api:course-subscribe', args=[self.course.id]))
        resp = self.client.get(url)
        self.assertTrue(resp.data['is_subscribed'])


class ValidatorTests(APITestCase):
    def test_valid_youtube_links(self):
        valid_links = [
            "https://www.youtube.com/watch?v=abc123",
            "https://youtu.be/xyz789",
            "http://m.youtube.com/watch?v=123"
        ]
        for link in valid_links:
            try:
                validate_video_url(link)
            except ValidationError:
                self.fail(f"Валидатор ошибочно отклонил допустимую ссылку: {link}")

    def test_invalid_links(self):
        invalid_links = [
            "https://vimeo.com/12345",
            "https://example.com/video",
            "https://google.com"
        ]
        for link in invalid_links:
            with self.assertRaises(ValidationError):
                validate_video_url(link)
