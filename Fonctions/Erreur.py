"""
Contient des fonctions pour gèrer les erreurs.
"""

import discord
from discord.ext import commands
from Classes import MarianneException

serveurAideURL = "https://discord.gg/fsW94cN"

async def gestionnaire_erreur(ctx: discord.ext.commands.Context, erreur: discord.ext.commands.CommandError):
    """Gestionnaire d'erreurs dans les commandes. Retourne des messages appropriés.

    Args:
        ctx (discord.ext.commands.Context): Contexte de la commande.
        erreur (discord.ext.commands.CommandError): Exception levé.
    """
    try:
        print(type(erreur), erreur.__dict__)
        #Erreurs levées par les commandes.
        if isinstance(erreur, commands.CommandError):
            if isinstance(erreur, commands.errors.BadArgument):
                return await ctx.send("**Exception caught!** The provided argument(s) are invalid.")

            if isinstance(erreur, commands.errors.MissingRequiredArgument):
                return await ctx.send("**Exception caught!** The command is missing required argument(s).")

            #Erreurs externe à la librairie discord.
            if hasattr(erreur, "original"):
                if isinstance(erreur.original, AttributeError):
                    return await ctx.send("")
                
                if isinstance(erreur.original, TypeError):
                    return await ctx.send("**Exception caught!** This is usually the result of an argument being the wrong type. For instance, typing letters where a number should be.")
                
                if isinstance(erreur.original, MarianneException.NonEnregDiscord):
                    return await ctx.send("**Exception caught!** You must be registered with me on Discord to use this command. Simply type: 'm/register discord'.")
                
                if isinstance(erreur.original, MarianneException.NonEnregSteam):
                    return await ctx.send("**Exception caught!** You must be registered with me on Steam to use this command. Use the following commands: 'm/register discord' and 'm/register steam'.")
        
        #Type d'erreurs non gèrées
        else:
            return await ctx.send(f"**Exception caught!** This exception is not handled. Please report it to the help server. ```{serveurAideURL}```")
    
    #Si le gestionnaire d'erreur attrape un exception.
    except Exception as e:
        print(e)
        return await ctx.send(f"**Exception caught in error handler!** Please report this to the help server. ```{serveurAideURL}```")