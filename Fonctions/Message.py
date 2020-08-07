import asyncio
import discord


async def demanderEntree(ctx: discord.ext.commands.Context, client: discord.Client, verification=None, messageEnvoye="An input is required...", 
                                    timeout=60, supprimerMessagesBot=True, supprimerMessageUtilisateur=True) -> str:
    #Définition de la fonction de vérification si besoin.
    if verification is None:
        #Fonction de base, vérifie que le message provient du même canale et de la même personne.
        def verification(m: discord.Message) -> bool:
            return m.channel == ctx.message.channel and m.author == ctx.message.author
    #Attente d'un message qui satisfait la vérification.
    messageEnvoye = await ctx.send(messageEnvoye)
    messageEntree = await client.wait_for('message', check=verification, timeout=timeout)
    entree = messageEntree.content

    #Supprimer les messages du bot au besoin.
    if supprimerMessagesBot:
        if messageEnvoye:
            await messageEnvoye.delete()

    #Supprimer l'entrée de l'utilisateur au besoin.
    if supprimerMessageUtilisateur:
        await messageEntree.delete()
    
    return entree

async def envoyerMessagePrive(utilisateur: discord.User, message: str):
    """La fonction créer une chaine de message privés au besoin, puis envoie à l'utilisateur le message.

    Args:
        utilisateur (discord.User): L'utilisateur à qui on envoi le message.
        message (str): Le message qu'on envoi.
    """
    if utilisateur.dm_channel == None:
        await utilisateur.create_dm()
    await utilisateur.dm_channel.send(message)