from discord import Color, Embed
from helpfxn import create_help_embed

from cogs.jsonfxn import open_datajson, save_json
import discord
from discord.errors import ClientException, HTTPException
from discord.player import AudioSource, FFmpegPCMAudio
from dotenv import load_dotenv
from discord.ext import commands
import os

from hed import hed_usage, multi_chinese, pinyin, rand_word, simple_chinese, single_chinese, single_multi_search
from embed import change_page, change_selection, add_credit, EmbedList, EmbedPage
import asyncio
import json
from datetime import datetime
import numpy as np
import re
import requests
from pathlib import Path
import pynormalize
import random
from collections import namedtuple
import csv
import pandas as pd
from PyDictionary import PyDictionary
from synonym import synonym
from typing import Union
import codecs

load_dotenv()
token = os.getenv("token")
time_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

cats = ["/ᐠ｡ꞈ｡ᐟ\\", "/ᐠ｡▿｡ᐟ\\*ᵖᵘʳʳ*", "/ᐠ –ꞈ –ᐟ\\",
        "₍⸍⸌̣ʷ̣̫⸍̣⸌₎", "˓˓ฅ₍˄ุ.͡ ̫.˄ุ₎ฅ˒˒", "ก₍⸍⸌̣ʷ̣̫⸍̣⸌₎ค"]
bears = ["ʕ •ᴥ•ʔ", "“φʕ•ᴥ•oʔ", "ʕ/　·ᴥ·ʔ/", "ʕノ•ᴥ•ʔノ ︵ ┻━┻", "＼ʕ •ᴥ•ʔ＼"]
embed_master_list = []
Emoji = namedtuple('Emoji', ["l_arrow", "r_arrow", "sound", "d_arrow",
                             "u_arrow", "books"])
emoji_list = Emoji('⬅️', '➡️', '🔊', '⬇️', '⬆️', '📚')
filepath = os.getcwd()
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
dictionary = PyDictionary()

def add_to_master(embed_list: EmbedList, sent_embed: Embed):
    embed_list.message_id = sent_embed.id
    embed_master_list.append(embed_list)

    if len(embed_master_list) > 50:
        embed_master_list.pop(0)


def command_count(
        command: str="", guild_id: str="", 
        channel: Union[discord.TextChannel, discord.VoiceChannel]=None):
    if channel is None:
        return
    elif isinstance(channel, discord.DMChannel):
        guild_id = "dm"
    else:
        guild_id = str(guild_id)
    channel_id = str(channel.id)
    command_list = ['sl', 'gc', 'leave_channel', 'audio', 'penyim']
    if command not in command_list:
        print("Not in list")
        return
    
    data = open_datajson(
        os.path.join(filepath, 'cogs', 'data.json'), guild_id)
    com_count = data[guild_id]['command_count']
    try:
        if channel_id not in com_count[command]:
            com_count[command][channel_id] = 1
        else:
            com_count[command][channel_id] += 1

    except KeyError:
        return

    data[str(guild_id)]['command_count'] = com_count
    save_json(os.path.join(filepath, 'cogs', 'data.json'), data)


def get_prefix(client, message):
    prefix_path = os.path.join(filepath, 'cogs', 'prefixes.json')
    with open(prefix_path, 'r') as f:
        prefixes = json.load(f)
        if isinstance(message.channel, discord.channel.DMChannel):
            return '+'
        else:
            try:
                return prefixes[str(message.guild.id)]
            except KeyError:
                prefixes[str(message.guild.id)] = '+'
                save_json(prefix_path, prefixes)

client = commands.Bot(
    command_prefix=get_prefix, case_insensitive=True, intents=intents,
    help_command=None)


num_to_tone = {
    "1": "55",
    "2": "33",
    "3": "22",
    "4": "32",
    "5": "21"
}

tone_to_num = {
    '55': '1',
    '33': '2',
    '22': '3',
    '32': '4',
    '21': '5',
}


