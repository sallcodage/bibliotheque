from django.db import models

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Auteur(models.Model):
    nom          = models.CharField(max_length=100)
    prenom       = models.CharField(max_length=100)
    nationalite  = models.CharField(max_length=50, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
#
    def __str__(self):
        return f"{self.prenom} {self.nom}"

    class Meta:
        ordering = ['nom']


class Livre(models.Model):
    GENRES = [
        ('roman',           'Roman'),
        ('science_fiction', 'Science-Fiction'),
        ('policier',        'Policier'),
        ('biographie',      'Biographie'),
        ('technique',       'Technique'),
    ]

    titre     = models.CharField(max_length=200)
    auteur    = models.ForeignKey(Auteur, on_delete=models.CASCADE,
                                   related_name='livres')
    genre      = models.CharField(max_length=20, choices=GENRES, default='autre')
    prix       = models.DecimalField(max_digits=6, decimal_places=2)
    disponible = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    description= models.TextField(blank=True)
    isbn       = models.CharField(max_length=13, unique=True)

    def __str__(self):
        return f"{self.titre} — {self.auteur}"


class Emprunt(models.Model):
    STATUTS = [
        ('en_cours', 'En cours'),
        ('retourne', 'Retourné'),
        ('en_retard','En retard'),
    ]

    livre = models.ForeignKey(Livre, on_delete=models.CASCADE,
                                              related_name='emprunts')
    emprunteur = models.ForeignKey(User, on_delete=models.CASCADE,
                                              related_name='emprunts')
    date_emprunt = models.DateTimeField(auto_now_add=True)
    date_retour_prevue  = models.DateField()
    date_retour_effective = models.DateField(null=True, blank=True)
    statut  = models.CharField(max_length=10, choices=STATUTS,
                                            default='en_cours')

    def __str__(self):
        return f"{self.emprunteur.username} — {self.livre.titre}"

class Note(models.Model):
    livre = models.ForeignKey('Livre', on_delete=models.CASCADE, related_name='notes')
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    valeur = models.IntegerField()

    def __str__(self):
        return f"{self.livre.titre} - {self.valeur}"


# Create your models here.
