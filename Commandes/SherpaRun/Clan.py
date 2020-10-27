"""
L'utilisateur peut envoyer une demande d'acceptation par la commande 'm/clan apply [clanNom] [*message]'.
L'application ne peut être envoyée que si l'applicant est enregistré sur steam avec Marianne.

Marianne notifie l'équipe de recrutement dans le bon salon.

Le message de Marianne contient un lien direct vers le profile bungie de l'applicant, ainsi que le message envoyé par l'applicant.

La demande est ajouté à la base de données.
Deux réactions sont ajoutés au message de Marianne. Une pour accepter l'application, l'autre pour la refuser.
Réagir au message envoi un message de notification à l'applicant.
"""
import discord
from discord.ext import commands
from Fonctions import Message
from Classes import VerificateurBD, MarianneException
from Classes.GestionnaireResources import GestionnaireResources

#TODO: Fonctions de vérifications pour la bd.
class Clan(commands.Cog):
    def __init__(self, gestRes : GestionnaireResources):
        self.gestRes = gestRes
    
    @commands.command()
    async def get_all_clan(self, ctx : commands.Context):
        """Retourne une liste formatée des clans et leurs sigle.

        Args:
            ctx (commands.Context): Le contexte de la commande.
        """
        return await ctx.send(self.gestRes.accesseurBD.reqListeClansFormatee())
    
    @commands.group()
    async def clan(self, ctx : commands.Context):
        pass

    @clan.command()
    async def apply(self, ctx : commands.Context, sigleClan : str = "", *, messageApplication : str = ""):
        """Permet à un utilisateur d'envoyer une demande de joindre un clan.

        Args:
            ctx (commands.Context): Le contexte de la commande.
            sigleClan (str, optional): le sigle du clan que l'utilisateur veut joindre. Defaults to "".
            messageApplication (str, optional): Le message que l'utilisateur . Defaults to "".

        Raises:
            commands.MissingRequiredArgument: [description]
            MarianneException.NonEnregSteam: [description]
            MarianneException.ErreurBD: [description]

        Returns:
            [type]: [description]
        """
        #Préconditions à l'utilisation.
        #Arguments manquants
        if sigleClan == "" or messageApplication == "":
            raise commands.MissingRequiredArgument
        
        #Non enregistré sur steam.
        if not self.gestRes.verificateurBD.utilisateurEnregSteam(ctx.message.author):
            raise MarianneException.NonEnregSteam()

        #Sigle inexistant
        if not self.gestRes.verificateurBD.sigleClanExiste(sigleClan):
            return await ctx.send("The provided clan tag does not exist. For a list of available clans and their tags, use: 'm/get_all_clans'.")

        #Confirmation de l'utilisateur. Le message de confirmation est envoyé
        #Demande du dictionnaire du tuple du clan et création de l'embed qui contient les informations de l'application.
        clanDict = self.gestRes.accesseurBD.reqClanDict(sigleClan)
        embed = discord.Embed(title="Clan Application Review", description="Review your clan application before sending it.")
        embed.add_field(name="Clan", value=clanDict["nom"], inline=False)
        embed.add_field(name="Why do you want to join this clan?", value=messageApplication, inline=False)
        await ctx.send(embed=embed)

        #L'utilisateur doit confirmer.
        res = await Message.demanderEntree(ctx, self.gestRes.client, None, "Do you wish to send this clan application? (y/n)", 60, False, False)
        if res != "y":
            return await ctx.send("Clan application cancelled. You can try again at any time.")
        
        #Ajout de l'application à la bd.
        self.gestRes.accesseurBD.ajtApplicationClan(ctx.message.author, sigleClan, messageApplication)

        #Envoy du message de notification.
        await self.envNotifApplicationClan(ctx.message.author, clanDict, messageApplication)

        #Message de complétion/confirmation.
        return await ctx.send(f"Application was successfully delivered. Keep an eye on your bungie.net notifications for a potential clan invite.")

    async def envNotifApplicationClan(self, utilisateur : discord.User, clanDict : dict, message : str):
        """Envoi un message de notification dans le salon de recrutement du clan selon clanDict.

        Args:
            utilisateur (discord.User): L'utilisateur ayant envoyé une demande.
            clanDict (dict): L'entrée mysql du clan dans la base de données.
            message (str): Le message envoyé avec l'application. 
        """
        #Demande du salon de recrutement du clan.
        salonRecrutement = self.gestRes.client.get_channel(clanDict["salon_recrutement"])

        #Demande du tuple de l'utilisateur.
        utilisateurDict = self.gestRes.accesseurBD.reqUtilisateurDict(utilisateur.id)

        #Demande du id de bungie de l'utilisateur.
        resBungieId = self.gestRes.sessionReq.get(f"https://www.bungie.net/Platform/User/GetMembershipFromHardLinkedCredential/12/{utilisateurDict['steam_id']}/", headers={"X-API-Key": "ddc2f6cc7bc842a1a2e55a207dc1e1cb"})
        bungie_id = resBungieId.json()["Response"]["membershipId"]

        #Création du embed.
        embed = discord.Embed(title="New Recrutement Entry", description="Received new entry")

        #Info sur le profile discord.
        embed.add_field(name="Discord Profile", value=utilisateur.mention)

        #Info sur le profile steam.
        embed.add_field(name="Steam Profile", value=f"https://steamcommunity.com/profiles/{utilisateurDict['steam_id']}")

        #Profile bungie
        embed.add_field(name="Bungie Profile", value=f"https://www.bungie.net/en/Profile/3/{bungie_id}")

        #Raid.report
        embed.add_field(name="Raid Report", value=f"https://raid.report/pc/{bungie_id}")

        #Message d'application de l'utilisateur.
        embed.add_field(name="Message", value=message)

        return await salonRecrutement.send(embed=embed)
