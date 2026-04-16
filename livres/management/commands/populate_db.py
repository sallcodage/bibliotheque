from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from livres.models import Auteur, Livre
from datetime import date

class Command(BaseCommand):
    help = 'Peuple la base de données avec des données de test'

    def handle(self, *args, **kwargs):
        # Créer les utilisateurs
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@test.com', 'is_staff': True}
        )
        admin.set_password('admin123')
        admin.save()

        user, _ = User.objects.get_or_create(
            username='alice',
            defaults={'email': 'alice@test.com'}
        )
        user.set_password('alice123')
        user.save()

        # Créer les auteurs
        hugo, _ = Auteur.objects.get_or_create(
            nom='Hugo', prenom='Victor',
            defaults={'nationalite': 'Française',
                      'date_naissance': date(1802, 2, 26)}
        )
        orwell, _ = Auteur.objects.get_or_create(
            nom='Orwell', prenom='George',
            defaults={'nationalite': 'Britannique',
                      'date_naissance': date(1903, 6, 25)}
        )

        # Créer les livres
        livres_data = [
            {'titre': 'Les Misérables', 'auteur': hugo,
             'genre': 'roman', 'prix': 12.90,
             'isbn': '9782070409228'},
            {'titre': '1984', 'auteur': orwell,
             'genre': 'science_fiction', 'prix': 8.50,
             'isbn': '9782070368228'},
            {'titre': 'La Ferme des animaux', 'auteur': orwell,
             'genre': 'roman', 'prix': 6.90,
             'isbn': '9782070360918'},
        ]
        for data in livres_data:
            Livre.objects.get_or_create(isbn=data['isbn'], defaults=data)

        self.stdout.write(self.style.SUCCESS('Base peuplée avec succès !'))
