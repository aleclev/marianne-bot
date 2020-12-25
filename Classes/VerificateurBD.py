"""
Classe qui sert à effectuer des opérations de vérification sur la base de données.
Les vérifications sont faites à partir de la connection MYSQL dans le __main__.py.
"""
import pymysql
import discord
from Classes import MarianneException

class VerificateurBD():
    def __init__(self, connectionBD : pymysql.Connection):
        self.connectionBD = connectionBD
    
    def utilisateurEnregSteam(self, utilisateur : discord.User) -> bool:
        """Vérifie qu'un utilisateur a enregistré son profile steam.

        Args:
            utilisateur (discord.User): L'utilisateur à vétifier

        Raises:
            MarianneException.ErreurBD: Erreur de formating dans la réponse.

        Returns:
            bool: True si l'utilisateur est enregistré
        """
        with self.connectionBD.cursor(cursor=pymysql.cursors.Cursor) as cur:
            requete = "SELECT EXISTS(SELECT * FROM utilisateur WHERE discord_id=%s AND steam_id IS NOT NULL);"
            cur.execute(requete, utilisateur.id)
            res = cur.fetchone()[0]
            print(res)
            #L'utilisateur n'est pas enregistré sur Discord.
            if res == 0:
                return False
            elif res == 1:
                return True
            else:
                #Cette ligne ne devrait jamais être atteinte.
                raise MarianneException.ErreurBD()

    def utilisateurEnregBungie(self, utilisateur : discord.User) -> bool:
        """Vérifie qu'un utilisateur a enregistré son profile bungie.

        Args:
            utilisateur (discord.User): L'utilisateur à vétifier

        Raises:
            MarianneException.ErreurBD: Erreur de formating dans la réponse.

        Returns:
            bool: True si l'utilisateur est enregistré
        """
        with self.connectionBD.cursor(cursor=pymysql.cursors.Cursor) as cur:
            requete = "SELECT EXISTS(SELECT * FROM utilisateur WHERE discord_id=%s AND bungie_id IS NOT NULL);"
            cur.execute(requete, utilisateur.id)
            res = cur.fetchone()[0]
            #L'utilisateur n'est pas enregistré sur Discord.
            if res == 0:
                return False
            elif res == 1:
                return True
            else:
                #Cette ligne ne devrait jamais être atteinte.
                raise MarianneException.ErreurBD()
        
    def utilisateurEnregDiscord(self, utilisateur : discord.User) -> bool:
        """Vérifi si le profile discord de l'utilisateur est enregistré.

        Args:
            utilisateur (discord.User): L'utilisateur discord.

        Raises:
            MarianneException.ErreurBD: Erreur de formating dans la réponse.

        Returns:
            bool: True si l'utilisateur est enregistré.
        """
        with self.connectionBD.cursor(cursor=pymysql.cursors.Cursor) as cur:
            requete = "SELECT EXISTS(SELECT * FROM utilisateur WHERE discord_id=%s);"
            cur.execute(requete, utilisateur.id)
            res = cur.fetchone()[0]
            #L'utilisateur n'est pas enregistré sur Discord.
            if res == 0:
                return False
            elif res == 1:
                return True
            else:
                #Cette ligne ne devrait jamais être atteinte.
                raise MarianneException.ErreurBD()
    
    def sigleClanExiste(self, sigle : str) -> bool:
        with self.connectionBD.cursor(cursor=pymysql.cursors.Cursor) as cur:
            requete = "SELECT EXISTS(SELECT * FROM clan WHERE sigle=%s);"
            cur.execute(requete, sigle)
            res = cur.fetchone()[0]
            #L'utilisateur n'est pas enregistré sur Discord.
            if res == 0:
                return False
            elif res == 1:
                return True
            else:
                #Cette ligne ne devrait jamais être atteinte.
                raise MarianneException.ErreurBD()
        
    def utilisateurEstNotifTagsBloque(self, utilisateur: discord.User, utilisateurBloque: discord.User) -> bool:
        """Vérifie s'il existe un lien de bloquage entre utilisateur et utilisateurBloque.

        Args:
            utilisateur (discord.User): L'utilisateur.
            utilisateurBloque (discord.User): L'utilisateur bloqué.

        Returns:
            bool: Vrai si utilisateur bloque les notifs de utilisateurBloque.
        """
        with self.connectionBD.cursor(cursor=pymysql.cursors.Cursor) as cur:
            requete = "SELECT EXISTS(SELECT * FROM blocage_notiftag bnt WHERE bnt.utilisateur_discord_id=%s AND bnt.utilisateur_bloque_discord_id=%s);"
            cur.execute(requete, (utilisateur.id, utilisateurBloque.id))
            res = cur.fetchone()[0]
            
            #L'entrée n'existe pas.
            if res == 0:
                return False
            
            #L'entrée existe.
            elif res == 1:
                return True
            else:
                #Cette ligne ne devrait jamais être atteinte.
                raise MarianneException.ErreurBD()