import random
import json
import discord
from Fonctions import Erreur
from discord.ext import commands
from Classes.GestionnaireResources import GestionnaireResources

class Util(commands.Cog):
    def __init__(self, gestRes : GestionnaireResources):
        self.client = gestRes.client

    #TODO: Améliorer l'accessibilité  de la commande.
    #TODO: Moyen pour envoyer un message plus long que 2000 caractères.
    @commands.command()
    async def help(self, ctx, module: str = "", *, commande: str = ""):
        """Commande d'aide. Utilise un fichier de documentation JSON: ./Documentation/MarianneDocEN.json

        Args:
            ctx: Contexte de la commande.
            module (str, optional): Nom du module recherché. Defaults to "".
            commande (str, optional): Nom de la commande recherchée. Defaults to "".

        Returns:
            Envoi un message d'aide.
        """
        try:
            with open("./Documentation/MarianneDocEN.json") as f:
                docJson = json.load(f)
        except FileNotFoundError:
            return await ctx.send("I couldn't find the documentation file.")

        #On envoi le nom/description de tous les modules si le nom n'a pas été choisi.
        if module == "":
            idx = 0
            await ctx.send("```" + docJson["commandeAideUtilisation"] + "```")
            message = "```"
            for cogNom in docJson["modules"]:
                message += f"{idx} : " + docJson["modules"][cogNom]["nomModule"] + ":\n" + docJson["modules"][cogNom]["descriptionModule"] + "\n\n"
                idx += 1
            message += "```"
            return await ctx.send(message)
        
        #On envoi le nom de tous les commandes dans le module si le module existe.
        idx = 0 #Index utilisé pour accéder plus facilement aux commandes.

        messageAide = f"```To look up a command in depth you can use the commands name or index (number).\nm/help {module} [idx/name]```\n"

        #Essay de prendre le nom du module par l'index.
        try:
            temp = list(docJson["modules"])[int(module)]
            module = docJson["modules"][temp]["nomModule"]
        except :
            pass

        if commande == "":
            for cogNom in docJson["modules"]:
                if docJson["modules"][cogNom]["nomModule"] == module:
                    message = "```"
                    for commandeNom in docJson["modules"][cogNom]["commandes"]:
                        message += f"{idx} : " + commandeNom + "\n"
                        idx += 1
                    message += "```"
                    return await ctx.send(messageAide + message)
            return await ctx.send("Requested module was not found")
        
        #Si les deux paramètres sont présent on envoi les information de la commande si elle existe.
        for cogNom in docJson["modules"]:
            if docJson["modules"][cogNom]["nomModule"] == module:
                try:
                    commandeJson = docJson["modules"][cogNom]["commandes"][commande]
                    commandeNom = commande
                    #La commande ou le module n'existe pas
                except KeyError:
                    try:
                        commandeNom = list(docJson["modules"][cogNom]["commandes"])[int(commande)]
                        commandeJson = docJson["modules"][cogNom]["commandes"][commandeNom]
                    except:
                        return await ctx.send(f"Command name/index **{commande}** does not exist in module **{module}**.")
                
                message = "```"
                message += "Commande name: " + commandeNom + "\n\n"
                message += "Description: " + commandeJson["description"] + "\n\n"
                message += "Arguments:\n"
                if len(commandeJson["arguments"]) == 0:
                    message += "No arguments.\n"
                for argument in commandeJson["arguments"]:
                    message += argument + ": " + commandeJson["arguments"][argument] + "\n"
                message += "\nUsage: " + commandeJson["utilisation"] + "\n\n"
                message += "```"
                return await ctx.send(message)
        return await ctx.send(f"Module {module} does not exist.")
    
    @commands.command()
    async def rng(self, ctx, limiteBas: int, limiteHaut: int = None):
        """Retourne un nombre aléatoire entre deux nombres.

        Args:
            ctx: Le contexte de la commande.
            limiteBas (int): Le nombre minimal.
            limiteHaut (int): Le nombre maximal.

        Returns:
            Retourne le nombre aléatoire dans le contexte.
        """
        #Valeur par défaut lorsqu'on passe un seul argument.
        if not limiteHaut:
            limiteHaut = limiteBas
            limiteBas = 1
        return await ctx.send(f"How about **{random.randint(limiteBas, limiteHaut)}**?")
    
    @commands.command()
    async def emoji_search(self, ctx, emoji: discord.Emoji):
        return await ctx.send(emoji.url)

    #TODO: Implémantation de cette commande.
    @commands.command(aliases=["ra"])
    async def react_above(self, ctx, emoji: discord.Emoji):
        """Permet de réagir au dernier message du salon.

        Args:
            ctx: Contexte de la commande.
            emoji (discord.Emoji): L'emoji à utiliser.
        """
        async for message in ctx.message.channel.history(limit=2):
            dernierMessage = message
        await dernierMessage.add_reaction(emoji)
        return await ctx.message.channel.delete_messages([ctx.message])
        