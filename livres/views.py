from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from datetime import date

from .models import Auteur, Livre, Emprunt
from .serializers import (
    AuteurSerializer, LivreListSerializer, LivreDetailSerializer,
    EmpruntSerializer, RegisterSerializer,
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin


class AuteurViewSet(viewsets.ModelViewSet):
    queryset         = Auteur.objects.all()
    serializer_class = AuteurSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields    = ['nom', 'prenom', 'nationalite']
    ordering_fields  = ['nom', 'date_naissance']


class LivreViewSet(viewsets.ModelViewSet):
    queryset = Livre.objects.select_related('auteur').all()
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields   = ['genre', 'disponible', 'auteur']
    search_fields      = ['titre', 'description', 'isbn']
    ordering_fields    = ['prix', 'date_ajout', 'titre']

    def get_serializer_class(self):
        if self.action == 'list':
            return LivreListSerializer
        return LivreDetailSerializer

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def emprunter(self, request, pk=None):
        """POST /api/livres/{id}/emprunter/"""
        livre = self.get_object()
        if not livre.disponible:
            return Response({'erreur': 'Livre non disponible.'},
                            status=status.HTTP_400_BAD_REQUEST)
        date_retour = request.data.get('date_retour_prevue')
        if not date_retour:
            return Response({'erreur': 'Date de retour obligatoire.'},
                            status=status.HTTP_400_BAD_REQUEST)
        emprunt = Emprunt.objects.create(
            livre=livre, emprunteur=request.user,
            date_retour_prevue=date_retour,
        )
        livre.disponible = False
        livre.save()
        return Response(EmpruntSerializer(emprunt).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """GET /api/livres/disponibles/"""
        livres = Livre.objects.filter(disponible=True)
        return Response(LivreListSerializer(livres, many=True).data)


class EmpruntViewSet(viewsets.ModelViewSet):
    serializer_class   = EmpruntSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Emprunt.objects.select_related('livre', 'emprunteur').all()
        return Emprunt.objects.filter(emprunteur=user)

    def perform_create(self, serializer):
        serializer.save(emprunteur=self.request.user)

    @action(detail=True, methods=['post'])
    def retourner(self, request, pk=None):
        """POST /api/emprunts/{id}/retourner/"""
        emprunt = self.get_object()
        if emprunt.statut == 'retourne':
            return Response({'erreur': 'Déjà retourné.'},
            status=status.HTTP_400_BAD_REQUEST)
        emprunt.statut = 'retourne'
        emprunt.date_retour_effective = date.today()
        emprunt.save()
        emprunt.livre.disponible = True
        emprunt.livre.save()
        return Response({'message': f'Livre retourné avec succès.'})

    @action(detail=False, methods=['get'])
    def en_retard(self, request):
        """GET /api/emprunts/en_retard/"""
        emprunts = self.get_queryset().filter(
            statut='en_cours', date_retour_prevue__lt=date.today()
        )
        emprunts.update(statut='en_retard')
        return Response(self.get_serializer(emprunts, many=True).data)


class RegisterView(generics.CreateAPIView):
    queryset           = User.objects.all()
    serializer_class   = RegisterSerializer
    permission_classes = [AllowAny]
