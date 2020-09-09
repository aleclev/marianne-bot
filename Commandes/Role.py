import discord
import random
from Fonctions import Erreur, Message
from Classes import MarianneException
from discord.ext import commands

class Role(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.group()
    async def role(self, ctx):
        """Groupe de commandes pour les commandes dans le module role.
            Aucun traitement spécial.

        Args:
            ctx: Le contexte de la commande.
        """
        return
    
    @role.command()
    @commands.has_permissions(administrator=True)
    async def remove_from_all(self, ctx, role: discord.Role):
        """Retire un rôle de tous les utilisateurs du serveur.

        Args:
            ctx: Contexte de la commande.
            role (discord.Role): Le rôle à retirer.

        Raises:
            MarianneException.MauvaiseEntree: Code d'authorisation invalide.
        """
        #Génère un code d'authorisation aléatoire.
        codeAuth = "".join([str(elem) for elem in random.choices([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], k=3)])
        
        #Affiche un message d'avertissement à l'utilisateur.
        messageAvert = (f"**WARNING**\nYou are about to **remove** the following role from **every member** of this server:\nRole Name: {role.name}\nRole ID: {role.id}\n**THIS ACTION IS IRREVERSIBLE**\n" +
        f"\nTo execute this command, please confirm by entering the following authorisation code: **{codeAuth}**")
        
        #Demande à l'utilisateur de confirmer la commande.
        res = await Message.demanderEntree(ctx, self.client, None, messageAvert, 60, False, False)

        #Vérification du code d'authorisation.
        if res != codeAuth:
            raise MarianneException.MauvaiseEntree()
        else:
            #On enlève les roles
            await ctx.send("Authorisation code accepted. Beginning task...")

            for membre in ctx.guild.members:
                await membre.remove_roles(role)
            
            #Fin de la tâche
            return await ctx.send("Task finished.")
    
    @role.command()
    @commands.has_permissions(administrator=True)
    async def give_to_all(self, ctx, role: discord.Role):
        """Permet de donner un rôle à tous les membres du serveur.

        Args:
            ctx: Contexte de la commande.
            role (discord.Role): Le rôle à ajouter.
        
        Raises:
            MarianneException.MauvaiseEntree: Confirmation invalide.
        """
        #Génération du code d'authorisation.
        codeAuth = "".join([str(elem) for elem in random.choices([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], k=3)])
        
        messageAvert = (f"**WARNING**\nYou are about to **give** the following role to **every member** of the server:\nRole Name: {role.name}\nRole ID: {role.id}" +
        f"**THIS ACTION IS IRREVERSIBLE**\nTo execute this command, please confirm by entering the following authorisation code: **{codeAuth}**")

        #Demande à l'utilisateur de confirmer la commande.
        res = await Message.demanderEntree(ctx, self.client, None, messageAvert, 60, False, False)

        if res != codeAuth:
            raise MarianneException.MauvaiseEntree()
        else:
            #Traitement de la commande.
            await ctx.send("Authorisation code accepted. Beginning task...")

            for membre in ctx.guild.members:
                await membre.add_roles(role)
            
            #Fin de la tâche
            return await ctx.send("Task finished.")
        
    @role.command()
    @commands.has_permissions(administrator=True)
    async def get_count(self, ctx, role: discord.Role):
        """Retourne le nombre d'utilisateurs dans le rôle.

        Args:
            ctx: Le contexte de la commande.
            role (discord.Role): Le rôle à analyser.
        """
        return await ctx.send(f"**{len(role.members)}** members found in role **{role.name}**.")
    
    @role.command()
    @commands.has_permissions(administrator=True)
    async def give_to_all_with_role(self, ctx, roleComp: discord.Role, roleCible: discord.Role):
        """Tous les utilisateurs avec roleComp vont être donnés roleCible

        Args:
            ctx: Le contexte de la commande.
            roleComp (discord.Role): Le rôle que l'utilisateur doit avoir a priori.
            roleCible (discord.Role): Le rôle que l'utilisateur recevra s'il a roleComp.

        Raises:
            discord.ext.commands.BadArgument: Si les deux rôles sont égaux (commande redondante)
            MarianneException.MauvaiseEntree: Si le code d'authorisation est invalide.
        """
        #Précondition
        if roleComp == roleCible:
            raise discord.ext.commands.BadArgument()
        
        #Génération du code d'authorisation + message avertissement.
        codeAuth = "".join([str(elem) for elem in random.choices([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], k=3)])
        
        messageAvert = (f"**WARNING**\nEvery member with the role **{roleComp.name}** (id={roleComp.id}) will be **given** the role **{roleCible.name}** (id={roleCible.id}).\n" +
        f"**THIS ACTION IS IRREVERSIBLE**\nTo execute this command, please confirm by entering the following authorisation code: **{codeAuth}**")
        
        #Demande à l'utilisateur de confirmer la commande.
        res = await Message.demanderEntree(ctx, self.client, None, messageAvert, 60, False, False)

        if res != codeAuth:
            raise MarianneException.MauvaiseEntree()
        else:
            #Traitement de la commande.
            await ctx.send("Authorisation code accepted. Beginning task...")

            for membre in roleComp.members:
                await membre.add_roles(roleCible)

            return await ctx.send("Task finished.")
    
    @role.command()
    @commands.has_permissions(administrator=True)
    async def remove_from_all_with_role(self, ctx, roleComp: discord.Role, roleCible: discord.Role):
        """Tous les membres avec roleComp vont être enlever du rôle roleCible.

        Args:
            ctx: Le contexte de la commande.
            roleComp (discord.Role): Le role que l'utilisateur doit avoir a priori.
            roleCible (discord.Role): Le rôle qui sera enlevé de l'utilisateur.

        Raises:
            discord.ext.commands.BadArgument: Si les deux rôles sont égaux (commande redondante)
            MarianneException.MauvaiseEntree: Si le code d'authorisation est invalide.
        """
        #Précondition
        if roleComp == roleCible:
            raise discord.ext.commands.BadArgument()
        
        #Génération du code d'authorisation + message avertissement.
        codeAuth = "".join([str(elem) for elem in random.choices([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], k=3)])
        
        messageAvert = (f"**WARNING**\nEvery member with the role **{roleComp.name}** (id={roleComp.id}) will be **removed** from the role **{roleCible.name}** (id={roleCible.id}).\n" +
        f"**THIS ACTION IS IRREVERSIBLE**\nTo execute this command, please confirm by entering the following authorisation code: **{codeAuth}**")

        #Demande à l'utilisateur de confirmer la commande.
        res = await Message.demanderEntree(ctx, self.client, None, messageAvert, 60, False, False)

        if res != codeAuth:
            raise MarianneException.MauvaiseEntree()
        else:
            #Traitement de la commande.
            await ctx.send("Authorisation code accepted. Beginning task...")

            for membre in roleComp.members:
                await membre.remove_roles(roleCible)

            return await ctx.send("Task finished.")

    async def cog_command_error(self, ctx, error):
        """Gère tous les exceptions non-attrapées."""
        return await Erreur.gestionnaire_erreur(ctx, error)