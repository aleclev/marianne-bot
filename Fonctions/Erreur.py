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
            if isinstance(erreur.original, AttributeError):
                return await ctx.send("")
            
            if isinstance(erreur.original, MarianneException.NonEnregDiscord):
                return await ctx.send("**Exception caught!** You must be registered with me on Discord to use this command. Simply type: 'm/register discord'.")
            
            if isinstance(erreur.original, MarianneException.NonEnregSteam):
                return await ctx.send("**Exception caught!** You must be registered with me on Steam to use this command. Simply type: 'm/register discord' and 'm/register steam'.")

        elif isinstance(erreur, commands.errors.BadArgument):
            print("hello")
            return await ctx.send("**Exception caught!** The provided arguments are invalid.")
        
        #Type d'erreurs non gèrées
        else:
            return await ctx.send(f"**Exception caught!** This exception is not handled. Please report it to the help server. ```{serveurAideURL}```")
    
    #Si le gestionnaire d'erreur attrape un exception.
    except:
        return await ctx.send("Error handler raised an exception... What?")