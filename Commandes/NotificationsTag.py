"""
Implémentation du module NotificationsTag.
"""

#TODO: Une commande qui permet de voir les tags enregistrés en ordre de popularité.

import discord
import steam
import requests
import asyncio
from Classes.GestionnaireResources import GestionnaireResources
from Classes import MarianneException
from Fonctions import Message
from Fonctions import Temps, Erreur, Message
from discord.ext import commands
from pymysql import cursors

class NotificationsTag(commands.Cog):
    def __init__(self, gestRes : GestionnaireResources):
        self.gestRes = gestRes

    @commands.group()
    async def notif(self, ctx: commands.Context):
        #Un utilisateur doit être enregitré sur discord pour utiliser les commandes de ce module.
        if not self.gestRes.verificateurBD.utilisateurEnregDiscord(ctx.message.author):
            raise MarianneException.NonEnregDiscord

    @notif.command()
    async def add(self, ctx: commands.Context, tagNom: str):
        self.gestRes.accesseurBD.ajtNotifTag(tagNom, ctx.message.author)
        return await ctx.send("You will now receive a notification when someone mentions this tag. For a list of your registered tags, use: m/notif list_all")
    
    @notif.command()
    async def remove(self, ctx: commands.Context, tagNom):
        self.gestRes.accesseurBD.enlNotifTag(tagNom, ctx.message.author)
        return await ctx.send("You will no longer receive a notification when this tag is mentionned. For a list of your registered tags, use: m/notif list_all")
    
    @notif.command()
    async def list_all(self, ctx: commands.Context):
        listeTagNom = self.gestRes.accesseurBD.reqTousNotifTag(ctx.message.author)
        return await ctx.send("Here is a list of your registered tags:\n" + Message.codifierListe(listeTagNom))

    #TODO: Cette commande doît avoir une vérification.
    @notif.command()
    async def remove_all(self, ctx: commands.Context):
        res = await Message.demanderEntree(ctx, self.gestRes.client, None, "You are about to unsubscribe from all your registered tags. This action is irreverisble. Proceed? (y/n)", 60, False, False)
        if res != "y":
            return await ctx.send("Operation cancelled.")

        self.gestRes.accesseurBD.enlTousNotifTag(ctx.message.author)
        return await ctx.send("Operation successful.")

    @notif.command()
    async def block(self, ctx: commands.Context, utilisateur_id: int):
        #Plusieurs utilisateurs peuvent ne pas être en cache. Regarde d'abord dans la cache puis fait un appel à l'api.
        utilisateur = self.gestRes.client.get_user(utilisateur_id)
        if not utilisateur:
            try:
                utilisateur = await self.gestRes.client.fetch_user(utilisateur_id)
            except:
                pass
            if not utilisateur:
                #L'utilisateur n'existe véritablement pas.
                return await ctx.send(f"**ERROR!** The user with id={utilisateur_id} was not found.")

        if not self.gestRes.verificateurBD.utilisateurEnregDiscord(utilisateur):
            return await ctx.send("**ERROR!** The user you are trying to block is not registered.")
        
        self.gestRes.accesseurBD.ajtLienBloquage(ctx.message.author, utilisateur)
        return await ctx.send("You will no longer receive notifications from this user. To see a list of currently blocked users, use: m/notif blacklist")
    
    @notif.command()
    async def unblock(self, ctx: commands.Context, utilisateur_id: int):
        #Plusieurs utilisateurs peuvent ne pas être en cache. Regarde d'abord dans la cache puis fait un appel à l'api.
        utilisateur = self.gestRes.client.get_user(utilisateur_id)
        if not utilisateur:
            utilisateur = await self.gestRes.client.fetch_user(utilisateur_id)
            if not utilisateur:
                #L'utilisateur n'existe véritablement pas.
                return await ctx.send(f"**ERROR!** The user with id={utilisateur_id} was not found.")

        self.gestRes.accesseurBD.enlLienBloquage(ctx.message.author, utilisateur)
        return await ctx.send("User is now unblocked. Notifications will be sent by private message.")
    
    @notif.command()
    async def blacklist(self, ctx: commands.Context):
        listeNoir = self.gestRes.accesseurBD.reqTousLiensBlocage(ctx.message.author)

        return await ctx.send(Message.codifierListe(listeNoir))
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Fonction pour envoyer une notification à tous les abonnés d'un notiftag lorsqu'il est mentionné.

        Args:
            message (discord.Message): Le message envoyé par l'évenement.
        """
        #Empêcher Marianne de répondre à d'autres bots
        if self.gestRes.config["ignore_notiftag"] == 1:
            return
        
        if message.author.bot:
            return

        if not self.gestRes.verificateurBD.utilisateurEnregDiscord(message.author):
            raise MarianneException.NonEnregDiscord()

        listeTags = Message.reqListeNotifTagDansMessage(message.content)

        #Retour si la liste est vide (aucun tag mentionné)
        if listeTags == []:
            return

        #Tag qui retourne la fonction. Permet d'écrire certains messages sans qu'une notif soit envoyée.
        if "override" in listeTags:
            return

        #Tag ALL qui sera toujours appelé. Permet aux utilisateurs d'être tous le temps notifié.
        listeTags.append("ALL")

        urlMessage = "https://discordapp.com/channels/" + str(message.guild.id) + "/" + str(message.channel.id) + "/" + str(message.id)

        #Retire ALL de la liste.
        listeTags.pop()
        
        listeUtilisateurs_id = self.gestRes.accesseurBD.reqTousAbonnesParListe(listeTags)

        await message.channel.send(f"Found {len(listeUtilisateurs_id)} users in tags:\n{Message.codifierListe(listeTags)}\nSending notifications...")

        if "BLOCK" in listeTags:
            return await message.channel.send("Detected tag BLOCK. Notifications will not be sent.")
        
        #Montre à l'utilisateur que la fonction est toujours en cours de traitement.
        async with message.channel.typing():
            for id in listeUtilisateurs_id:
                try:
                    #permet de ne pas envoyer de message à un utilisateur qui n'est pas sur le serveur courant (member n'existera pas)
                    utilisateur = message.guild.get_member(id)
                    if not utilisateur:
                        utilisateur = await message.guild.fetch_member(id)
                        if not utilisateur:
                            continue
                    
                    #Si l'utilisateur est bloqué on continue.
                    if self.gestRes.verificateurBD.utilisateurEstNotifTagsBloque(utilisateur, message.author):
                        continue

                    #On empêche Marianne d'envoyer un message à l'utilisateur ayant écrit le message.
                    if id == message.author.id:
                        continue

                    #On empêche d'envoyer le message si l'utilisateur est hors ligne.
                    if utilisateur.status == discord.Status.offline:
                        continue

                    embed = discord.Embed(title="Notification Tag Ping", description="One of your registered tags was mentionned.")
                    embed.add_field(name="Sender", value=f"{message.author.display_name}\nid={message.author.id}", inline=True)
                    embed.add_field(name="Message content", value=message.content, inline=True)
                    embed.add_field(name="Message Link", value=urlMessage, inline=True)
                    embed.add_field(name="Tip", value=f"If you no longer wish to receive notifications from this user, you can type: m/notif block {message.author.id}", inline=True)
                    await Message.envoyerMessagePrive(utilisateur, embed=embed)
                except:
                    continue

            await message.channel.send("All notifications sent.")