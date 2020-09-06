import random
import json
import discord
from Fonctions import Erreur
from discord.ext import commands

class Util(commands.Cog):
    def __init__(self, client, config=None):
        self.client = client

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
            await ctx.send("```" + docJson["commandeAideUtilisation"] + "```")
            message = "```"
            for cogNom in docJson["modules"]:
                message += docJson["modules"][cogNom]["nomModule"] + ":\n" + docJson["modules"][cogNom]["descriptionModule"] + "\n\n"
            message += "```"
            return await ctx.send(message)
        
        #On envoi le nom de tous les commandes dans le module si le module existe.
        if commande == "":
            for cogNom in docJson["modules"]:
                if docJson["modules"][cogNom]["nomModule"] == module:
                    message = "```"
                    for commandeNom in docJson["modules"][cogNom]["commandes"]:
                        message += commandeNom + "\n"
                    message += "```"
                    return await ctx.send(message)
            return await ctx.send("Requested module was not found")
        
        #Si les deux paramètres sont présent on envoi les information de la commande si elle existe.
        for cogNom in docJson["modules"]:
            if docJson["modules"][cogNom]["nomModule"] == module:
                try:
                    commandeJson = docJson["modules"][cogNom]["commandes"][commande]
                    #La commande ou le module n'existe pas
                except KeyError:
                    return await ctx.send(f"Command {commande} does not exist in module {module}.")
                
                message = "```"
                message += commande + "\n\n"
                message += "Description: " + commandeJson["description"] + "\n\n"
                message += "Arguments:\n"
                for argument in commandeJson["arguments"]:
                    message += argument + ": " + commandeJson["arguments"][argument] + "\n"
                message += "```"
                return await ctx.send(message)
            return await ctx.send(f"Module {module} does not exist.")
    
    @commands.command()
    async def rng(self, ctx, limiteBas: int, limiteHaut: int):
        """Retourne un nombre aléatoire entre deux nombres.

        Args:
            ctx: Le contexte de la commande.
            limiteBas (int): Le nombre minimal.
            limiteHaut (int): Le nombre maximal.

        Returns:
            Retourne le nombre aléatoire dans le contexte.
        """
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

    async def cog_command_error(self, ctx, error):
        """Gère tous les exceptions non-attrapées."""
        return await Erreur.gestionnaire_erreur(ctx, error)