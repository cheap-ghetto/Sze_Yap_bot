import discord


class EmbedPage:
    def __init__(self, embed: discord.Embed, audio: list, audio_link: str,
                 curr_selection: int):
        self.content = embed
        self.audio = audio
        self.audio_link = audio_link
        self.curr_selection = curr_selection
        self.page = None
        self.defn_idx = []
        self.is_details = False


class EmbedList:
    def __init__(self, message_id: int, type_id: int):
        self.pages = []
        self.curr = 0
        self.list_len = 0
        self.message_id = message_id
        self.type_id = type_id

    def add_page(self, embed: discord.Embed, audio: list,
                 link: list, selection: int):
        self.pages.append(EmbedPage(embed=embed, audio=audio, audio_link=link,
                                    curr_selection=selection))
        self.list_len += 1
        self.curr = self.list_len - 1

    def curr_page(self) -> EmbedPage:
        return self.pages[self.curr]


def change_page(embed: EmbedList, direction: int) -> EmbedPage:
    last = embed.list_len - 1

    if direction == 0:
        return embed.curr_page()

    if direction < 0 and embed.curr < 1:
        curr_page = last
    elif direction > 0 and embed.curr >= last:
        curr_page = 0
    else:
        curr_page = embed.curr + direction
    embed.curr = curr_page
    return embed.curr_page()


def change_selection(embed: EmbedList, direction: int) -> int:
    num_elem = len(embed.curr_page().content.fields)
    if num_elem <= 2:
        return
    if direction == 0:
        return
    if direction < 0 and embed.curr_page().curr_selection < 1:
        curr_field = num_elem - 2
    elif direction > 0 and embed.curr_page().curr_selection >= num_elem-2:
        curr_field = 0
    else:
        curr_field = embed.curr_page().curr_selection + direction
    embed.curr_page().curr_selection = curr_field
    return curr_field


def add_credit(embed, embed_list, credit):
    if credit == 1:
        embed.add_field(
            name=chr(173),
            value=f"*SOURCE*: [Gene Chin's Hoisanva English Dictionary]"
            f"(https://sites.fitnyc.edu/users/gene_chin/hed/index.htm)",
            inline=False)
    else:
        embed.add_field(
            name=chr(173),
            value=f"*SOURCE*: [Stephen Li's Taishanese Dictionary]"
            f"(https://stephen-li.com/WebTemplates/greencreative/taishanese."
            f"html)",
            inline=False)
    if len(embed_list.pages) > 1 and embed_list.type_id in [1, 3]:
        embed_list.curr_page().audio.extend([None, None])
        embed_list.curr_page().audio_link.extend([None, None])