import discord
from discord.ext import commands
from asyncio import sleep as asleep

from bot.reference import *


class Lobby:

    def __init__(self, id, channel, host):
        self.id = id
        self.channel = channel
        self.host = host
        self.player_list = []

    def add_player(self, player):
        self.player_list.append(player)

    def remove_player(self, player):
        self.player_list.remove(player)

class AmongUs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.lobby_list = []

    @commands.Cog.listener()
    async def on_ready(self):
        print("Deleting active lobbies!")
        for guild in self.bot.guilds:
            for channel in guild.channels:
                if LOBBY_ROOT in channel.name:
                    role = discord.utils.get(guild.roles, name=channel.name[-4:])
                    if role is not None:
                        await role.delete()
                    await channel.delete()
        print("Done!")

    # Creates VC for those in special created role.
    @commands.command()
    async def create_lobby(self, ctx, lobby_id):
        guild = ctx.guild
        user = ctx.author
        for role in guild.roles:
            if role.name == lobby_id:
                await role.delete()
                print(f"Deleted Role:{role.name}")
        role = await guild.create_role(name=lobby_id)
        await user.add_roles(role)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            role: discord.PermissionOverwrite(view_channel=True)
        }

        for lobby in self.lobby_list:
            if lobby.channel.name == f"{LOBBY_ROOT}{lobby_id}":
                await lobby.channel.delete()
                self.lobby_list.remove(lobby)

        vc = await guild.create_voice_channel(f"{LOBBY_ROOT}{lobby_id}", user_limit=10, overwrites=overwrites)
        new_lobby = Lobby(lobby_id, vc, ctx.author)
        self.lobby_list.append(new_lobby)
        await self.join_lobby(ctx, lobby_id)
        await vc.edit(position=len(guild.voice_channels))

    @commands.command()
    async def join_lobby(self, ctx, lobby_id):
        in_lobby = False
        for lobby in self.lobby_list:
            if ctx.message.author in lobby.player_list:
                if lobby.id != lobby_id:
                    await self.leave_lobby(ctx, lobby.id)
                else:
                    in_lobby = True

        if in_lobby:
            msg = await ctx.send("**You are already in this lobby**")
            await asleep(2)
            await msg.delete()
            return

        joined = False
        user = ctx.message.author
        for lobby in self.lobby_list:
            if lobby.channel.name == f"{LOBBY_ROOT}{lobby_id}":
                role = discord.utils.get(user.guild.roles, name=lobby_id)
                lobby.add_player(user)
                await user.add_roles(role)
                joined = True

        if not joined:
            msg = await ctx.send("**There are no lobbies with that ID**")
            await asleep(1)
            await msg.delete()
        else:
            msg = await ctx.send(f"**{user.mention} joined {lobby_id}."
                                 f" Connect to the voice channel at top of channel list!**")
            await asleep(2.5)
            await msg.delete()

    @commands.command()
    async def leave_lobby(self, ctx, lobby_id):
        user = ctx.message.author
        role = discord.utils.get(user.guild.roles, name=lobby_id)
        await user.remove_roles(role)

        for lobby in self.lobby_list:
            if lobby.id == lobby_id:
                lobby.remove_player(user)
                if len(lobby.player_list) == 0:
                    await self.delete_lobby(ctx, lobby_id)

    @commands.command()
    async def delete_lobby(self, ctx, lobby_id):
        user = ctx.message.author
        for lobby in self.lobby_list:
            if lobby.id == lobby_id and ctx.message.author == lobby.host:
                self.lobby_list.remove(lobby)
                await lobby.channel.delete()

                role = discord.utils.get(user.guild.roles, name=lobby_id)
                if role is not None:
                    await role.delete()
                else:
                    msg = await ctx.send("**There are no lobbies with that ID**")
                    await asleep(1)
                    await msg.delete()
            else:
                msg = await ctx.send(f"**{ctx.message.author.mention} Only the host of a lobby can use this command.**")
                await asleep(1)
                await msg.delete()

    @commands.command()
    async def list_lobbies(self, ctx):
        message = ""
        embed_list = discord.Embed(title=f"**Current Active Among Us Lobbies: {len(self.lobby_list)}**",
                                   description="\u200b")
        if len(self.lobby_list) > 0:
            i = 1
            for lobby in self.lobby_list:
                embed_list.add_field(name=f"{i}. Join Code:{lobby.id}\nHost:{lobby.host.name}",
                                     value=f"Players: {len(lobby.player_list)}/10\n",
                                     inline=False)
                i += 1
            embed_list.add_field(name="Join with /join_lobby <join-code>",value="\u200b")
            await ctx.send(embed=embed_list)
        else:
            message = "**No Active Lobbies**"
            await ctx.send(message)


def setup(bot):
    bot.add_cog(AmongUs(bot))