"""
Implémentation de l'engrenage de développement. 
Cette engrenage contient des commandes pour tester les fonctionnalités du bot.
Les commandes de ce module devrait être accessibles seulement pour le propriétaire du bot.
"""

import discord
import random
import json
import datetime
import time
from discord.ext import commands, tasks
from Classes import MarianneException as MarianneException
from Fonctions import Erreur

class Dev(commands.Cog):
    """
    Engrenage pour développement. 
    Contient des commandes et des fonctions de tests.
    """
    def __init__(self, client, config, reddit, clientDest, connectionBD):
        """
        Initialisation. On passe le client et le fichier config.
        """
        self.client = client
        self.config = config
        self.reddit = reddit
        self.clientDest = clientDest
        self.connectionBD = connectionBD

    @commands.command(hidden=True)
    @commands.is_owner()
    async def hello(self, ctx):
        """Dire bonjour."""
        return await ctx.send("hello world!")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def req_tous_engr(self, ctx):
        """Retourne le nom des engrenages."""
        return await ctx.send(self.client.get_cog)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def lever_marianne_exception(self, ctx):
        """Test d'exception. L'exeption doit être attrapée par cog_command_error()"""
        raise MarianneException.MarianneException

    @commands.command(hidden=True)
    @commands.is_owner()
    async def attraper_exception(self, ctx):
        """Test d'exception. L'exception doit être attrapée dans cette fonction (non par cog_command_error())"""
        try:
            raise MarianneException.MarianneException
        except MarianneException.MarianneException:
            #Retour attendu
            return await ctx.send("L'exception a été attrapée.")
        except:
            pass
        #Retour non-attendu
        return await ctx.send("L'exeption n'a pas été attrapée.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reddit_test(self, ctx):
        """Test du client reddit.

        Args:
            ctx: Contexte de la commande.

        Returns:
            Retourne un post de animemes aléatoire.
        """
        listePosts = self.reddit.subreddit("AniMemes").hot(limit=10)
        for post in listePosts:
            return await ctx.send(post.url)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def test_retour_pydest(self, ctx):
        res = await self.clientDest.api.get_profile(3, 76561198177596658, [1000])
        return await ctx.send(res)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def req_tous_commandes(self, ctx):
        """Retourne la liste de tous les commandes.

        Args:
            ctx: Le contexte de la commande.

        Returns:
            Un message avec la liste des commandes.
        """
        messageAide = "```"
        
        for commande in self.client.walk_commands():
            messageAide += commande.qualified_name + " " + commande.signature + "\n"    

        messageAide += "```"
        
        return await ctx.send(messageAide)
    
    @commands.command(hidden=True)
    @commands.is_owner()
    async def generer_doc_json(self, ctx, fichier: str = "./Documentation/MarianneDocEN.json"):
        """Permet de générer ou mettre à jour la documentation dans un format JSON.

        Args:
            ctx: Le ctx de la commande.
            fichier (str): Le fichier dans lequel mettre la documentation.
        """
        try:
            with open(fichier, 'r') as f:
                docJsonCourante = json.load(f)
            with open(fichier+".backup", "w") as f:
                json.dump(docJsonCourante, f, indent=4)
        except:
            print("Le fichier demandé n'existe pas.")
            #Format général du fichier Json
            docJsonCourante = {
                "description": "",
                "prefix": self.client.command_prefix,
                "modules": {}
            }
        
        messageModifs = f"Modifications dans: {fichier}\nTemps de modification: {str(datetime.datetime.now())}\n"

        #On défini les clés manquantes
        for section in ["description", "prefix", "modules"]:
            if section not in docJsonCourante:
                messageModifs += f"Ajout de section: {section}\n"
                docJsonCourante[section] = {}

        #Dictionnaire: {cogNom: cog}
        cogDict = self.client.cogs

        for cogNom in cogDict:
            print(cogNom)
            #On ajoute le nom du cog au besoin
            if cogNom not in docJsonCourante["modules"]:
                messageModifs += f"Ajout de cog: {cogNom}\n"
                docJsonCourante["modules"][cogNom] = {"nomModule":"", "descriptionModule": "", "commandes": {}}
            
            for commande in cogDict[cogNom].walk_commands():
                #Pas besoin de documenter les méthodes cachés.
                if commande.hidden:
                    continue

                #Au besoin on génère une entré formatté.
                if commande.qualified_name not in docJsonCourante["modules"][cogNom]["commandes"]:
                    messageModifs += f"{cogNom}: Ajout de commande: {commande.qualified_name}\n"
                    docJsonCourante["modules"][cogNom]["commandes"][commande.qualified_name] = {"description": "", "utilisation": "", "arguments": {}}
                    argumentsStr = commande.signature
                    argumentsListe = argumentsStr.split()

                    #On génère une entré pour chaque arguments
                    for argument in argumentsListe:
                        docJsonCourante["modules"][cogNom]["commandes"][commande.qualified_name]["arguments"][argument] = ""
        
        with open(fichier, "w") as f:
            json.dump(docJsonCourante, f, indent=4)

        with open(f"Documentation/logs/{str(int(time.time()))}.txt", "x") as f:
            f.write(messageModifs)
        
        return await ctx.send("Fin de la commande.")

    
    @commands.command(hidden=True)
    @commands.is_owner()
    async def verifier_integrite_doc(self, ctx, fichier: str = "./Documentation/MarianneDocEN.json"):
        """Permet d'afficher les erreurs quant à la précision de la documentation json.

        Args:
            ctx: Contexte de la commande.
            fichier (str, optional): Endroit relatif du fichier. Defaults to "./Documentation/MarianneDocEN.json".

        Returns:
            Affiche les erreurs trouvés.
        """
        try:
            with open(fichier, 'r') as f:
                docJsonCourante = json.load(f)
        except:
            return print("Le fichier demandé n'existe pas.")

        #La liste affichera tous les messages d'avertissements.
        listeAvertissement = []

        #Partie 1: Vérification que l'implémentation est documenté entièrement:
        #Dictionnaire: {cogNom: cog}
        cogDict = self.client.cogs

        for cogNom in cogDict:
            if cogNom not in docJsonCourante["modules"]:
                listeAvertissement.append(f"Cog manquants: {cogNom}")
                continue
            else:
                for commande in cogDict[cogNom].walk_commands():
                    #Si la commande est privée on la passe.
                    if commande.hidden:
                        continue

                    #Si la commande manque.
                    if commande.qualified_name not in docJsonCourante["modules"][cogNom]["commandes"]:
                        listeAvertissement.append(f"{cogNom}: Commande manquante: {commande.qualified_name}")
                    else:
                        #S'il y'a un argument de trop.
                        if len(commande.signature.split()) != len(docJsonCourante["modules"][cogNom]["commandes"][commande.qualified_name]["arguments"]):
                            listeAvertissement.append(f"{cogNom}: Nombre d'arguments incorrect pour la commande: {commande.qualified_name}")
        
        #Partie 2: Vérification que la documentation correspond à l'implémantation.
        for cogNom in docJsonCourante["modules"]:
            #Vérification que le cog de la documentation existes.
            if cogNom not in cogDict:
                listeAvertissement.append("Cog documenté non présent dans l'implémantation: {cogNom}")
            else:
                commandeCogNom = ""
                #Vérification que tous les commandes du cog dans la documentation existes.
                for commandeDoc in docJsonCourante["modules"][cogNom]["commandes"]:
                    print(f"#{commandeDoc}")
                    for commande in cogDict[cogNom].walk_commands():
                        commandeCogNom = commande.qualified_name
                        if commandeCogNom == commandeDoc:
                            break
                    
                    #En temps normal cette vérification se fait directement après le break.
                    if commandeCogNom != commandeDoc:
                        listeAvertissement.append(f"{cogNom}: Commande documentée non présente dans l'implémantation: {commandeDoc}")
        
        #On formate un message pour afficher les erreurs dans discord.
        message = "```"
        for avert in listeAvertissement:
            message += avert + "\n"
        message += "```"
        print(message)
        return await ctx.send(message)
    
    @commands.command(hidde=True)
    @commands.is_owner()
    async def reinit_bd_conn(self, ctx):
        """Ferme puis réouvre la connexion mysql.

        Args:
            ctx: Le contexte de la commande.

        Returns:
            Message de réussite.
        """
        tempsDebut = time.time()
        self.connectionBD.close()
        self.connectionBD.ping(reconnect=True)
        tempsFin = time.time()
        return await ctx.send(f"Connexion réinitialiser en {tempsFin - tempsDebut}!")
    
    @commands.command(hidden=True)
    @commands.is_owner()
    async def fermer_bd_conn(self, ctx):
        """Ferme la connexion mysql.

        Args:
            ctx: Contexte de la commande.

        Returns:
            Message de réussite.
        """
        tempsDebut = time.time()
        self.connectionBD.close()
        tempsFin = time.time()
        return await ctx.send(f"Connexion fermer en {tempsFin - tempsDebut}!")
    
    @commands.command(hidden=True)
    @commands.is_owner()
    async def ouvrir_bd_conn(self, ctx):
        """Ouvre la connexion mysql (si fermée)

        Args:
            ctx: Contexte de la commande.

        Returns:
            Message de réussite.
        """
        tempsDebut = time.time()
        self.connectionBD.ping(reconnect=True)
        tempsFin = time.time()
        return await ctx.send(f"Connexion réouverte en {tempsFin - tempsDebut}!")
    
    @commands.command(hidden=True)
    @commands.is_owner()
    async def cogDict(self, ctx):
        """Imprime l'engrenage courant en dictionnaire.

        Args:
            ctx: Le contexte de la commande.

        Returns:
            Imprime...
        """
        return print(self.__dict__)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def lever_attributeError(self, ctx):
        raise AttributeError

    async def cog_command_error(self, ctx, error):
        """Gère tous les exceptions non-attrapées."""
        return await Erreur.gestionnaire_erreur(ctx, error)