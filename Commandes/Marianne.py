import discord
from discord.ext import commands
from gtts import gTTS
from Fonctions import Erreur

class Marianne(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def join(self, ctx):
        """Permet à Marianne de rejoindre le salon vocal de l'utilisateur."""
        salon = ctx.message.author.voice.channel

        #L'utilisateur n'est pas dans un salon vocal.
        if salon == None:
            return await ctx.send("You have to be in a voice channel for me to join you.")
        
        #Connection au salon.
        return await salon.connect()

    #@commands.command()
    #async def say(self, ctx, *, message):
    #    """Permet à Marianne de parler dans un salon vocal."""
    #    guilde = ctx.message.guild       
    #    clientVoix = guilde.voice_client
    #    
    #    #Marianne n'est pas dans un salon.
    #    if clientVoix == None:
    #        return await ctx.send("You have to tell me which voice channel to join. Just use 'm/join', I'll join the one you go to.")
    #
    #    voix = gTTS(message)
    #    voix.save('./MarianneVoix.mp3')
    #
    #    await clientVoix.play(discord.FFmpegPCMAudio("./MarianneVoix.mp3", executable="./ffmpeg/bin/ffmpeg.exe"))
    
    @commands.command()
    async def ping(self, ctx):
        """Commande pour tester le temps de réponse de Marianne.

        Args:
            ctx: Contexte de la commande.

        Returns:
            Marianne doit retourner Pong!/Ping! dans le salon du contexte de la commande.
        """
        return await ctx.send("Pong!")
    
    @commands.command(hidden=True)
    async def pong(self, ctx):
        return await ctx.send("Ping!")

    @commands.command()
    async def leave(self, ctx):
        """Permet à Marianne de quitter le salon de voix.

        Args:
            ctx: Contexte de la commande.

        Returns:
            Marianne quitte le salon.
        """
        clientVoix = ctx.guild.voice_client
        try:
            await clientVoix.disconnect()
        except AttributeError:
            return await ctx.send("I'm not currently in a voice channel. So...")


    async def cog_command_error(self, ctx, error):
        """Gère tous les exceptions non-attrapées."""
        return await Erreur.gestionnaire_erreur(ctx, error)