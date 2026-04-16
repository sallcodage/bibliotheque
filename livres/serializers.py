from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Auteur, Livre, Emprunt


class AuteurSerializer(serializers.ModelSerializer):
    nombre_livres = serializers.SerializerMethodField()
#
    class Meta:
        model  = Auteur
        fields = ['id', 'nom', 'prenom', 'nationalite',
                  'date_naissance', 'nombre_livres']

    def get_nombre_livres(self, obj):
        return obj.livres.count()


class LivreListSerializer(serializers.ModelSerializer):
    """Serializer léger pour la liste"""
    auteur_nom = serializers.CharField(source='auteur.__str__', read_only=True)

    class Meta:
        model  = Livre
        fields = ['id', 'titre', 'auteur_nom', 'genre', 'prix',
                  'disponible', 'isbn']


class LivreDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour le détail"""
    auteur     = AuteurSerializer(read_only=True)
    auteur_id  = serializers.PrimaryKeyRelatedField(
        queryset=Auteur.objects.all(), source='auteur', write_only=True
    )
    nombre_emprunts = serializers.SerializerMethodField()

    class Meta:
        model  = Livre
        fields = ['id', 'titre', 'auteur', 'auteur_id', 'genre',
                  'prix', 'disponible', 'date_ajout',
                  'description', 'isbn', 'nombre_emprunts']

    def get_nombre_emprunts(self, obj):
        return obj.emprunts.count()

    def validate_isbn(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("L'ISBN ne doit contenir que des chiffres.")
        if len(value) not in [10, 13]:
            raise serializers.ValidationError("L'ISBN doit avoir 10 ou 13 chiffres.")
        return value

    def validate_prix(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le prix doit être positif.")
        return value


class EmpruntSerializer(serializers.ModelSerializer):
    emprunteur    = serializers.StringRelatedField(read_only=True)
    livre_titre   = serializers.CharField(source='livre.titre', read_only=True)
    jours_restants= serializers.SerializerMethodField()

    class Meta:
        model  = Emprunt
        fields = ['id', 'livre', 'livre_titre', 'emprunteur',
                  'date_emprunt', 'date_retour_prevue',
                  'date_retour_effective', 'statut', 'jours_restants']
        read_only_fields = ['emprunteur', 'statut', 'date_retour_effective']

    def get_jours_restants(self, obj):
        if obj.statut != 'en_cours': return None
        from datetime import date
        return (obj.date_retour_prevue - date.today()).days

    def validate(self, data):
        livre = data.get('livre')
        if livre and not livre.disponible:
            raise serializers.ValidationError("Ce livre n'est pas disponible.")
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password         = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)

