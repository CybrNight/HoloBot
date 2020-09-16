import asyncio

import discord
from discord.ext import commands

from bot.reference import *

class Roles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                role = discord.utils.get(guild.roles, id=755660727305633813)
                if role is not None:
                    await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = discord.utils.get(member.guild.roles, id=755660727305633813)
        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        role = discord.utils.get(user.guild.roles, id=755660727305633813)
        channel = reaction.message.channel
        print(channel.id)
        if channel.id == 755830287182725282:
            if reaction.emoji == "👍":
                await user.add_roles(role)

def setup(bot):
    bot.add_cog(Roles(bot))