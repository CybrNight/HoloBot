import asyncio

import discord
from discord.ext import commands

from bot.reference import *

class Roles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot;

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = discord.utils.get(member.guild.roles, id=755660727305633813)
        await member.add_roles(role)

def setup(bot):
    bot.add_cog(Roles(bot))