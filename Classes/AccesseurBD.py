"""
Interface pour effectuer des requêtes à la base de données.
"""
import pymysql
import discord
from Fonctions import Temps
class AcesseurBD():
    def __init__(self, connectionBD : pymysql.Connection):
        self.connectionBD = connectionBD
    
    def ajtApplicationClan(self, utilisateur : discord.User, sigleClan : str, message : str):
        with self.connectionBD.cursor() as cur:
            #Ajout de l'entrée dans la bd.
            tempsUnix = Temps.reqTempsUNIX()
            req = "INSERT INTO application_clan (utilisateur_discord_id, clan_sigle, temps_unix, message) VALUES (%s, %s, %s, %s);"
            cur.execute(req, (utilisateur.id, sigleClan, tempsUnix, message))

    def reqClanDict(self, sigleClan : str) -> dict:
        """Retourne le tuple du clan associé au sigle.

        Args:
            sigleClan (str): Le sigle du clan recherché.

        Returns:
            dict: [description]
        """
        with self.connectionBD.cursor() as cur:
            requete = "SELECT * FROM clan WHERE sigle=%s;"
            cur.execute(requete, sigleClan)
            return cur.fetchone()

    def reqTousClanDict(self) -> list:
        with self.connectionBD.cursor() as cur:
            requete = "SELECT * FROM clan;"
            cur.execute(requete)
            return cur.fetchall()
    
    def reqUtilisateurDict(self, id : int) -> dict:
        with self.connectionBD.cursor() as cur:
            requete = "SELECT * FROM utilisateur WHERE utilisateur.discord_id=%s;"
            cur.execute(requete, id)
            return cur.fetchone()

    def reqListeClansFormatee(self) -> str:
        listeClanDict = self.reqTousClanDict()

        message = "```"

        for clan in listeClanDict:
            message += f"{clan['sigle']} : {clan['nom']}\n"
        
        return message + "```"
