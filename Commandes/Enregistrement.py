"""Contient des fonctions pour enregistrer
certaines données des utilisateurs.
"""

import discord
import steam
import requests
from Classes.GestionnaireResources import GestionnaireResources
from Classes import MarianneException
from Fonctions import Temps, Erreur, Message
from discord.ext import commands
from pymysql import cursors

class Enregistrement(commands.Cog):
    def __init__(self, gestRes : GestionnaireResources):
        self.gestRes = gestRes
        self.client = gestRes.client
        self.connectionBD = gestRes.connectionBD
        self.config = gestRes.config

    @commands.group()
    async def register(self, ctx):
        return

    @register.command()
    async def discord(self, ctx):
        """Enregistre le discord_id de l'utilisateur dans la base de données.

        Args:
            ctx : Le contexte de la commande.
        """

        with self.connectionBD.cursor() as cur:
            requete = "INSERT IGNORE INTO utilisateur (discord_id) VALUES (%s);"
            cur.execute(requete, (ctx.message.author.id))

        return await ctx.send("I succesfully registered your discord profile.")
    
    @register.command()
    async def steam(self, ctx, codeAuth: str = ""):
        #Traitement si l'utilisateur a un code d'authorisation.
        if codeAuth != "":
            with self.connectionBD.cursor() as cur:
                requete = "SELECT * FROM requetes WHERE code_auth=%s;"
                cur.execute(requete, codeAuth)
                resultat = cur.fetchone()
                if resultat is None:
                    return await ctx.send("The authentication code is invalid. Make sure you've copied it correctly and fully!")
                
                #Si la requête a expirée.
                if resultat["date"] < Temps.reqTempsUNIX() - 600:
                    return await ctx.send("This authentication code is expired.")
                
            #Ici la requête est valide.
            #On commence par supprimé la requête.
            with self.connectionBD.cursor() as cur:
                requete = "DELETE FROM requetes WHERE code_auth=%s"
                cur.execute(requete, codeAuth)

                #On mets à jour le profil de l'utilisateur.
                requete = "UPDATE utilisateur SET steam_id=%s WHERE discord_id=%s;"
                cur.execute(requete, (resultat["steam_id"], ctx.message.author.id))
            self.connectionBD.commit()
            return await ctx.send("Your steam profile was successfully linked.")


        #Traitement si l'utilisateur n'a pas de code d'authorisation.
        else:
            if not (self.gestRes.verificateurBD.utilisateurEnregDiscord):
                raise MarianneException.NonEnregDiscord
            else:
                await ctx.send("Alright, I'm gonna send you a private message with more info.")
                await Message.envoyerMessagePrive(ctx.message.author, "Here's what you'll need to do:\n"
                                                                        "1 - Go to: https://aleclev.pythonanywhere.com/\n"
                                                                        "2 - Follow the link to log into your steam account.\n"
                                                                        "3 - After you log in, you will see an authentication code. Copy that code.\n"
                                                                        "4 - Finally come back here and type 'm/register steam Code'. Replace 'Code' with the code you got after you logged in. Example: 'm/register steam abcdefghij'\n"
                                                                        "**It's important you don't share your authentication code.\n Codes expire after 10 minutes for security.**")
    
    #TODO: Commande ci-dessous
    #@register.commands()
    #async def timezone(self, ctx):
    #    """Devra permettre à l'utilisateur d'enregistrer son fuseau horaire dans un dialog.
    #    L'utilisateur peut alors formatter un message pour 
    #
    #    Args:
    #        ctx ([type]): [description]
    #    """
    #    return
    
    @commands.command()
    async def whoami(self, ctx):
        with self.connectionBD.cursor() as cur:
            requete = "SELECT * FROM utilisateur U WHERE U.discord_id=%s;"
            cur.execute(requete, ctx.message.author.id)
            res = cur.fetchone()
            if res is None:
                return await ctx.send("Your Discord account is not registered.")
            else:
                print(res)
                return await ctx.send("The following is a list of ids you've registered with me. Ids are public and serve only to identify you.\n"
                                        f"```Discord profile id: {res['discord_id']}\n"
                                        f"Steam profile id: {res['steam_id']}\n```")
