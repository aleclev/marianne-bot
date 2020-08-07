"""Contient des fonctions pour enregistrer
certaines données des utilisateurs.
"""

import discord
import steam
import requests
from Fonctions import Temps
from discord.ext import commands
from pymysql import cursors
from Fonctions import Message

class Enregistrement(commands.Cog):
    def __init__(self, client, connectionBD, config):
        self.client = client
        self.connectionBD = connectionBD
        self.config = config

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
            with self.connectionBD.cursor(cursor=cursors.Cursor) as cur:
                #Vérification que l'utilisateur est enregistré sur Discord.
                requete = "SELECT EXISTS(SELECT * FROM utilisateur WHERE discord_id=%s);"
                cur.execute(requete, ctx.message.author.id)
                #L'utilisateur n'est pas enregistré sur Discord.
                if cur.fetchone()[0] == 0:
                    return await ctx.send("You have to register in Discord first. You can do that by typing 'm/register discord'.")
                #L'utilisateur est enregistré. On l'emmène vers le site web avec plus d'information.
                else:
                    await ctx.send("Alright, I'm gonna send you a private message with more info.")
                    await Message.envoyerMessagePrive(ctx.message.author, "Here's what you'll need to do:\n"
                                                                            "1 - Go to: https://aleclev.pythonanywhere.com/\n"
                                                                            "2 - Follow the link to log into your steam account.\n"
                                                                            "3 - After you log in, you will see an authentication code. Copy that code.\n"
                                                                            "4 - Finally come back here and type 'm/register steam Code'. Replace 'Code' with the code you got after you logged in. Example: 'm/register steam abcdefghij'\n"
                                                                            "**It's important you don't share your authentication code.\n Codes expire after 10 minutes for security.**")
    
    @commands.command()
    async def whoami(self, ctx):
        with self.connectionBD.cursor(cursor=cursors.Cursor) as cur:
            requete = "SELECT U.steam_id FROM utilisateur U WHERE U.discord_id=%s;"
            cur.execute(requete, ctx.message.author.id)
            res = cur.fetchone()
            if res is None:
                return await ctx.send("Steam profile is not registered.")
            else:
                steamID = res[0]
                res = requests.get("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/", params={"key": self.config["cleSteam"], "steamids": steamID})
                if res.ok:
                    nomSteam = res.json()["response"]["players"][0]["personaname"]
                    return await ctx.send(f"steamID: {steamID}\nSteam name: {nomSteam}")
                else:
                    return await ctx.send("Request for data was refused by steam.")

    async def cog_command_error(self, ctx, error):
        """Gère tous les exceptions non-attrapées."""
        print(error)
        return await ctx.send("I caught an exception in my program. I wasn't able to do your command. Sorry.")