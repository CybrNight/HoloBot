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
        await self.bot.change_presence(
            activity=discord.Game("Under Maintenance -_-"))

        for guild in self.bot.guilds:
            if guild.id == 755658743957684256:
                print(guild.members)

                for role in guild.roles:
                    self.role_list.append(role)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = discord.utils.get(member.guild.roles, id=755660727305633813)
        await member.add_roles(role)

    @commands.command(name="hololive", aliases=['holo'])
    async def hololive(self, ctx, role_name):
        role_name = role_name.replace('"', '')
        for role in self.role_list:
            for approved in self.approved_list:
                if role_name.lower() in role.name.lower() and role_name.lower() \
                        in approved.lower():

                    try:
                        if role in ctx.author.roles:
                            await ctx.author.remove_roles(role)
                            msg = await ctx.send(f"**I have stripped "
                                                 f"{role.name} from "
                                                 f"{ctx.author.mention}**")
                            await asleep(3.5)
                            await msg.delete()
                            return
                        else:
                            await ctx.author.add_roles(role)
                            msg = await ctx.send(f"**I have bestowed "
                                                 f"{ctx.author.mention} with "
                                                 f"{role.name}**")
                            await asleep(3.5)
                            await msg.delete()
                            return
                    except Exception as e:
                        print(e)
                        msg = await ctx.send(f"**{ctx.author.mention} There is "
                                           f"no "
                                       f"role with that name**")
                        await asleep(3.5)
                        await msg.delete()
                        return


def setup(bot):
    bot.add_cog(Roles(bot))
