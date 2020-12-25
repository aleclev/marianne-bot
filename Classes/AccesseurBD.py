"""
Interface pour effectuer des requêtes à la base de données.
"""
import pymysql
import discord
import aiohttp
import json
from Fonctions import Temps

class AcesseurBD():
    def __init__(self, connectionBD : pymysql.Connection, config : dict):
        self.connectionBD = connectionBD
        self.config = config
    
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
        """[summary]

        Args:
            listeNotifTags (list): Retourne la liste des abonnées distinct tel que l'abonnée a au moins un des tags dans listeNotifTag.

        Returns:
            list: Liste des utilisateurs
        """
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

    def enregUtilisateurBungie(self, id_bungie: int, id_discord: int):
        """Permet d'enregistrer le id_bungie de l'utilisateur avec id_discord

        Args:
            id_bungie (int): id_bungie obtenue de bungie.net
            id_discord (int): id_discord de la personne enregistré.
        """
        with self.connectionBD.cursor() as cur:
            requete = "UPDATE utilisateur SET bungie_id=%s WHERE discord_id=%s;"
            cur.execute(requete, (id_bungie, id_discord))
    
    async def reqIDBungieHTTP(self, utilisateur : discord.User) -> int:
        """Demande le bungie_id de la personne par requête http à bungie.net

        Args:
            utilisateur (discord.User): l'utilisateur (doît être enregistré sur steam)

        Returns:
            int: le id_bungie
        """
        steamID = self.reqUtilisateurDict(utilisateur.id)["steam_id"]
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.bungie.net/Platform/User/GetMembershipFromHardLinkedCredential/12/{steamID}/", headers={"X-API-Key": self.config["cleDestiny"]}) as res:
                resJson = await res.json()
                print(resJson)
                id = resJson["Response"]["membershipId"]
                return id
    
    def reqIDBungie(self, utilisateur: discord.User) -> int:
        """Retourne le bungie_id de l'utilisateur si enregistré dans la bd.

        Args:
            utilisateur (discord.User): l'utilisateur

        Returns:
            int: l'id de bungie.
        """
        with self.connectionBD.cursor() as cur:
            requete = "SELECT bungie_id FROM utilisateur WHERE discord_id=%s;"
            cur.execute(requete, (utilisateur.id,))
            return cur.fetchone()["bungie_id"]
    
    async def reqTousRolesReqComplActiv(self) -> list:
        """Retourne la liste complète des role_req_compl_activ

        Returns:
            list: La liste en question.
        """
        with self.connectionBD.cursor() as cur:
            #Requête formatée pour prendre en compte un liste de longueur variable.
            requete = "SELECT * FROM role_req_compl_activ;"
            cur.execute(requete)
            return cur.fetchall()

    async def reqListeIDPersonnagesDest(self, bungieID : int) -> list:
        """retourne l'id des personnages de l'utilisateur avec l'id bungieID (membership_id, bungie.net)

        Args:
            bungieID (int): membership_id

        Returns:
            list: liste d'id (int)
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.bungie.net/Platform/Destiny2/3/Profile/{bungieID}/", params={"components": "204"}, headers={"X-API-Key": self.config["cleDestiny"]}) as resCharId:
                resCharIdJson = await resCharId.json()
                
        characterIds = []

        for entree in resCharIdJson["Response"]["characterActivities"]["data"]:
            characterIds.append(entree)
        
        return characterIds
            

    async def reqTousRolesReqComplActivAcess(self, utilisateur : discord.User) -> list:
        """La liste des rôles tel que l'utilisateur y'a accès.

        Args:
            utilisateur (discord.User): L'utilisateur en question.

        Returns:
            list: [description]
        """
        #Requête formatée pour prendre en compte un liste de longueur variable.
        listeRoles = await self.reqTousRolesReqComplActiv()

        #Première requête pour le bungieID
        bungieID = self.reqIDBungie(utilisateur)

        async with aiohttp.ClientSession() as session:
            characterIds = await self.reqListeIDPersonnagesDest(bungieID)

            DonnesPerso = []
                        
            for id in characterIds:
                async with session.get(f"https://www.bungie.net/Platform/Destiny2/3/Account/{bungieID}/Character/{id}/Stats/AggregateActivityStats/", headers={"X-API-Key": self.config["cleDestiny"]}) as res:
                    resJson = await res.json()
                    DonnesPerso.append(resJson)

        #Liste qui sera retourné à la fin.
        listeRetour = []

        for role in listeRoles:
            #Total des complétions pour l'activité solicitée
            compltot = 0
            for perso in DonnesPerso:
                for activ in perso["Response"]["activities"]:
                    if activ["activityHash"] in self.reqListeHashParIdRaid(role["id_raid"]):
                        compltot += activ["values"]["activityCompletions"]["basic"]["value"]
            
            if compltot >= role["compl_min"]:
                listeRetour.append(role)

        return listeRetour
    
    async def reqDonneesPersonnage(self, id_bungie: int, listeIDPersonnage: list) -> list:
        """Retourne la liste des donnees de complétions d'activité des personnages dans listeIDPeronnage

        Args:
            id_bungie (int): l'id de bungie de la personne
            listeIDPersonnage (list): la liste des ids de personnages

        Returns:
            list: la liste de donnees
        """
        async with aiohttp.ClientSession() as session:
            #liste des id des personnages
            characterIds = await self.reqListeIDPersonnagesDest(id_bungie)

            DonnesPerso = []
            for id in characterIds:
                async with session.get(f"https://www.bungie.net/Platform/Destiny2/3/Account/{id_bungie}/Character/{id}/Stats/AggregateActivityStats/", headers={"X-API-Key": self.config["cleDestiny"]}) as res:
                    resJson = await res.json()
                    DonnesPerso.append(resJson)
            return DonnesPerso

    def reqListeHashParIdRaid(self, id_raid: int) -> tuple:
        """Retourne tous les hash associés au raid/activité avec id.

        Args:
            id_raid (int): l'id du raid/activité

        Returns:
            tuple: la liste en question.
        """
        with self.connectionBD.cursor(cursor=pymysql.cursors.Cursor) as cur:
            requete = "SELECT DISTINCT hash_activ FROM raid_vers_hash WHERE id_raid=%s;"
            cur.execute(requete, (id_raid,))
            liste = cur.fetchall()
        
        listeR = []
        for hashTuple in liste:
            listeR.append(hashTuple[0])
        
        return listeR 
    
    def compterCompletions(self, listeDonneesPerso: list, listeHash: list):
        """[summary]

        Args:
            listeDonneesPerso (list): liste des données de personnages (req)
            listeHash (list): La liste des hashs

        Returns:
            int: Le nombre de complétions dans tous les hash
        """
        compltot = 0
        for perso in listeDonneesPerso:
            for activ in perso["Response"]["activities"]:
                if activ["activityHash"] in listeHash:
                    compltot += activ["values"]["activityCompletions"]["basic"]["value"]
        return compltot


    def getTousActivInfo(self):
        """Retourne tous les champs de activite_info

        Returns:
            dict: les champs de activite_info
        """
        with self.connectionBD.cursor() as cur:
            requete = "SELECT * FROM activite_info;"
            cur.execute(requete)
            return cur.fetchall()
    
    async def reqCompletionsActivID(self, utilisateur: discord.User, id_raid: int) -> int:
        """Retourne le nombre de complétion que l'utilisateur a dans l'activité avec id.

        Args:
            utilisateur (discord.User): l'utilisateur
            id_raid (int): le id

        Returns:
            int: [description]
        """
        id_bungie = self.reqIDBungie(utilisateur)
        listePersoID = await self.reqListeIDPersonnagesDest(id_bungie)
        listeHashActivTuple = self.reqListeHashParIdRaid(id_raid)
        listeHashActiv = []

        for entree in listeHashActivTuple:
            listeHashActiv.append(entree[0])

        listeDonneesPerso = await self.reqDonneesPersonnage(id_bungie, listePersoID)
        
        return self.compterCompletions(listeDonneesPerso, listeHashActiv)

    async def _peuplerraid_vers_hash(self):
        with open("C:/Users/alecl/Desktop/scratch/m.json", "r") as f:
            resJson = json.load(f)

        defJson = resJson["DestinyActivityDefinition"]

        async def getByName(name: str):
            listeHash = []
            for hash in defJson:
                try:
                    if name in defJson[hash]["displayProperties"]["name"]:
                        listeHash.append(int(hash))
                except:
                    continue
            return listeHash
        
        listeNomRaidNormal = [
            #"Leviathan",
            #"Eater of Worlds",
            #"Spire of Stars",
            #"Last Wish",
            #"Scourge of the Past",
            "Crown of Sorrow"
            #"Garden of Salvation",
            #"Deep Stone Crypt"
            ]

        with self.connectionBD.cursor() as cur:
            #Requête formatée pour prendre en compte un liste de longueur variable.
            requete = "INSERt INTO raid_vers_hash (id_raid, hash_activ, nom_activ) VALUES (%s, %s, %s);"

            id_raid = 0

            for raid in listeNomRaidNormal:
                listeHash = await getByName(raid)
                for hash in listeHash:
                    try:
                        cur.execute(requete, (id_raid, hash, raid))
                    except:
                        print("Erreur pour la combinaison:", raid, hash, id_raid)
                id_raid += 1
        return