@client.command()
@commands.has_permissions(administrator=True)
async def adminhelp(ctx):
    text = (
        "```Help commands for admins!!\n\n"
        "setwcmsg [your message]-sets welcome msg for when member joins\n\n"
        "setentitle [your title]-sets title for banner when member joins\n\n"
        "setchtitle [your ch title]-sets ch title below english one\n\n"
        "setwcchannel [#your_channel]-sets the welcome msgs are sent to\n\n"
        "delwcmsg-deletes configured welcome message\n\n"
        "sendwcmsg [true/false or on/off]-turn welcome message on or off\n\n"
        "showpfp [true/false]-toggle showing pfp of member on banner\n\n"
        "hoisanwcpics [true/false]-toggle using pics from Hoisan or random "
        "pictures for the welcome banner\n\n"
        "title_colour [red/green/blue/yellow/white/green/255, 255, 255 <- "
        "This is rgb value] - set text colour for welcome banner```\n")
    embed = Embed(title="Admin-only commands", description=text,
                          colour=Color.from_rgb(232, 194, 58))
    await ctx.send(embed=embed)


@client.command()
async def help(ctx):
    embed_list = create_help_embed(get_prefix(client, ctx.message))
    
    embed_list.curr = 0
    sent_embed = await ctx.send(embed=embed_list.curr_page().content)
    for emoji in emoji_list[:2]:
        await sent_embed.add_reaction(emoji)
    if len(embed_list.curr_page().content.fields) > 2:
        await sent_embed.add_reaction(emoji_list[3])
        await sent_embed.add_reaction(emoji_list[4])

    add_to_master(embed_list, sent_embed)

def add_spaces(search_term):
    if isinstance(search_term, list):
        for index in range(len(search_term)):
            search_term[index] = " " + str(search_term[index]) + " "
        return search_term
    elif isinstance(search_term, str):
        return " " + str(search_term) + " "
    else:
        return search_term


async def not_found(messageable: discord.abc.Messageable):
    embed = Embed(
        title="Sorry, I've searched far and wide and couldn't find anything")
    file = discord.File('cat_404.jpg')
    embed.set_image(url="attachment://cat_404.jpg")
    await messageable.send(embed=embed, file=file)


@client.event
async def on_ready():
    initial_extensions = ['cogs.command_prefix', 'cogs.error_handling', 
                          'cogs.welcome', 'cogs.easteregg']
    for cog in initial_extensions:
        client.load_extension(cog)
    if not os.path.isfile(os.path.join(filepath, 'cogs', 'prefixes.json')):
        with open(os.path.join(filepath, 'cogs', 'prefixes.json'), 'w') as f:
            json.dump({}, f)
    global stephen_li, freq, command_channel
    with codecs.open(os.path.join(filepath, 'stephen-li.json'), 'r', 
                     encoding='utf-8') as f:
        stephen_li = json.load(f)
    with open('canto_freq_list.csv', mode='r') as f:
        reader = csv.reader(f)
        freq = {rows[0]:rows[3] for rows in reader}
    print(f'{client.user} has connected to Discord!')
    command_channel = client.get_channel(id=785674955676188682)
    await client.change_presence(activity=discord.Activity(
        name=" +help", type=discord.ActivityType.listening))


def embed_from_rxn(reaction):
    return next(iter([x for x in embed_master_list
                     if reaction.message.id == x.message_id]), None)


async def timeout(seconds, voice):
    obj = object()
    global last_play
    last_play = id(obj)
    await asyncio.sleep(seconds)
    if last_play == id(obj):
        await voice.disconnect()


