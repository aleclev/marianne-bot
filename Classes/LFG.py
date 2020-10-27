import discord
import datetime
from Fonctions import Message

class LFG:
    #TODO: Méthode pour notifier tout le monde.
    #TODO: Méthode pour ajouter/supprimer des joueurs.
    #TODO: Méthode pour ajouter/supprimer le post à la base de données
    #TODO: Méthodes pour mettre à jour le message d'un post.

    def __init__(self, nomActivite : str, createur : discord.User, limiteJoueurs : int, dateDebut : datetime.datetime):
        """Constructeur de la classe LFG.

        Args:
            nomActivite (str): Le nom de l'activité
            createur (discord.User): Le créateur du post.
            limiteJoueurs (int): Le nombre maximal de joueurs pouvants participé à l'activité
            dateDebut (datetime.datetime): La date du début de l'activité.
        """
        #TODO: Le post doit avoir un id.

        #Préconditions
        assert nomActivite != ""
        assert limiteJoueurs > 1
        assert dateDebut > datetime.datetime.now()

        self.nomActivite = nomActivite
        self.createur = createur
        self.limiteJoueurs = limiteJoueurs
        self.dateDebut = dateDebut