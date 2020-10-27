import asyncio
import discord
from Classes.GestionnaireResources import GestionnaireResources
from discord.ext import commands

class MessagesFonctions(commands.Cog):
    def __init__(self, gestRes : GestionnaireResources):
        self.gestRes = gestRes
        self.client = gestRes.client
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Envoi un avertissement si le message supprimé contient une mention global.

        Args:
            message (Discord.message): Le message supprimé.

        Returns:
            Un message au besoin.
        """
        if message.mention_everyone:
            return await message.channel.send(f"**DETECTED DELETED MESSAGE WITH EVERYONE/HERE MENTION**\n**Author:** {message.author.mention}\n**Content:** ```{message.content}```\nMany people agree that deleting messages with mentions in them is not boss. Be careful.")


async def demanderEntree(ctx: discord.ext.commands.Context, client: discord.Client, verification=None, messageEnvoye="An input is required...", 
                                    timeout=60, supprimerMessagesBot=True, supprimerMessageUtilisateur=True) -> str:
    """Meta fonction pour demander à un utilisateur Discord une entrée dans un salon.

    Args:
        ctx (discord.ext.commands.Context): Contexte de la commande.
        client (discord.Client): Le client discord courant.
        verification (Fonction, optional): Fonction de vérification pour savoir quels messages écouter. Defaults to None.
        messageEnvoye (str, optional): Message à envoyer avant de demander l'entrée. Defaults to "An input is required...".
        timeout (int, optional): Nombre de secondes avant que la demande soit annulée. Defaults to 60.
        supprimerMessagesBot (bool, optional): Si le message du bot devrait être supprimé. Defaults to True.
        supprimerMessageUtilisateur (bool, optional): Si le message . Defaults to True.

    Returns:
        str: [description]
    """
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