async def reaction_handling(reaction, user):
    if user.bot:
        return
    direction = 0
    selection = 0
    embed = embed_from_rxn(reaction)
    if reaction.emoji == emoji_list.l_arrow:
        direction = -1
    elif reaction.emoji == emoji_list.r_arrow:
        direction = 1
    elif reaction.emoji == emoji_list.sound:
        audio_link = embed.curr_page().audio_link[
                embed.curr_page().curr_selection]
        dir_and_name = re.split(
            r'audio/(?=[^/]+$)',
            audio_link.replace(
                "http://www.stephen-li.com/TaishaneseVocabulary/", ""),
            maxsplit=1, flags=re.IGNORECASE)
        folder_path = Path(os.path.join(
            filepath, 'tones_audio', dir_and_name[0]))
        audio_path = os.path.join(folder_path, dir_and_name[1])
        folder_path.mkdir(parents=True, exist_ok=True)
        orig = os.path.join(
            filepath, 'orig_audio', ''.join(dir_and_name))
        Path(os.path.join(filepath, 'orig_audio', dir_and_name[0])).\
            mkdir(parents=True, exist_ok=True)

        if not os.path.isfile(audio_path):
            mp3 = requests.get(audio_link)
            with open(orig, 'wb') as f:
                f.write(mp3.content)
            pynormalize.process_files(
                [orig], target_dbfs=-12, directory=folder_path)
        
        if isinstance(reaction.message.channel, discord.channel.DMChannel):
            page = embed.curr_page()
            file = discord.File(
                fp=audio_path, 
                filename=page.content.fields[page.curr_selection].name[1:]\
                    .split('-')[0] + '.mp3')
            await reaction.message.channel.send(file=file)
        elif user.voice:
            channel = user.voice.channel
            command_count(
                'audio', reaction.message.guild.id, channel)
            voice = discord.utils.get(
                client.voice_clients, guild=reaction.message.guild)
            print(voice)
            print(client.voice_clients)
            if voice is not None:
                if voice.channel != user.voice.channel:
                    voice = await voice.move_to(user.voice.channel)
            else:  
                voice = await channel.connect()

            source = FFmpegPCMAudio(audio_path)
            try:
                voice.play(source)
            except ClientException:
                await reaction.message.channel.send(
                    "Sorry, I can't connect play the audio")
                return
            await timeout(seconds=30, voice=voice)
        else:
            await reaction.message.channel.send(content=f"{user.mention} please connect to a voice channel to listen to audio!", delete_after=30)

    elif reaction.emoji == emoji_list.d_arrow:
        selection = 1
    elif reaction.emoji == emoji_list.u_arrow:
        selection = -1
    elif reaction.emoji == emoji_list.books:
        page = embed.curr_page()
        curr_selection = page.curr_selection
        if page.is_details:
            await reaction.message.edit(embed=page.content)
            page.is_details = False
        else:
            try:
                alts = [alt for alt in hed_usage(page.defn_idx[curr_selection])]
            except:
                alts = ['No usages found!']
            title = page.content.fields[curr_selection].name
            embed_meanings = Embed(
                title=title, description=f'```{chr(10).join(alts)}```', 
                colour=Color.from_rgb(59, 130, 245))
            add_credit(embed_meanings, embed, 1)
            await reaction.message.edit(embed=embed_meanings)
            page.is_details = True

    if direction != 0:
        change_page(embed, direction)
        await reaction.message.edit(embed=embed.curr_page().content)
        if len(embed.curr_page().audio) > 0:
            await reaction.message.add_reaction(emoji_list.sound)
        else:
            try:
                for poss_react in reaction.message.reactions:
                    if poss_react.emoji == emoji_list.sound:
                        await poss_react.remove(client.user)
            except HTTPException:
                print(emoji_list.sound + " not present")
                pass
    elif selection != 0:
        field_index = embed.curr_page().curr_selection
        curr_field = embed.curr_page().content.fields[field_index]
        value = curr_field.value.replace("asciidoc\n= ", "").replace(" =", "")
        embed.curr_page().content.set_field_at(index=field_index, value=value,
                                               name=curr_field.name[1:],
                                               inline=False)
        field_index = change_selection(embed, selection)
        name = "🠶 " + embed.curr_page().content.fields[field_index].name
        value = embed.curr_page().content.fields[field_index].value
        index = [m.start(0) for m in re.finditer(r'(?!^)```', value)][0]
        value = value[:3] + 'asciidoc\n= ' + value[3:index] + " =" +\
            value[index:]
        embed.curr_page().content.set_field_at(index=field_index, value=value,
                                               name=name, inline=False)
        await reaction.message.edit(embed=embed.curr_page().content)


@client.event
async def on_reaction_add(reaction, user):
    await reaction_handling(reaction, user)


@client.event
async def on_reaction_remove(reaction, user):
    await reaction_handling(reaction, user)


def remove_format(string):
    return re.sub(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]|\<wr\.\>\s|<又>\s|<台>|<topo.>\s', '', string)

