from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Auteur, Livre, Emprunt
from datetime import date, timedelta


class AuteurTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            'admin', is_staff=True, password='admin123')
        self.user = User.objects.create_user('user', password='user123')
        self.auteur = Auteur.objects.create(nom='Hugo', prenom='Victor')

    def test_liste_accessible_sans_auth(self):
        response = self.client.get('/api/auteurs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_creation_admin_seulement(self):
        response = self.client.post('/api/auteurs/',
            {'nom': 'Zola', 'prenom': 'Emile'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/auteurs/',
            {'nom': 'Zola', 'prenom': 'Emile'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LivreTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('user', password='user123')
        auteur = Auteur.objects.create(nom='Orwell', prenom='George')
        self.livre = Livre.objects.create(
            titre='1984', auteur=auteur,
            genre='science_fiction', prix=8.50,
            isbn='9782070368228'
        )

    def test_emprunter_disponible(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/livres/{self.livre.id}/emprunter/',
            {'date_retour_prevue': str(date.today() + timedelta(days=14))}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.livre.refresh_from_db()
        self.assertFalse(self.livre.disponible)

    def test_emprunter_non_disponible(self):
        self.livre.disponible = False
        self.livre.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/livres/{self.livre.id}/emprunter/',
            {'date_retour_prevue': str(date.today() + timedelta(days=14))}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuthTests(APITestCase):
    def test_register(self):
        data = {'username': 'bob', 'email': 'bob@test.com',
                'password': 'bobpass123', 'password_confirm': 'bobpass123'}
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_obtenir_jwt(self):
        User.objects.create_user('testuser', password='testpass')
        response = self.client.post('/api/auth/token/',
            {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access',  response.data)
        self.assertIn('refresh', response.data)
