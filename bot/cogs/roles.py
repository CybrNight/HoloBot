import asyncio
from os import getcwd
from asyncio import sleep as asleep

import discord
from discord.ext import commands

from bot.reference import *


class Roles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.role_list = []
        self.approved_list = []

        with open(getcwd()+'/roles.txt') as f:
            self.approved_list = f.readlines()

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            if guild.id == 755658743957684256:
                for role in guild.roles:
                    self.role_list.append(role)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = discord.utils.get(member.guild.roles, id=755660727305633813)
        await member.add_roles(role)

    @commands.command(name="hololive", aliases=['holo'])
    async def hololive(self, ctx, role_name):
        role_name = role_name.replace('"','')
        for role in self.role_list:
            for approved in self.approved_list:
                if role_name in role.name and role_name in approved:
                    if role in ctx.author.roles:
                        await ctx.author.remove_roles(role)
                        msg = await ctx.send(f"**I have bestowed {ctx.author.mention} with {role.mention}**")
                        await asleep(3.5)
                        await msg.delete()
                    else:
                        await ctx.author.add_roles(role)
                        msg = await ctx.send(f"**I have stripped {role.mention} from {ctx.author.mention}**")
                        await asleep(3.5)
                        await msg.delete()

def setup(bot):
    bot.add_cog(Roles(bot))
