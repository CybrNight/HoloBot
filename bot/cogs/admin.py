from discord.ext import commands
import asyncio

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, number=5):
        channel = ctx.message.channel
        author = ctx.author

        number = int(number)
        await ctx.channel.purge(limit=number)
        temp = await ctx.send(f"**{author.mention} :white_check_mark: "
                                  f"{number} message(s) Cleared!**")
        print(f"Cleared {number} messages from channel: {channel}")
        await asyncio.sleep(2.5)
        await temp.delete()


def setup(bot):
    bot.add_cog(Admin(bot))