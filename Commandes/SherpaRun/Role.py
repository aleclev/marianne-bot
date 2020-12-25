import discord
from discord.ext import commands
from Fonctions import Message
from Classes import VerificateurBD, MarianneException
from Classes.GestionnaireResources import GestionnaireResources

class Role(commands.Cog):
    def __init__(self, gestRes : GestionnaireResources):
        self.gestRes = gestRes

    @commands.group()
    async def sr_role(self, ctx : commands.Context):
        if not self.gestRes.verificateurBD.utilisateurEnregSteam(ctx.message.author):
            raise MarianneException.NonEnregSteam

        if ctx.guild.id != 439563888342859776:
            return await ctx.send("This command cannot be used on this server.")

    @sr_role.command()
    async def choose(self, ctx : commands.Context):
        """Permet à l'utilisateur de choisir un role.

        Args:
            ctx (commands.Context): Le contexte de la commande.
        """
        if not self.gestRes.verificateurBD.utilisateurEnregBungie(ctx.author):
            raise MarianneException.NonEnregBungie()

        async with ctx.channel.typing():
            listeRoles = await self.gestRes.accesseurBD.reqTousRolesReqComplActivAcess(ctx.message.author)

        message = f"You have access to the following roles: {Message.codifierListeIndex(listeRoles)}Enter the number of the role you wish to get..."
        reponse = await Message.demanderEntree(ctx, self.gestRes.client, None, message, 60, False, False)
        
        #Peut lever ValueError
        idx = int(reponse)

        #Peut lever une erreur d'index
        roleid = listeRoles[idx]["id_role"]
        role = ctx.guild.get_role(roleid)

        #enlève tous les roles courant
        await self.enleverTousRoles(ctx.author, ctx.guild)

        await ctx.author.add_roles(role)

        return await ctx.send("Operation successful.")

    @sr_role.command()
    async def view_all(self, ctx : commands.Context):
        pass

    @sr_role.command()
    async def view_access(self, ctx : commands.context):
        listeRoles = await self.gestRes.accesseurBD.reqTousRolesReqComplActivAcess(ctx.message.author)

        msg = ""
        for i in listeRoles:
            msg += str(i) + "\n"

        return await ctx.send(msg)

    async def enleverTousRoles(self, utilisateur : discord.Member, guild : discord.Guild):
        """enlève tous les roles enregistrés de l'utilisateur

        Args:
            utilisateur (discord.Member): L'utilisateur.
            guild (discord.Guild): Le serveur (devrait toujours être SherpaRun)
        """
        listeTousRoles = await self.gestRes.accesseurBD.reqTousRolesReqComplActiv()

        for roleID in listeTousRoles:
            role = guild.get_role(roleID["id_role"])
            
            #s'assure que le role existe.
            if role == None:
                continue
            else:
                await utilisateur.remove_roles(role)