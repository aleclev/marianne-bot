import discord
import requests
import aiohttp
from Classes import MarianneException
from pymysql import cursors
from Fonctions import Erreur
from discord.ext import commands
from Classes.GestionnaireResources import GestionnaireResources

class Steam(commands.Cog):
    def __init__(self, gestRes : GestionnaireResources):
        self.client = gestRes.client
        self.connectionBD = gestRes.connectionBD
        self.config = gestRes.config
        self.clientDest = gestRes.clientDest
    
    @commands.group(aliases=["st"])
    async def steam(self, ctx):
        return
    
    #TODO: Ajouter l'endroit courant de la personne dans le jeux. (Si possible sans ralentir considérablement la commande)
    #TODO: Optimiser la commande steam joinme
    @steam.command(aliases=["j"])
    async def joinme(self, ctx):
        """Permet à l'utilisateur de générer un invitation steam de format: '/join [steamID]'.
        L'utilisateur doit être enregistré.

        Args:
            ctx: Le contexte de la commande.
        """
        with self.connectionBD.cursor(cursors.Cursor) as cur:
            requete = "SELECT steam_id FROM utilisateur WHERE discord_id=%s;"
            cur.execute(requete, ctx.message.author.id)

            #On doit confirmer le résultat avant de prendre le steamID
            #Resultat devient None si le tuple n'existe pas. (None,) si le tuple existe mais steam_id est NULL.
            resultat = cur.fetchone()

            if resultat == None or resultat == (None,):
                raise MarianneException.NonEnregSteam

            #L'utilisateur est enregistré, on retourne le message formatté.
            else:
                #steamID est dans un tuple.
                steamID = resultat[0]

                #Ouverture d'une session pour faire des requêtes.
                async with aiohttp.ClientSession() as session:
                    #Requête du nom steam de la personne.   
                    async with session.get("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/", params={"key": self.config["cleSteam"], "steamids": steamID}) as res:
                        if res.status == 200:
                            resJson = await res.json()
                            
                            try:
                                nomSteam = resJson["response"]["players"][0]["personaname"]
                            
                            #Attrape un exception où la réponse de steam est mal formatée
                            except KeyError:
                                nomSteam = "ERROR IN FETCHING STEAM NAME"

                            #Attrape un exception où players ne contient rien (Le steamID est invalide)
                            except IndexError:
                                nomSteam = "ERROR IN FETCHING STEAM NAME"
                        else:
                            nomSteam = "ERROR IN FETCHING STEAM NAME"
                        
                        #La commande est coupée ici. Le reste n'est pas utilisé puisque les autres requêtes prennent trops de temps.
                        return await ctx.send(f"Join code of: {ctx.message.author.mention}\nSteam name: **{nomSteam}**\n```/join {steamID}```") 
                    
                    #Requête du BungieID de la personne.
                    async with session.get(f"https://www.bungie.net/Platform/User/GetMembershipFromHardLinkedCredential/12/{steamID}/", headers={"X-API-Key": self.config["cleDestiny"]}) as res:
                        if res.status == 200:
                            resJs = await res.json()
                            bungieID = resJs["Response"]["membershipId"]
                    
                    #Requête de l'état de l'escouade de la personne.
                    async with session.get(f"https://www.bungie.net/Platform/Destiny2/3/Profile/{bungieID}/", params={"components": "204,1000"}, headers={"X-API-Key": self.config["cleDestiny"]}) as res:
                        if res.status == 200:
                            #Pour obtenir le code de capacité à joindre.
                            resJs = await res.json()
                            #Au cas ou la réponse est mauvaise
                            try:
                                codeConfigPrive = resJs["Response"]["profileTransitoryData"]["data"]["joinability"]["privacySetting"]
                                positionsOuvertes = resJs["Response"]["profileTransitoryData"]["data"]["joinability"]["openSlots"]
                            except KeyError:
                                print("Erreur")
                                codeConfigPrive = 0
                                positionsOuvertes = 0

                            #Message d'erreur approprié
                            if codeConfigPrive == 0:
                                messageErreurEscouade = ""
                            else:
                                messageErreurEscouade = "**WARNING: FIRETEAM PRIVACY IS NOT PUBLIC! CERTAIN PLAYERS MAY BE UNABLE TO JOIN!**\n"
                            
                            #Pour obtenir l'activité courante de la personne
                            try:
                                for charID in resJs["Response"]["characterActivities"]["data"]:
                                    #On trouve un personnage actif.
                                    if resJs["Response"]["characterActivities"]["data"][charID]["currentActivityHash"] != 0:
                                        activiteHash = resJs["Response"]["characterActivities"]["data"][charID]["currentActivityHash"]
                                        activiteModeHash = resJs["Response"]["characterActivities"]["data"][charID]["currentActivityModeHash"]

                                        #On décode le hash activiteHash
                                        async with session.get(f"https://www.bungie.net/Platform/Destiny2/Manifest/DestinyActivityDefinition/{activiteHash}/", headers={"X-API-Key": self.config["cleDestiny"]}) as res:
                                            if res.status == 200:
                                                resJs = await res.json()
                                                try:
                                                    activiteNom = resJs["Response"]["displayProperties"]["name"] + ". "
                                                    placeHash = resJs["Response"]["placeHash"]

                                                    #Remplacer si vide.
                                                    if activiteNom == ". ":
                                                        activiteNom = ""

                                                except KeyError:
                                                    activiteNom = ""
                                                    placeHash = 0
                                                
                                                async with session.get(f"https://www.bungie.net/Platform/Destiny2/Manifest/DestinyPlaceDefinition/{placeHash}/", headers={"X-API-Key": self.config["cleDestiny"]}) as res:
                                                    if res.status == 200:
                                                        resJs = await res.json()
                                                        try:
                                                            placeNom = resJs["Response"]["displayProperties"]["name"] + ". "
                                                            
                                                            #Remplacer si vide.
                                                            if placeNom == ". ":
                                                                placeNom = ""

                                                        except KeyError:
                                                            placeNom = ""
                                                    else:
                                                        placeNom = ""
                                            else:
                                                activiteNom = ""
                                                placeNom = ""
                                            
                                            #On décode le hash activiteHash
                                            async with session.get(f"https://www.bungie.net/Platform/Destiny2/Manifest/DestinyActivityModeDefinition/{activiteModeHash}/", headers={"X-API-Key": self.config["cleDestiny"]}) as res:
                                                if res.status == 200:
                                                    resJs = await res.json()
                                                    try:
                                                        activiteModeNom = resJs["Response"]["displayProperties"]["name"] + ". "
                                                        
                                                        #Remplacer si vide.
                                                        if activiteModeNom == ". ":
                                                            activiteModeNom = ""

                                                    except KeyError:
                                                        activiteModeNom = ""
                                                else:
                                                    activiteModeNom = ""
                                        #Break pour éviter de revenir dans le loop pour un autre personnage.
                                        break
                                    
                                    #Définition des variables au cas où les boucles ne retrouves rien.
                                    activiteModeNom = ""
                                    activiteNom = ""
                                    placeNom = ""
                            
                            #Exception pour attraper une erreur de clés dans le for.
                            except KeyError:
                                activiteModeNom = ""
                                activiteNom = ""
                                placeNom = ""

                            #Message décrivant l'endroit
                            if activiteModeNom == "" and activiteNom == "" and placeNom == "":
                                messageEndroit = "Location could not be found."
                            else:
                                messageEndroit = placeNom + activiteNom + activiteModeNom

                    return await ctx.send(f"Join code of: {ctx.message.author.mention}\nSteam name: **{nomSteam}**\nCurrent location: **{messageEndroit}**\nOpen slots: **{positionsOuvertes}**\n```/join {steamID}```\n{messageErreurEscouade}") 
