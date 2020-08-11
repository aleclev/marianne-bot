"""
Implémantation du module Tag.
"""

import discord
from discord.ext import commands
import random
import pymysql
import asyncio
from pymysql import cursors
from Classes import MarianneException
from Fonctions import Message

class Tag(commands.Cog):
    def __init__(self, client, connectionBD):
        self.client = client
        self.connectionBD = connectionBD
    
    @commands.group()
    async def tag(self, ctx):
        """Groupe de commande tag. Ce groupe de commande
        permet à l'utilisateur de définir un mot clé avec
        un certain texte. Le texte peut être récupéré avec
        le mot clé."""
        return

    @tag.command()
    async def set(self, ctx, p_tagNom: str = "", *, p_tagText: str = ""):
        """Permet à l'utilisateur de sauvegarder un tag.

        Args:
            ctx (): Le contexte.
            p_tagNom (str): Le nom du tag.
            p_tagText (str): Le texte du tag.
        """

        #Paramètres manquants.
        if p_tagNom == "" or p_tagText == "":
            return await ctx.send("Missing parameters. You have to give me a tag name and a text to remember. e.g. 'm/tag set joke a really funny joke'...")

        with self.connectionBD.cursor(cursors.Cursor) as cur:
            #Vérification si le tag existe déjà.
            requete = "SELECT EXISTS(SELECT * FROM tag WHERE tag.utilisateur_discord_id=%s AND tag.tag_nom=%s);"
            cur.execute(requete, (ctx.message.author.id, p_tagNom))
        
            #Le tag n'existe pas. Aucun traitement spécial.
            if cur.fetchone()[0] == 0:
                requete = "INSERT INTO tag VALUES (%s, %s, %s);"
                cur.execute(requete, (ctx.message.author.id, p_tagNom, p_tagText))
                return await ctx.send(f"Tag was saved successfully. You can get it again with 'm/tag get {p_tagNom}'.")
            
            #La tag existe. L'utilisateur doît choisir s'il veut écraser l'ancien ou ne rien faire.
            else:
                try:
                    choix = await Message.demanderEntree(ctx, self.client, None, f"You've already registered {p_tagNom} as a tag. Should I overwrite the old one? Type (y/n)...")
                except asyncio.TimeoutError:
                    return await ctx.send()
                
                #Actions selon le choix de l'utilisateur.
                if choix == "y":
                    requete = "UPDATE tag SET tag.tag_text=%s WHERE tag.utilisateur_discord_id=%s AND tag.tag_nom=%s;"
                    cur.execute(requete, (p_tagText, ctx.message.author.id, p_tagNom))
                elif choix=="n":
                    return await ctx.send("Alright, I canceled the command.")
                else:
                    return await ctx.send("Invalid input. I canceled the command just to be safe.")
                
        return await ctx.send(f"Tag was successfully saved. You can print the message again with 'm/tag get {p_tagNom}'.")


    @tag.command()
    async def get(self, ctx, tagNom: str):
        """Permet à l'utilisateur de récupéré un tag sauvegarder auparavant.

        Args:
            ctx ([type]): Le contexte de la commande.
            tagNom (str): Le nom du tag demandé.

        Returns:
            Envoi un message avec le tag.
        """
        with self.connectionBD.cursor() as cur:
            #Recherche du tag pertinent.
            requete = "SELECT * FROM tag WHERE tag.tag_nom=%s AND utilisateur_discord_id=%s;"
            cur.execute(requete, (tagNom, ctx.message.author.id))
            resultat = cur.fetchone()
            
            #Le tag n'existe pas.
            if resultat is None:
                return await ctx.send("I couldn't find the tag your requested. You can see a list of your registered tags with 'm/tag mytags'.")
            #Le tag existe.
            else:
                return await ctx.send(f"**{tagNom}:**\n{resultat['tag_text']}")
    
    @tag.command()
    async def mytags(self, ctx):
        """Permet d'afficher la liste des tags enregistrés au nom de l'utilisateur.

        Args:
            ctx: Le contexte de la commande.
        """
        with self.connectionBD.cursor(cursors.Cursor) as cur:
            requete = "SELECT t.tag_nom FROM tag t WHERE t.utilisateur_discord_id=%s ORDER BY t.tag_nom;"
            cur.execute(requete, ctx.message.author.id)
            resultat = cur.fetchall()

            #L'utilisateur n'a pas de tag enregistrés.
            if resultat is None:
                return await ctx.send("You don't have any registered tags.")
            
            #L'utilisateur a des tags enregistrés. On les affiches dans un message formaté.
            else:
                message = f"List of all tags for {ctx.message.author.mention}\n```\n"
                
                #On ajoute le nom des tags.
                for tagNom in resultat:
                    message += f"{tagNom[0]}\n"
                message += "```"
                return await ctx.send(message)
    
    @tag.command(aliases=["del"])
    async def delete(self, ctx, tagNom: str = ""):
        """Permet à l'utilisateur de supprimer un tag enregistré.

        Args:
            ctx: Le contexte de la commande.
            tagNom (str, optional): Nom du tag à supprimer. Defaults to "".

        Returns:
            Si nomTag est valide, le tag sera supprimé.
        """
        if tagNom == "":
            return await ctx.send("You must pass the name of the tag you wish to delete.")
        with self.connectionBD.cursor() as cur:
            requete = "DELETE FROM tag WHERE tag.tag_nom=%s AND tag.utilisateur_discord_id=%s;"
            cur.execute(requete, (tagNom, ctx.message.author.id))
            
            #Avertissement si la requête n'a affectée aucun tuple.
            if cur.rowcount == 0:
                return await ctx.send(f"I couldn't find a tag named {tagNom}")
        return await ctx.send("The tag was successfully deleted.")

    async def cog_command_error(self, ctx, error):
        """Gère tous les exceptions non-attrapées."""
        print(error)
        return await ctx.send("I caught an exception in my program. I wasn't able to do your command. Sorry.")