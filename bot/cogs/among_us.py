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
        self.message = ""

    def add_player(self, player):
        self.player_list.append(player)

    def remove_player(self, player):
        self.player_list.remove(player)

class AmongUs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.lobby_list = []
        self.among_us_role = None

    @commands.command(name="among_us")
    async def among_us_cmd(self, ctx):
        has_role = False
        for role in ctx.message.author.roles:
            if role.id == 755923402941792397:
                has_role = True

        if self.among_us_role is not None and not has_role:
            await ctx.message.author.add_roles(self.among_us_role)
            role_msg = await ctx.send(f"**{ctx.author.mention} You have turned on notifications for Among Us lobbies!**")
            await asleep(2.5)
            await role_msg.delete()
        elif self.among_us_role is not None and has_role:
            await ctx.message.author.remove_roles(self.among_us_role)
            role_msg = await ctx.send(f"**{ctx.author.mention} You have turned off notifications for Among Us lobbies!**")
            await asleep(2.5)
            await role_msg.delete()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Deleting active lobbies!")
        for guild in self.bot.guilds:
            if guild.id == 755658743957684256:
                print("Got role")
                self.among_us_role = discord.utils.get(guild.roles, id=755923402941792397)
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
        await vc.edit(position=len(guild.voice_channels))
        new_lobby.message = await ctx.send(f"**{self.among_us_role.mention} {user.mention} has created an Among Us lobby!"
                       f"\nReact to join or use /join_lobby {lobby_id}**")
        await new_lobby.message.add_reaction('\u2705')
        self.lobby_list.append(new_lobby)
        await self.join_lobby(ctx.author, ctx.message.channel, lobby_id)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user:
            return

        if reaction.emoji == "\u2705":
            for lobby in self.lobby_list:
                if reaction.message.id == lobby.message.id:
                    await self.join_lobby(user, reaction.message.channel, lobby.id)

    async def join_lobby(self, user, channel, lobby_id):
        in_lobby = False
        for lobby in self.lobby_list:
            if user in lobby.player_list:
                if lobby.id != lobby_id:
                    await self.leave_lobby(user, channel, lobby.id)
                else:
                    in_lobby = True

        if in_lobby:
            msg = await channel.send("**You are already in this lobby**")
            await asleep(2)
            await msg.delete()
            return

        joined = False
        joined_lobby = None
        for lobby in self.lobby_list:
            if lobby.channel.name == f"{LOBBY_ROOT}{lobby_id}":
                role = discord.utils.get(user.guild.roles, name=lobby_id)
                lobby.add_player(user)
                await user.add_roles(role)
                joined = True
                joined_lobby = lobby

        if not joined:
            msg = await channel.send("**There are no lobbies with that ID**")
            await asleep(1)
            await msg.delete()
        else:
            if user != joined_lobby.host:
                msg = await channel.send(f"**{user.mention} joined {lobby_id}."
                                     f" Connect to the voice channel at top of channel list!**")
                await asleep(2.5)
                await msg.delete()

    async def leave_lobby(self, user, channel, lobby_id):
        role = discord.utils.get(user.guild.roles, name=lobby_id)
        await user.remove_roles(role)

        for lobby in self.lobby_list:
            if lobby.id == lobby_id:
                lobby.remove_player(user)
                if len(lobby.player_list) == 0:
                    await self.delete_lobby(user, channel, lobby_id)

    async def delete_lobby(self, user, channel, lobby_id):
        for lobby in self.lobby_list:
            if lobby.id == lobby_id and user == lobby.host:
                self.lobby_list.remove(lobby)
                await lobby.channel.delete()

                role = discord.utils.get(user.guild.roles, name=lobby_id)
                if role is not None:
                    await role.delete()
                else:
                    msg = await channel.send("**There are no lobbies with that ID**")
                    await asleep(1)
                    await msg.delete()
            elif lobby.id == lobby_id and user != lobby.host:
                msg = await channel.send(f"**{user.mention} Only the host of a lobby can use this command.**")
                await asleep(2.5)
                await msg.delete()
            else:
                msg = await channel.send(f"**No channel with this ID to delete**")
                await asleep(2.5)
                await msg.delete()

    @commands.command(name="join_lobby")
    async def join_lobby_cmd(self, ctx, lobby_id):
        await self.join_lobby(ctx.message.author, ctx.message.channel, lobby_id)

    @commands.command(name="leave_lobby")
    async def leave_lobby_cmd(self, ctx, lobby_id):
        await self.leave_lobby(ctx.message.author, ctx.message.channel, lobby_id)

    @commands.command(name="delete_lobby")
    async def delete_lobby_cmd(self, ctx, lobby_id):
        await self.delete_lobby(ctx.message.author, ctx.message.channel, lobby_id)

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