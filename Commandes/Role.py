import discord
import random
from Fonctions import Erreur, Message, Permissions
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
        if not ctx.guild.me.guild_permissions.administrator:
            raise MarianneException.PermissionsDiscordManquante("Administrator")
    
    #TODO: Empêcher de modifier un rôle plus haut que le top_role du client
    @role.command()
    @commands.has_permissions(administrator=True)
    async def remove_from_all(self, ctx, *, role: discord.Role):
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
        messageAvert = (f"**WARNING**\n" +
        f"You are about to **remove** the following role from **every member** of this server:\n" +
        f"Role Name: {role.name}\n" +
        f"Role ID: {role.id}\n" +
        f"**THIS ACTION IS IRREVERSIBLE**\n" +
        f"\nTo execute this command, please confirm by entering the following authorisation code: **{codeAuth}**")
        
        #Demande à l'utilisateur de confirmer la commande.
        res = await Message.demanderEntree(ctx, self.client, None, messageAvert, 60, False, False)

        #Vérification du code d'authorisation.
        if res != codeAuth:
            raise MarianneException.MauvaiseEntree()
        else:
            #On enlève les roles
            await ctx.send("Authorisation code accepted. Beginning task...")

            for membre in role.members:
                await membre.remove_roles(role)
            
            #Fin de la tâche
            return await ctx.send("Task finished.")
    
    @role.command()
    @commands.has_permissions(administrator=True)
    async def give_to_all(self, ctx, *, role: discord.Role):
        """Permet de donner un rôle à tous les membres du serveur.

        Args:
            ctx: Contexte de la commande.
            role (discord.Role): Le rôle à ajouter.
        
        Raises:
            MarianneException.MauvaiseEntree: Confirmation invalide.
        """
        #Génération du code d'authorisation.
        codeAuth = "".join([str(elem) for elem in random.choices([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], k=3)])
        
        messageAvert = (f"**WARNING**\n" +
        f"You are about to **give** the following role to **every member** of the server:\n" +
        f"Role Name: {role.name}\n" +
        f"Role ID: {role.id}" +
        f"**THIS ACTION IS IRREVERSIBLE**\n" +
        f"To execute this command, please confirm by entering the following authorisation code: **{codeAuth}**")

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
        
        messageAvert = (f"**WARNING**\n" +
        f"Every member with the role **{roleComp.name}** (id={roleComp.id}) will be **given** the role **{roleCible.name}** (id={roleCible.id}).\n" +
        f"**THIS ACTION IS IRREVERSIBLE**\n" +
        f"To execute this command, please confirm by entering the following authorisation code: **{codeAuth}**")
        
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
        
        messageAvert = (f"**WARNING**\n" +
        f"Every member with the role **{roleComp.name}** (id={roleComp.id}) will be **removed** from the role **{roleCible.name}** (id={roleCible.id}).\n" +
        f"**THIS ACTION IS IRREVERSIBLE**\n" +
        f"To execute this command, please confirm by entering the following authorisation code: **{codeAuth}**")

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
    
    @role.command()
    @commands.has_permissions(administrator=True)
    async def update_permissions_of_all(self, ctx, permValeur: int):
        """Change les permissions de tous les rôles à permValeur.

        Args:
            ctx ([type]): [description]
            permValeur (int): Valeur des permissions à soustraire.
            role (discord.Role): Rôle à modifier.
        """
        #Génération du code d'authorisation + message avertissement.
        codeAuth = "".join([str(elem) for elem in random.choices([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], k=3)])

        #La liste des rôles au dessus du rôle à modifier (incluant le rôle à modifier)
        maxRole = ctx.guild.me.top_role
        listeRolesInaccessibles = [maxRole]

        #Ce message est affiché à l'utilisateur pour lister les rôles qui ne pourronts pas être modifiés.
        listeRolesInaccessiblesMessage = f"{maxRole.name} ({maxRole.id})\n"

        #Analyse des rôles qui ne pourront pas être modifiés.
        for role in ctx.guild.roles:
            if role.position > maxRole.position:
                listeRolesInaccessiblesMessage += f"{role.name} ({role.id})\n"
                listeRolesInaccessibles.append(role)
        
        messageAvert = (f"**WARNING**\n" +
        f"The permission value of every role will be set to: {permValeur}\n" +
        f"**THE FOLLOWING ROLES WILL NOT BE AFFECTED:**\n" +
        f"```{listeRolesInaccessiblesMessage}```\n" +
        f"**THIS ACTION CANNOT BE REVERSED**\n" +
        f"To execute this command, please confirm by entering the following authorisation code: **{codeAuth}**")
        
        #Demande à l'utilisateur de confirmer la commande.
        res = await Message.demanderEntree(ctx, self.client, None, messageAvert, 60, False, False)

        if res != codeAuth:
            raise MarianneException.MauvaiseEntree()
        else:
            #Traitement de la commande.
            await ctx.send("Authorisation code accepted. Beginning task...")

            #Changement des permissions.
            for role in ctx.guild.roles:
                if role not in listeRolesInaccessibles:
                    await role.edit(permissions=discord.Permissions(permissions=permValeur))
            return await ctx.send("Task finished.")
    
    @role.command(hidden=True)
    @commands.has_permissions(administrator=True)
    @commands.is_owner()
    async def remove_permissions_from_all(self, ctx, permValeur: int):
        """Soustrait les permissions de valeurPerm de tous les rôles.

        Args:
            ctx ([type]): [description]
            permValeur (int): Valeur des permissions à soustraire.
            role (discord.Role): Rôle à modifier.
        """
        #Génération du code d'authorisation + message avertissement.
        codeAuth = "".join([str(elem) for elem in random.choices([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], k=3)])

        #La liste des rôles au dessus du rôle à modifier (incluant le rôle à modifier)
        maxRole = ctx.guild.me.top_role
        listeRolesInaccessibles = [maxRole]

        #Ce message est affiché à l'utilisateur pour lister les rôles qui ne pourronts pas être modifiés.
        listeRolesInaccessiblesMessage = f"{maxRole.name} ({maxRole.id})\n"

        #Analyse des rôles qui ne pourront pas être modifiés.
        for role in ctx.guild.roles:
            if role.position > maxRole.position:
                listeRolesInaccessiblesMessage += f"{role.name} ({role.id})\n"
                listeRolesInaccessibles.append(role)
        
        messageAvert = (f"**WARNING**\n Every role will lose the permissions associated with the following permission value: {permValeur}\n" +
        f"**THE FOLLOWING ROLES WILL NOT BE AFFECTED:**\n```{listeRolesInaccessiblesMessage}```\n" +
        f"**THIS ACTION CANNOT BE REVERSED**\nTo execute this command, please confirm by entering the following authorisation code: **{codeAuth}**")
        
        #Demande à l'utilisateur de confirmer la commande.
        res = await Message.demanderEntree(ctx, self.client, None, messageAvert, 60, False, False)

        if res != codeAuth:
            raise MarianneException.MauvaiseEntree()
        else:
            #Traitement de la commande.
            await ctx.send("Authorisation code accepted. Beginning task...")

            #Changement des permissions.
            for role in ctx.guild.roles:
                if role not in listeRolesInaccessibles:
                    rolePermValeur = role.permissions.value
                    await role.edit(permissions=discord.Permissions(permissions=Permissions.soustraire_permissions(rolePermValeur, permValeur)))
            return await ctx.send("Task finished.")

    @role.command(hidden=True)
    @commands.has_permissions(administrator=True)
    @commands.is_owner()
    async def give_permissions_to_all(self, ctx, permValeur: int):
        """Additionne les permissions de valeurPerm de à tous les rôles.

        Args:
            ctx: Contexte de la commande.
            permValeur (int): Valeur des permissions à additionner.
        """
        #Génération du code d'authorisation + message avertissement.
        codeAuth = "".join([str(elem) for elem in random.choices([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], k=3)])

        #La liste des rôles au dessus du rôle à modifier (incluant le rôle à modifier)
        maxRole = ctx.guild.me.top_role
        listeRolesInaccessibles = [maxRole]

        #Ce message est affiché à l'utilisateur pour lister les rôles qui ne pourronts pas être modifiés.
        listeRolesInaccessiblesMessage = f"{maxRole.name} ({maxRole.id})\n"

        #Analyse des rôles qui ne pourront pas être modifiés.
        for role in ctx.guild.roles:
            if role.position > maxRole.position:
                listeRolesInaccessiblesMessage += f"{role.name} ({role.id})\n"
                listeRolesInaccessibles.append(role)
        
        messageAvert = (f"**WARNING**\n Every role will be given the permissions associated with the following permission value: {permValeur}\n" +
        f"**THE FOLLOWING ROLES WILL NOT BE AFFECTED:**\n```{listeRolesInaccessiblesMessage}```\n" +
        f"**THIS ACTION CANNOT BE REVERSED**\nTo execute this command, please confirm by entering the following authorisation code: **{codeAuth}**")
        
        #Demande à l'utilisateur de confirmer la commande.
        res = await Message.demanderEntree(ctx, self.client, None, messageAvert, 60, False, False)

        if res != codeAuth:
            raise MarianneException.MauvaiseEntree()
        else:
            #Traitement de la commande.
            await ctx.send("Authorisation code accepted. Beginning task...")

            #Changement des permissions.
            for role in ctx.guild.roles:
                if role not in listeRolesInaccessibles:
                    rolePermValeur = role.permissions.value
                    await role.edit(permissions=discord.Permissions(permissions=Permissions.additioner_permissions(rolePermValeur, permValeur)))
            return await ctx.send("Task finished.")

    async def cog_command_error(self, ctx, error):
        """Gère tous les exceptions non-attrapées."""
        return await Erreur.gestionnaire_erreur(ctx, error)