@client.command()
async def gc(ctx, *, args):
    if isinstance(ctx.channel, discord.DMChannel):
        command_count('gc', 'dm', ctx.channel)
    else:
        command_count('gc', ctx.guild.id, ctx.channel)
    if re.search(r'[a-zA-Z]', "".join(args)) and len([args]) > 1:
        search = " ".join(args)
    else:
        search = "".join(args)

    if type(args) == str and not re.search(r'[\u4e00-\u9fff\u3400-\u4DBF\u4E00-\u9FCC]', search):  # makes sure its a list
        args = [args]

    def sort(series):
        score = []
        req_synonyms = synonym(search)
        for index, defn in series.items():
            precedence = next(iter([i for i, s in enumerate(defn.split(';')) if search in s]), 0)
            try:
                syn_list = 5 - len([syn for syn in req_synonyms if re.search(rf"\b{re.escape(syn)}\b", defn)]) / max(defn.count(' '), 1)
            except TypeError:
                syn_list = 5
            distance = next(iter([i for i, s in enumerate(re.split(r'[,;.]\s|\s', defn)) if search in s]), 0)
            score.append((precedence, distance, syn_list))
            print(f"{defn[:20]} - {(precedence, syn_list, distance)}\n")
        return pd.Series(score, dtype='float64')

    if re.search(r'[\u4e00-\u9fff\u3400-\u4DBF\u4E00-\u9FCC]', search):
        if len(args) < 2:
            search_result = single_chinese(args[0])
            disp_id = 1
        else:
            search_result = multi_chinese(search)
            disp_id = 2
    elif re.match(r"[A-Za-z]+[1-9]{2,3}\b", search) and len(args) < 2:
        decomp = re.match(r"([a-z]+)([0-9]+)\b", args[0], re.I).groups()
        search_result = pinyin(decomp[0] + tone_to_num.get(decomp[1][:2]))
        disp_id = 3
    else:
        search_result = single_multi_search(search).sort_values(
            by=['英译与词句'], key=sort, ascending=True)
        disp_id = 4

    if search_result.empty:
        embed = Embed(
            title="Sorry, I searched far and wide and couldn't find anything",
            colour=discord.Colour.from_rgb(255, 159, 56))
        file = discord.File('cat_404.jpg')
        embed.set_image(url="attachment://cat_404.jpg")
        await ctx.send(embed=embed, file=file)
        return
    else:
        embed_list = EmbedList(message_id=None, type_id=disp_id)
        if disp_id == 4:
            for index, row in search_result.iterrows():
                embed = Embed(
                    title=f'Words matching "{search}"',
                    colour=Color.from_rgb(161, 202, 255))
                pin_num = ""
                try:
                    pin_num = row['p.y.'].split(" or ")
                    for pin_index, ping in enumerate(pin_num):
                        pin_num[pin_index] = "-".join([re.sub(r'([1-9]+)', lambda x: num_to_tone.get(
                            x.group(), x.group()), pin) for pin in ping.split('-')])
                except (TypeError, AttributeError):
                    print(f"Error on pinyin {row}")
                    pass
                embed_name = f"{' or '.join(pin_num)}-{row['繁']}"
                if not row['简'] is np.nan:
                    embed_name += f"/{row['简']}"
                embed_name = remove_format(embed_name)
                # alt_mean = [alt for alt in hed_usage(index) if search in alt]
                value = f"```{row['英译与词句']}```\n"
                
                embed.add_field(name=embed_name, value=remove_format(value),
                                inline=False)
                add_credit(embed, embed_list, 1)
                embed_list.add_page(embed=embed, audio=[],
                                    link=[], selection=0)
                embed_list.curr_page().defn_idx.append(index)
        elif disp_id == 2:
            for index, row in search_result.iterrows():
                description = remove_format(row['英译与词句'])
                embed = Embed(
                    title=f'Words matching "{search}"',
                    description=f"```{description}```",
                    colour=Color.from_rgb(110, 162, 252))
                add_credit(embed, embed_list, 1)
                embed_list.add_page(embed=embed, audio=[],
                                    link=[], selection=0)
        elif disp_id in [1, 3]:
            counter = 0
            for index, row in search_result.iterrows():
                embed_name = ""
                value = "```"
                if counter == 0:
                    embed_list.add_page(embed=None, audio=[],
                                        link=[], selection=0)
                    embed = Embed(
                        title=f'Words matching "{search}"',
                        colour=Color.from_rgb(59, 130, 245))
                    embed_name = "🠶 "
                    value = "```asciidoc\n= "
                embed_name += re.sub(r'([1-9]+)', lambda x: num_to_tone.get(
                    x.group(), x.group()), row['p.y.']) + '-' + row['繁']
                if not row['简'] is np.nan:
                    embed_name += f"/{row['简']}"
                embed_name = remove_format(embed_name)
                value += f"{row['英译与词句']}"
                if counter == 0:
                    value += " =```\n"
                else:
                    value += "```\n"
                embed.add_field(name=embed_name, value=remove_format(value),
                                inline=False)
                embed_list.curr_page().defn_idx.append(index)
                if counter > 4:
                    add_credit(embed, embed_list, 1)
                    embed_list.curr_page().content = embed
                    counter = 0
                else:
                    counter += 1
            if counter != 0:
                add_credit(embed, embed_list, 1)
                embed_list.curr_page().content = embed

    for index, page in enumerate(embed_list.pages):
        if isinstance(page.content, Embed):
            page.content.set_footer(
                text=f"Page {index+1} of {embed_list.list_len}")

    embed_list.curr = 0
    sent_embed = await ctx.send(embed=embed_list.curr_page().content)
    for emoji in emoji_list[:2]:
        await sent_embed.add_reaction(emoji)
    if len(embed_list.curr_page().audio) == 1:
        await sent_embed.add_reaction(emoji_list.sound)
    if len(embed_list.curr_page().content.fields) > 2:
        await sent_embed.add_reaction(emoji_list.u_arrow)
        await sent_embed.add_reaction(emoji_list.d_arrow)
    if len(embed_list.curr_page().defn_idx) > 0 and disp_id == 1:
        await sent_embed.add_reaction(emoji_list.books)

    add_to_master(embed_list, sent_embed)



