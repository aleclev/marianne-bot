"""
Contient des fonctions pour gèrer les erreurs.
"""

import discord
from discord.ext import commands
from Classes import MarianneException
import pymysql

serveurAideURL = "https://discord.gg/fsW94cN"

async def gestionnaire_erreur(ctx: discord.ext.commands.Context, erreur: discord.ext.commands.CommandError):
    """Gestionnaire d'erreurs dans les commandes. Retourne des messages appropriés.

    Args:
        ctx (discord.ext.commands.Context): Contexte de la commande.
        erreur (discord.ext.commands.CommandError): Exception levé.
    """
    try:
        #Affiche les informations de l'exception dans la console. 
        try:
            print("Erreur originale", erreur.original)
        except:
            pass
        print("Erreur", type(erreur))

        #Liste blanche de commandes. Les commandes suivantes ne retourne aucun messages d'erreurs.
        if ctx.command:
            listeNomCommandes = ['react_above']
            print(ctx.command.qualified_name)
            if ctx.command.qualified_name in listeNomCommandes:
                return await ctx.message.channel.delete_messages([ctx.message])

        #Erreurs levées par les commandes.
        if isinstance(erreur, commands.CommandError):
            if isinstance(erreur, commands.errors.BadArgument):
                return await ctx.send("**Exception caught!** The provided argument(s) are invalid.")

            if isinstance(erreur, commands.errors.MissingRequiredArgument):
                return await ctx.send("**Exception caught!** The command is missing required argument(s).")
            
            if isinstance(erreur, commands.errors.CheckFailure):
                return await ctx.send("**Exception caught!** Unauthorized access to command.")
            
            if isinstance(erreur, commands.errors.CommandNotFound):
                return await ctx.send("**Exception caught!** Unknown command.")

        #Erreurs externe à la librairie discord.
        if hasattr(erreur, "original"):
            #Erreur de Python
            if isinstance(erreur.original, AttributeError):
                return await ctx.send(f"**Exception caught!** Please report this exception to the help server. ```{serveurAideURL}```")
            
            if isinstance(erreur.original, TypeError):
                return await ctx.send("**Exception caught!** This is usually the result of an argument being the wrong type. For instance, typing letters where a number should be.")
            
            #Erreurs de Marianne.
            if isinstance(erreur.original, MarianneException.NonEnregDiscord):
                return await ctx.send("**Exception caught!** You must be registered with me on Discord to use this command. Simply type: 'm/register discord'.")
            
            if isinstance(erreur.original, MarianneException.NonEnregSteam):
                return await ctx.send("**Exception caught!** You must be registered with me on Steam to use this command. Use the following commands: 'm/register discord' and 'm/register steam'.")
            
            if isinstance(erreur.original, MarianneException.MauvaiseEntree):
                return await ctx.send("**Exception caught!** Bad entry.")
            
            if isinstance(erreur.original, MarianneException.PermissionsDiscordManquante):
                return await ctx.send(f"**Exception Caught**! I need the following permission(s) for this command: {erreur.original.permission}.")
        
            #Erreur de MYSQL
            if isinstance(erreur.original, pymysql.Error):
                print("Erreur MYSQL")
                #errno
                print(erreur.original.args[0])

                #Duplicate entry
                if (erreur.original.args[0] == 1062):
                    return await ctx.send(f"**Exception Caught**! Database entry already exists. Entry cannot be written.")
        
        #Type d'erreurs non gèrées
        return await ctx.send(f"**Exception caught!** This exception is not handled. Please report it to the help server. ```{serveurAideURL}```")
    
    #Si le gestionnaire d'erreur attrape un exception.
    except Exception as e:
        print(f"EXCEPTION DANS LE GESTIONNAIRE D'ERREUR: {e}")
        return await ctx.send(f"**Exception caught in error handler!** Please report this to the help server. ```{serveurAideURL}```")
