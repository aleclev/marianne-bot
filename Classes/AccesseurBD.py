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
    
    def ajtNotifTag(self, tagNom: str, utilisateur: discord.User):
        """Permet d'ajouter un lien entre un utilisateur et un NotifTag.

        Args:
            tagNom (str): Le nom du tag à ajouter.
            utilisateur (discord.User): L'utilisateur pour lequel on ajoute le tag.
        """
        with self.connectionBD.cursor() as cur:
            requete = "INSERT INTO abonnement_notiftag VALUES (%s, %s);"
            cur.execute(requete, (utilisateur.id, tagNom))

    def enlNotifTag(self, tagNom: str, utilisateur: discord.User):
        """Permet de supprimer un lien entre un utilisateur et un NotifTag.

        Args:
            tagNom (str): Le nom du tag à supprimer.
            utilisateur (discord.User): L'utilisateur.
        """
        with self.connectionBD.cursor() as cur:
            requete = "DELETE bnt FROM abonnement_notiftag bnt WHERE bnt.utilisateur_discord_id=%s AND bnt.nomTag=%s;;"
            cur.execute(requete, (utilisateur.id, tagNom))

    def enlTousNotifTag(self, utilisateur: discord.User):
        """Enlève tous les lien NotifTags de l'utilisateur.

        Args:
            utilisateur (discord.User): L'utilisateur à modifier.
        """
        with self.connectionBD.cursor() as cur:
            requete = "DELETE bnt FROM abonnement_notiftag AS bnt WHERE bnt.utilisateur_discord_id=%s;"
            cur.execute(requete, (utilisateur.id,))

    def reqTousNotifTag(self, utilisateur: discord.User) -> tuple:
        """Retourne une liste des NotifTags que l'utilisateur a enregistré.

        Args:
            utilisateur (discord.User): L'utilisateur recherché.

        Returns:
            list: La liste <str> des NotifTags.
        """
        with self.connectionBD.cursor(cursor=pymysql.cursors.Cursor) as cur:
            requete = "SELECT abt.nomTag FROM abonnement_notiftag abt WHERE abt.utilisateur_discord_id=%s;"
            cur.execute(requete, (utilisateur.id,))
            
            #Le retour de cette fonction est un tuple de tuple. tue moi svp
            tupleRaw = cur.fetchall()

            listeRetour = []

            for elem in tupleRaw:
                listeRetour.append(elem[0])
            
            return listeRetour

    def ajtLienBloquage(self, utilisateur: discord.User, utilisateurABloquer: discord.User):
        """Permet d'ajouter un lien de bloquage entre utilisateur et utilisateurABloquer.
        utilisateur ne recevera pas de notifications de utilisateurABloquer.

        Args:
            utilisateur (discord.User): L'utilisateur qui souhaite bloquer.
            utilisateurABloquer (discord.User): L'utilisateur qu'on souhaite bloquer.
        """
        with self.connectionBD.cursor() as cur:
            requete = "INSERT INTO blocage_notiftag VALUES (%s, %s);"
            cur.execute(requete, (utilisateur.id, utilisateurABloquer.id))
    
    def enlLienBloquage(self, utilisateur: discord.User, utilisateurABloquer: discord.User):
        """Permet d'enlever un lien de bloquage entre utilisateur et utilisateurABloquer.

        Args:
            utilisateur (discord.User): L'utilisateur qui souhaitait bloquer.
            utilisateurABloquer (discord.User): L'utilisateur qu'on souhaitait bloquer.
        """
        with self.connectionBD.cursor() as cur:
            requete = "DELETE bnt FROM blocage_notiftag bnt WHERE bnt.utilisateur_discord_id=%s AND bnt.utilisateur_bloque_discord_id=%s;"
            cur.execute(requete, (utilisateur.id, utilisateurABloquer.id))
    
    def reqTousLiensBlocage(self, utilisateur: discord.User):
        with self.connectionBD.cursor(cursor=pymysql.cursors.Cursor) as cur:
            requete = "SELECT bnt.utilisateur_bloque_discord_id FROM blocage_notiftag bnt WHERE bnt.utilisateur_discord_id=%s;"
            cur.execute(requete, (utilisateur.id,))
            
            #Le retour de cette fonction est un tuple de tuple. tue moi svp
            tupleRaw = cur.fetchall()

            listeRetour = []

            for elem in tupleRaw:
                listeRetour.append(elem[0])
            
            return listeRetour
    
    def reqTousAbonnesParListe(self, listeNotifTags: list) -> list:
            with self.connectionBD.cursor(cursor=pymysql.cursors.Cursor) as cur:
                #Requête formatée pour prendre en compte un liste de longueur variable.
                requete = "SELECT DISTINCT ant.utilisateur_discord_id FROM abonnement_notiftag ant WHERE"
                requete += ((len(listeNotifTags)-1) * " ant.nomTag=%s OR") + " ant.nomTag=%s" + ";" 
                cur.execute(requete, tuple(listeNotifTags))

                #Le retour de cette fonction est un tuple de tuple. tue moi svp
                tupleRaw = cur.fetchall()

                listeRetour = []

                for elem in tupleRaw:
                    listeRetour.append(elem[0])
                
                return listeRetour
