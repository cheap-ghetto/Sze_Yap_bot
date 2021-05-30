from PIL import Image, ImageFont, ImageDraw, ImageOps
import discord
from discord.ext import commands
from os.path import dirname, join
import os
import random
import json
from textwrap import wrap
from cogs.jsonfxn import open_wcjson, save_json
from discord import File, Embed, Color
import asyncio
import re
from textwrap import wrap


path = join(dirname(__file__))
admin = True

def ordinal(n):
    if 0 < n%10 < 4 and not 10 < n < 14:
        return "%d%s" % (n, "stndrd"[2*(n%10)-2:2*(n%10)])
    else:
        return "%d%s" % (n, "th")


def calc_border(center: tuple, width: int, dimension):
    dimension /= 2
    return ((center[0] - dimension - width, 
            center[1] - dimension - width),
            (center[0] + dimension + width,
            center[1] + dimension + width))

def find_center(size: tuple, offset: tuple=(0, 0)):
    return (size[0] // 2 + offset[0], size[1] // 2 + offset[1])

def profile_pic(image: Image, pfp: Image, dim: int) -> Image:
    pfp = pfp.resize((dim, dim))
    # create mask and fit/crop
    mask = Image.new(mode='L', size=pfp.size, color=0)
    ImageDraw.Draw(mask).ellipse((0, 0) + pfp.size, fill=255)
    ImageOps.fit(pfp, mask.size, centering=(0.5, 0.5)).putalpha(mask)
    
    center = find_center(size=image.size, offset=(0, -250*image.size[1]//900))
    
    # draw background circle
    ImageDraw.Draw(image).ellipse(
        xy=calc_border(
            center=center, width=8*image.size[1]//900, dimension=dim),
            fill=(0, 0, 0))

    # paste pfp onto image
    image.paste(im=pfp,
                    box=(center[0] - dim // 2, center[1] - dim // 2),
                    mask=mask)
    return image

def add_text(image: Image, en: str, ch: str, name: str, num_mem: int,
             colour: tuple) -> Image:
    im_w, im_h = image.size
    title_font = ImageFont.truetype(
            font=join(path, 'fonts', 'NotoSans-hinted', 'NotoSans-Black.ttf'), 
            size=85*im_h//900)
    draw = ImageDraw.Draw(image)
    offset = 350*im_h//900
    for line in wrap(en, width=28):
        margin = (im_w - title_font.getlength(line))//2
        draw.text(xy=(margin, offset), text=line, font=title_font, 
                  fill=colour, stroke_width=5*im_h//900,
                  stroke_fill=(0,0,0))
        offset += title_font.getsize(line)[1]
    
    title_font = ImageFont.truetype(
            font=join(path, 'fonts', 'stkaiti.ttf'), 
            size=130*im_h//900)
    margin = (im_w - title_font.getlength(ch))//2
    ImageDraw.Draw(image).text(
        xy=(margin, offset), text=ch, fill=colour, font=title_font,
        stroke_width=6*im_h//900, stroke_fill=(0,0,0))
    offset += title_font.getsize(ch)[1] - 10*image.size[1]//900
    
    title_font = ImageFont.truetype(
            font=join(path, 'fonts', 'NotoSans-hinted', 'NotoSans-Black.ttf'), 
            size=70*im_h//900)
    margin = (im_w - title_font.getlength(name + '!'))//2
    ImageDraw.Draw(image).text(
        xy=(margin, offset), text=name + '!', fill=colour, 
        font=title_font, stroke_width=5*im_h//900, stroke_fill=(0,0,0))

    add_member_count(image, num_mem, colour)
    
    return image

def add_member_count(image: Image, member_count: int, colour: tuple) -> Image:
    
    title_font = ImageFont.truetype(
            font=join(path, 'fonts', 'NotoSans-hinted', 'NotoSans-Black.ttf'), 
            size=70*image.size[1]//900)
    text = f"You are our {ordinal(member_count)} member!"
    offset = image.size[1] - title_font.getsize(text)[1] - 15*image.size[1]//900
    margin = (image.size[0] - title_font.getlength(text))//2
    ImageDraw.Draw(image).text(
        xy=(margin, offset), text=text, align='center', fill=colour, 
        font=title_font, stroke_width=5*image.size[1]//900, stroke_fill=(0,0,0))

async def create_image(member):
    welcome = open_wcjson(
            'welcome.json', member.guild.id)[str(member.guild.id)]

    member_cnt = member.guild.member_count
    temp = join(path, 'temp')
    pfp_path = join(temp, f"{member.id}.png")
    await member.avatar_url.save(pfp_path)
    
    if welcome['hoisan_pics'] is True:
        bg_file = random.choice(
            os.listdir(join(path, 'welcome_images', 'hoisan')))
        wel_img = Image.open(join(path, 'welcome_images', 'hoisan', bg_file))
        print(bg_file)
    else:
        bg_file = random.choice(
            os.listdir(join(path, 'welcome_images', 'reg')))
        wel_img = Image.open(join(path, 'welcome_images', 'reg', bg_file))
    
    dim = 300*wel_img.size[1]//900
    
    if welcome['pfp'] is True:
        wel_img = profile_pic(
            image=wel_img, pfp=Image.open(pfp_path), dim=dim)
    if welcome['en_title'] != "":
        wel_img = add_text(
            image=wel_img, en=welcome['en_title'], ch=welcome['ch_title'], 
            name=str(member), num_mem=member_cnt, 
            colour=tuple(welcome['text_colour']))
    wel_img.save(join(temp, f'{member.id}_edited.png'))
    return join(temp, f'{member.id}_edited.png')


class WelcomeImage(commands.Cog):
    
    def __init__(self, client):
        self.client = client
    
    @commands.command(aliases=['test'])
    async def testwcmsg(self, ctx):
        member = ctx.author
        welcome = open_wcjson(
            'welcome.json', member.guild.id)[(str(member.guild.id))]
        img_path = await create_image(member)
        file = File(img_path)
        embed = Embed(colour=Color.from_rgb(77, 179, 247))
        embed.set_image(url=f"attachment://{member.id}_edited.png")
        if welcome['message'] != '':
            await ctx.send(
                welcome['message'].replace('@_mention', member.mention)\
                    .replace('@member#', ordinal(member.guild.member_count)),
                file=file, embed=embed)
        else:
            await ctx.send(file=file, embed=embed)
    
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        welcome = open_wcjson(
            'welcome.json', member.guild.id)[(str(member.guild.id))]
        if welcome['showwcmsg'] is False:
            return
        img_path = await create_image(member)
        file = File(img_path)
        embed = Embed(colour=Color.from_rgb(77, 179, 247))
        embed.set_image(url=f"attachment://{member.id}_edited.png")
        try:
            channel = self.client.get_channel(id=welcome['channel'])
            await channel.send(
                welcome['message'].replace('@_mention', member.mention)\
                    .replace(
                        '@member#', ordinal(member.guild.member_count)), 
                file=file, embed=embed)
        except TypeError:
            return

    
    @commands.command()
    @commands.has_permissions(administrator=admin)
    async def setwcmsg(self, ctx, *, args):
        
        def check_valid(message):
            return ctx.channel.permissions_for(message.author).administrator\
                and message.author == ctx.author\
                and re.match(r'\<#[0-9]{18}\>$', message.content)

        config = open_wcjson('welcome.json', ctx.guild.id)
        
        await ctx.send(f"What is the channel you would like to send the "
                       f"welcome message in?")
        try:
            message = await self.client.wait_for(
                'message', check=check_valid, timeout=60)
            
        except asyncio.TimeoutError:
            await ctx.send(
                "Sorry, I timed out. Please enter valid channel more quickly")
            return

        config[str(ctx.guild.id)]['channel'] = int(
            message.content.replace('<#', '').replace('>', ''))
        config[str(ctx.guild.id)]['message'] = args
        with open('welcome.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        await ctx.send("Ok, welcome message configured!")
    
    @commands.command()
    @commands.has_permissions(administrator=admin)
    async def setentitle(self, ctx, *, args):
        if len(args) > 60:
            await ctx.send("Sorry that title is too long!")
            return
        config = open_wcjson('welcome.json', ctx.guild.id)
        config[str(ctx.guild.id)]['en_title'] = args.replace('#_newline', '\n')
        save_json('welcome.json', config)
        await ctx.send("Ok, English title for welcome message configured!")
    
    
    @commands.command()
    @commands.has_permissions(administrator=admin)
    async def setchtitle(self, ctx, *, args):
        config = open_wcjson('welcome.json', ctx.guild.id)
        config[str(ctx.guild.id)]['ch_title'] = args
        save_json('welcome.json', config)
        await ctx.send("Ok, Chinese title for welcome message configured!")
    
    @commands.command()
    @commands.has_permissions(administrator=admin)
    async def setwcchannel(self, ctx, channel: discord.TextChannel=None):
        if not isinstance(channel, discord.TextChannel):
            await ctx.send("Please specify a text channel!")
            return
        
        config = open_wcjson('welcome.json', ctx.guild.id)
        config[str(ctx.guild.id)]['channel'] = channel.id
        save_json('welcome.json', config)
        await ctx.send("Ok, channel to send welcome message configured!")
    
    @commands.command()
    @commands.has_permissions(administrator=admin)
    async def delwcmsg(self, ctx):
        config = open_wcjson('welcome.json', ctx.guild.id)
        config.pop(str(ctx.guild.id), None)
        save_json('welcome.json', config)
        await ctx.send(
            f"Ok, welcome message deleted for the server: {ctx.guild.name}!")
    
    @commands.command()
    @commands.has_permissions(administrator=admin)
    async def sendwcmsg(self, ctx, show: str=""):
        config = open_wcjson('welcome.json', ctx.guild.id)
        if show.lower() == 'true' or show.lower() == 'on':
            config[str(ctx.guild.id)]['showwcmsg'] = True
            await ctx.send("Ok, I will send a wc msg once someone joins!")
        elif show.lower() == 'false' or show.lower() == 'off':
            config[str(ctx.guild.id)]['showwcmsg'] = False
            await ctx.send("Ok, I won't send a wc msg!")
        else:
            await ctx.send("Please specify true/false or on/off!")
            return
        save_json('welcome.json', config)


    @commands.command()
    @commands.has_permissions(administrator=admin)
    async def showpfp(self, ctx, pfp: str=""):
        config = open_wcjson('welcome.json', ctx.guild.id)
        if pfp.lower() == "true":
            config[str(ctx.guild.id)]['pfp'] = True
            await ctx.send("Set showing pfp to true!")  
        elif pfp.lower() == "false":
            config[str(ctx.guild.id)]['pfp'] = False
            await ctx.send("Set showing pfp to false!")  
        else:
            await ctx.send("Please specify true or false!")
            return
        save_json('welcome.json', config)
    
    @commands.command()
    @commands.has_permissions(administrator=admin)
    async def hoisanwcpics(self, ctx, pic: str=""):
        config = open_wcjson('welcome.json', ctx.guild.id)
        if pic.lower() == "true":
            config[str(ctx.guild.id)]['hoisan_pics'] = True
            await ctx.send("Set showing hoisan pictures to true!")  
        elif pic.lower() == "false":
            config[str(ctx.guild.id)]['hoisan_pics'] = False
            await ctx.send("Set showing hoisan pictures to false!")  
        else:
            await ctx.send("Please specify true or false!")
            return
        save_json('welcome.json', config)
    
    @commands.command(
        aliases=['title_color', 'wccolor', 'wccolour', 'setcolor',\
            'setcolour'])
    @commands.has_permissions(administrator=True)
    async def title_colour(self, ctx, *, args: str=""):
        config = open_wcjson('welcome.json', ctx.guild.id)
        args = args.lower()
        print(args)
        match = re.search(
            r'([0-9]{1,3}),([0-9]{1,3}),([0-9]{1,3})', args.replace(' ', ''))
        if args == 'red':
            config[str(ctx.guild.id)]['text_colour'] = [255, 204, 204]
        elif args == 'blue':
            config[str(ctx.guild.id)]['text_colour'] = [168, 177, 255]
        elif args == 'white':
            config[str(ctx.guild.id)]['text_colour'] = [255, 255, 255]
        elif args == 'yellow':
            config[str(ctx.guild.id)]['text_colour'] = [241, 255, 153]
        elif args == 'green':
            config[str(ctx.guild.id)]['text_colour'] = [186, 255, 168]
        elif match:
            config[str(ctx.guild.id)]['text_colour'] = [
               int(match.group(1)), 
                int(match.group(2)),
                int(match.group(3))]
        else:
            await ctx.send('Please enter a valid colour!')
            return
        await ctx.send(f"Set colour to {args}!")
        save_json('welcome.json', config)
        
 
def setup(client):
    client.add_cog(WelcomeImage(client))