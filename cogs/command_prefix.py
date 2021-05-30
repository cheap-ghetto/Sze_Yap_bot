from discord.ext import commands
import json
import os

json_path = os.path.join(os.path.dirname(__file__), 'prefixes.json')


class InitializeCommandPrefix(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        with open(json_path, 'r') as f:
            prefixes = json.load(f)
        prefixes[str(guild.id)] = '+'
        with open(json_path, 'w') as f:
            json.dump(prefixes, f, indent=4)
        try:
            await guild.system_channel.send(
                "Thanks for adding me to this server! You can use the command "
                "+help to find out some help commands!")
        except:
            pass

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open(json_path, 'r') as f:
            prefixes = json.load(f)
        prefixes.pop(str(guild.id))
        with open(json_path, 'w') as f:
            json.dump(prefixes, f, indent=4)

    @commands.command(aliases=['changeprefix', 'prefixset', 'prefixchange'])
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, prefix):
        with open(json_path, 'r') as f:
            prefixes = json.load(f)
            prefixes[str(ctx.guild.id)] = prefix
        with open(json_path, 'w') as f:
            json.dump(prefixes, f, indent=4)

        await ctx.send(f'Successfully changed the prefix to: **``{prefix}``**')


def setup(client):
    client.add_cog(InitializeCommandPrefix(client))
