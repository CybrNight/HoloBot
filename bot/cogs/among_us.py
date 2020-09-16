import discord
from discord.ext import commands

class AmongUs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.lobby_list = []

    @commands.Cog.listener()
    async def on_ready(self):
        print("Finding already active lobbies")
        for guild in self.bot.guilds:
            for channel in guild.channels:
                if "Among Us" in channel.name:
                    self.lobby_list.append(channel)
        print("Done!")

    # Creates VC for those in special created role.
    @commands.command()
    @commands.has_permissions(send_messages=True)
    async def create_lobby(self, ctx, lobby_id):
        guild = ctx.guild
        user = ctx.author
        for role in guild.roles:
            if role.name == lobby_id:
                await role.delete()
        role = await guild.create_role(name=lobby_id)
        await user.add_roles(role)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            role: discord.PermissionOverwrite(view_channel=True)
        }

        for lobby in self.lobby_list:
            if lobby.name == f"Among Us{lobby_id}":
                await lobby.delete()
                self.lobby_list.remove(lobby)

        vc = await guild.create_voice_channel(f"Among Us{lobby_id}", user_limit=10, overwrites=overwrites)
        self.lobby_list.append(vc)
        await vc.edit(position=len(guild.voice_channels))

    async def join_lobby(self, lobby_id):
        pass

def setup(bot):
    bot.add_cog(AmongUs(bot))