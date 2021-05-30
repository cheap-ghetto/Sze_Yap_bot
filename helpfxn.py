import discord
from embed import EmbedList
import json

def create_help_embed(prefix: str='+') -> EmbedList:
    embed_list = EmbedList(message_id=None, type_id=7)
    
    with open('help.json', 'r') as f:
        helpdict = json.load(f)
    
    for page in helpdict:
        page = helpdict[page]
        embed = discord.Embed(
            title=page['title'],
            colour=discord.Color.from_rgb(*page['colour']))
        embed.add_field(
            name=page['name'].format(prefix=prefix),
            value=page['value'].format(prefix=prefix))
        embed_list.add_page(embed, [], [], 0)
    return embed_list