@client.command()
async def sl(ctx, *, args):
    if isinstance(ctx.channel, discord.DMChannel):
        command_count('sl', 'dm', ctx.channel)
    else:
        command_count('sl', ctx.guild.id, ctx.channel)
    search = "".join(args).lower()
    counter = 0
    new_args = []
    
    def sort_sl(word):
        index = re.search(
            rf'\b{re.escape(search)}\b', word['english'], re.IGNORECASE)
        if index is None:
            index = (200, 200)
        else:
            index = index.span()
        if index == (-1, -1):
            index = (200, 200)
        return (index[0], len(word['taishanese']))
        
    
    if type(args) == str and not re.search(r'[\u4e00-\u9fff\u3400-\u4DBF\u4E00-\u9FCC]', search):
        args = [args]

    if re.search(u'[\u4e00-\u9fff]', search):
        
        for word in args:
            search_result = single_chinese(word).dropna(subset=['简'])
            if search_result.empty:
                new_args.append(word)
                continue
            else:
                new_args.append(search_result['简'].iloc[0])
        search = "".join(new_args)
        
        search_result = [word for word in stephen_li 
                         if search in word['taishanese']]
    else:
        search_result = [word for word in stephen_li if re.search(rf'\b{re.escape(search)}\b', word['english'].lower())]
    search_result = sorted(search_result, key=sort_sl)

    if len(search_result) == 0:
        embed = Embed(
            title="Sorry, I searched far and wide and couldn't find anything")
        file = discord.File('cat_404.jpg')
        embed.set_image(url="attachment://cat_404.jpg")
        await ctx.send(embed=embed, file=file)
        return
    
    embed_list = EmbedList(message_id=None, type_id=6)
    for word in search_result:
        embed_name = ""
        value = "```"
        if counter == 0:
            embed_list.add_page(embed=None, audio=[], link=[], selection=0)
            embed = Embed(title=f'Words matching "{search}"', 
                        colour=Color.from_rgb(163, 255, 163))
            embed_name = "🠶 "
            value = "```asciidoc\n= "
        embed_name += f"{word['taishaneseRomanization'].replace('[', '').replace(']', '')}-{word['taishanese']}"
        embed_list.curr_page().audio.append(counter)
        embed_list.curr_page().audio_link.append(word['taishaneseAudio'])
        value += f"{word['english']}"
        if counter == 0:
            value += " =```"
        else:
            value += "```"
        if word['notes'] is not None:
            value += word['notes']
        embed.add_field(name=embed_name, value=value + '\n', inline=False)
        if counter > 3:
            add_credit(embed=embed, embed_list=embed_list, credit=2)
            embed_list.curr_page().content = embed
            counter = 0
        else:
            counter += 1

    if counter != 0:
        add_credit(embed=embed, embed_list=embed_list, credit=2)
        embed_list.curr_page().content = embed

    for index, page in enumerate(embed_list.pages):
        if isinstance(page.content, Embed):
            page.content.set_footer(
                text=f"Page {index+1} of {embed_list.list_len}")

    embed_list.curr = 0
    sent_embed = await ctx.send(embed=embed_list.curr_page().content)
    for emoji in emoji_list[:3]:
        await sent_embed.add_reaction(emoji)
    if len(embed_list.curr_page().content.fields) > 2:
        await sent_embed.add_reaction(emoji_list.d_arrow)
        await sent_embed.add_reaction(emoji_list.u_arrow)

    add_to_master(embed_list, sent_embed)

@client.command(aliases=['word', 'random'])
async def randomgc(ctx):
    row = rand_word().iloc[0]
    title = re.sub(r'([1-9]+)', lambda x: num_to_tone.get(
                    x.group(), x.group()), row['p.y.']) + '-' + row['繁']
    if not row['简'] is np.nan:
        title += f"/{row['简']}"
    title = remove_format(title)
    value = f"{row['英译与词句']}"
    embed = Embed(title=title, description=f"```{value}```",
                          colour=Color.from_rgb(186, 143, 255))
    await ctx.send(embed=embed)

@client.command()
async def randomsl(ctx):
    embed_list = EmbedList(message_id=None, type_id=6)
    result = random.choice(stephen_li)
    title = f"{result['taishaneseRomanization']} - {result['taishanese']}"
    embed = Embed(title=title, description=f"```{result['english']}```",
                  colour=Color.from_rgb(110, 143, 93))
    embed_list.add_page(embed, [0], [result['taishaneseAudio']], selection=0)
    sent_embed = await ctx.send(embed=embed)
    await sent_embed.add_reaction(emoji_list.sound)
    add_to_master(embed_list, sent_embed)


@client.command()
async def leave_channel(ctx):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.send("Sorry, this command can only be used in a server")
        return
    command_count('leave_channel', ctx.guild.id, ctx.channel)
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice = discord.utils.get(client.voice_clients,
                                  guild=ctx.message.guild)
        if voice is not None and voice.channel == channel:
            await voice.disconnect()
            return
        else:
            await ctx.send("I'm not in a vc!", delete_after=30)
            return
        
    await ctx.send(content=f"{ctx.author.mention} please connect to a voice channel to use the command!", delete_after=30)


@client.command()
async def hoisan_sauce(ctx):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.send("Sorry, this command can only be used in a server")
        return
    videos = {
        'Taishanese Tones': 'https://www.youtube.com/watch?v=1xSEIOpONuI',
        'What is Taishanese?': 'https://www.youtube.com/watch?v=yS5lOnUBrQw'
    }
    gifs = {
        'Taishanese Tones': 'Taishanese_Tones.gif',
        'What is Taishanese?': 'What_is_Taishanese?.gif'
    }
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice is not None:
            if voice.channel != ctx.author.voice.channel:
                voice = await voice.move_to(ctx.author.voice.channel)
        else:
            voice = await channel.connect()
        mypath = os.path.join(filepath, 'tones_audio', 'hoisan_videos')
        audio_file = [f for f in os.listdir(mypath) if os.path.isfile(
            os.path.join(mypath, f))]
        chosen_file = random.choice(audio_file)
        source = FFmpegPCMAudio(os.path.join(mypath, chosen_file))
        voice.play(source)
        embed = Embed(
            title=f"Now Playing {chosen_file.replace('.mp3', '')}",
            url=videos[chosen_file.replace('.mp3', '')],
            colour=discord.Colour.from_rgb(255, 120, 120))
        file = discord.File(
            os.path.join(
                mypath, 'gifs', gifs[chosen_file.replace('.mp3', '')]),
            filename=gifs[chosen_file.replace('.mp3', '')])
        url = "attachment://" + gifs[chosen_file.replace('.mp3', '')]
        embed.set_image(url=url)
        await ctx.send(embed=embed, file=file)
        while True:
            await asyncio.sleep(300)
            if not voice.is_playing():
                await voice.disconnect()
                break
    else:
        await ctx.send(content=f"{ctx.author.mention} please connect to a voice channel to listen to audio!", delete_after=30)

tone_to_accent_dict = {
    "55": '\u0304',
    "33": '\u0308',
    "22": '\u0342',
    "32": '\u0300',
    "21": '\u0302'
}

vowels = ('a', 'e', 'i', 'o', 'u')


def num_to_accent(input_string):
    return_list = []
    items = [phrase.groups() for phrase in re.finditer(r"([a-z]+)([0-9]+)\b",
                                                       input_string, re.I)]
    for word_num in items:
        positions = [index+1 for index, char in enumerate(
            word_num[0]) if char in vowels]
        if len(positions) > 1:
            return_list.append(word_num[0][:(
                positions[-2])] + tone_to_accent_dict[word_num[1]] +
                    word_num[0][positions[-2]:])
        else:
            return_list.append(word_num[0][:(
                positions[0])] + tone_to_accent_dict[word_num[1]] +
                    word_num[0][positions[0]:])
    return " ".join(return_list)


@client.command()
async def penyim(ctx, *, args):
    if isinstance(ctx.channel, discord.DMChannel):
        command_count('penyim', 'dm', ctx.channel)
    else:
        command_count('penyim', ctx.guild.id, ctx.channel)
    if type(args) == str and not re.search(u'[\u4e00-\u9fff]', args):
        args = [args]
    search_result = []
    search_pinyin = []
    for word in args:
        if re.search(u'[\u4e00-\u9fff]', word):
            row = single_chinese(word)
            if row.empty:
                row = simple_chinese(word)
            if row.empty:
                await not_found(ctx)
                return
            else:
                row = row.sort_index(
                    key=lambda index: pd.Series([len(hed_usage(num)) 
                                                 for num in index.tolist()]), 
                    ascending=False)
            row = row.iloc[0]
            search_result.append(
                re.sub(r'([1-9]+)', lambda x: num_to_tone.get(
                    x.group(), x.group()), row['p.y.']))
            search_pinyin.append(row['台拼'])
        else:
            search_result.append(word)
            search_pinyin.append(word)
    conversion = f'{"".join(args)} -> {" ".join(search_result)} ({" ".join(search_pinyin)})'
    if len(conversion) < 50:
        embed = Embed(
            title=conversion, colour=Color.from_rgb(181, 255, 158))
    elif len(conversion) < 256:
        conversion = f'{"".join(args)}\n{" ".join(search_result)}\n({" ".join(search_pinyin)})'
        embed = Embed(
            title=conversion, colour=Color.from_rgb(181, 255, 158))
    elif len(conversion) <= 2048:
        conversion = f'{"".join(args)}\n\n'\
    f'{" ".join(search_result)}\n\n{" ".join(search_pinyin)}'
        embed = Embed(
            description=conversion, 
            colour=Color.from_rgb(181, 255, 158))
    else:
        await ctx.send("Sorry that's too long!")
    await ctx.send(embed=embed)


@client.command()
async def pause(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if channel != voice:
            await ctx.send(
                content=f"{ctx.author.mention} you need to be in the same \
                    channel as the bot to use this command!")
        else:
            await voice.pause()
    else:
        await ctx.send(
            content=f"{ctx.author.mention} please connect to a voice channel \
                to use this command!", delete_after=30)


@client.command()
async def leave_server(ctx, guild_id=None):
    if guild_id is None:
        await ctx.send("Please specify server id")
        return

    def check(response):
        return response.author.id == 693267245610303518 and \
            response.content == guild_toleave.name

    if ctx.author.id != 693267245610303518:
        return
    guild_toleave = client.get_guild(int(guild_id))
    if guild_toleave is None:
        await ctx.send("Sorry, I couldn't find that server")
    await ctx.send(
        f"Are you sure you want {client.user} to leave {guild_toleave.name}?\n"
        f"Type the server name to confirm.")
    try:
        await client.wait_for('message', timeout=30, check=check)
        await ctx.send(f"{client.user} is leaving {guild_toleave.name} byeee!")
        await guild_toleave.leave()
    except asyncio.TimeoutError:
        await ctx.send("Leave server command *CANCELLED*")

@client.command()
async def dm(ctx, user_id: int, *, args):
    if ctx.author.id != 693267245610303518:
        return
    reciever = await client.fetch_user(int(user_id))
    await reciever.send(args)
    

@client.event
async def on_message(message):
    if not message.guild:
        if len(message.embeds) > 0:
            await command_channel.send(embed=message.embeds[0], content=f"{message.author} sent an embed")
        elif len(message.attachments) > 0:
            for attachment in message.attachements:
                await command_channel.send(file=attachment)
        if message.content != "":
            await command_channel.send(f"{message.author} ({message.author.id}) said {message.content}")
    await client.process_commands(message)


client.run(token)
