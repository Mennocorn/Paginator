#  this package will represent a hopefully easy to use Paginator System for discord embeds
# as a general idea, we will have multiple classes representing:
#  - a page
#  - a "book"/ the embed and discord.View we are working with
#  - add categories with a select menu
#  - modal with page entry

import datetime
import typing
from operator import itemgetter

from utils.errors import InvalidIndex, NotAPage
import discord as discord

from utils.math_helper import get_difference


class Page(discord.Embed):
    """
    Pass in
    __index__: the page` slot
    __color__: the embed`s colour
    __title__: the embed`s title
    __url__: the link the title points to
    __description__: the embed`s description located under the title
    __timestamp__: the embed`s timestamp located at the bottom left
    __fields__: all fields the embed should have >! 25
    __author__: the embed`s author located at the top left
    __image_url__: an url pointing to an image on the web
    Returns Something
    """
    def __init__(self,
                 index: int = None,
                 color: typing.Optional[int] = None,
                 title: typing.Optional[str] = None,
                 url: typing.Optional[str] = None,
                 description: typing.Optional[str] = None,
                 timestamp: typing.Optional[datetime.datetime] = None,
                 fields: typing.Optional[list] = None,
                 author: typing.Optional[dict] = None,
                 image_url: typing.Optional[str] = None,
                 thumbnail: typing.Optional[str] = None):
        if index is not None and index < 0:
            raise InvalidIndex("Index can't be lower than 0")
        self._index = index
        self.color = color
        self.title = title
        self.url = url
        self.description = description
        self.timestamp = timestamp
        self._book = None
        #  not settable
        self.thumbnail_url = thumbnail
        self.all_fields = fields
        self.init_author = author
        self.image_url = image_url
        super().__init__(title=self.title, description=self.description, color=self.color, url=self.url, timestamp=self.timestamp)

    @property
    def book(self):
        return self._book

    @book.setter
    def book(self, value):
        if isinstance(value, Book):
            self._book = value

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value: int):
        self._index = value

    def __lt__(self, other):
        return self._index < other.index

    def __add__(self, other):
        if not isinstance(other, Page):
            raise NotAPage(f"Invalid Operation of type '{type(other)}' and 'Page'")
        if self._index == other.index and self._index is not None:
            raise InvalidIndex('You must provide a unique index for every page!')
        return Book([self, other])


class EnterIndexModal(discord.ui.Modal, title='Go to by index'):

    index = discord.ui.TextInput(required=True, label='Enter a page index!')

    def __init__(self, book):
        self._book = book
        super().__init__(timeout=None)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            value = int(self.index.value) - 1
        except Exception as e:
            return await interaction.response.send_message('The entered index is not a numeric value.', ephemeral=True)

        if value < 1 or value > max([page.index for page in self._book.pages]):
            return await interaction.response.send_message('The entered index is not a valid page.', ephemeral=True)
        self._book.check_borders(self._book.index, value)
        await interaction.response.edit_message(embed=self._book.pages[value], view=self._book)


class Book(discord.ui.View):
    def __init__(self, pages: typing.Optional[list], user: discord.User = None, autoindex: bool = True):
        self._last_index = 0
        self._pages = pages
        if autoindex:
            self._pages = self.autoindex(pages)
        self._pages = self.sort(self._pages)
        self._pages = self.fill_empty_slots(self._pages)
        self.index = 0
        self._indexes = []
        self.user = user
        super().__init__(timeout=None)
        self.check_borders(self.index)

    @property
    def pages(self):
        return self._pages

    @property
    def indexes(self):
        return self._indexes

    @discord.ui.button(label='<<', style=discord.ButtonStyle.grey, disabled=True)
    async def first_page(self, interaction: discord.Interaction, button: discord.Button):
        self.check_borders(self.index, 0)
        await interaction.response.edit_message(embed=self._pages[0], view=self)

    @discord.ui.button(label='<', style=discord.ButtonStyle.grey, disabled=True)
    async def previous_page(self, interaction: discord.Interaction, button: discord.Button):
        self.check_borders(self.index, self.index - 1)
        await interaction.response.edit_message(embed=self._pages[self.index], view=self)

    @discord.ui.button(label='🛑', style=discord.ButtonStyle.grey)
    async def reload(self, interaction: discord.Interaction, button: discord.Button):
        self.clear_items()
        embed = discord.Embed(title='Finished', description=f'Started by: {self.user.mention or "unknown"}')
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='>', style=discord.ButtonStyle.grey)
    async def next_page(self, interaction: discord.Interaction, button: discord.Button):
        self.check_borders(self.index, self.index + 1)
        await interaction.response.edit_message(embed=self._pages[self.index], view=self)

    @discord.ui.button(label='>>', style=discord.ButtonStyle.grey)
    async def last_page(self, interaction: discord.Interaction, button: discord.Button):
        self.check_borders(self.index, len(self._pages) - 1)
        await interaction.response.edit_message(embed=self._pages[self.index], view=self)

    @discord.ui.button(label='🚫', style=discord.ButtonStyle.grey, disabled=True)
    async def filler1(self, interaction: discord.Interaction, button: discord.Button):
        pass
    # ⛔

    @discord.ui.button(label='🚫', style=discord.ButtonStyle.grey, disabled=True)
    async def filler2(self, interaction: discord.Interaction, button: discord.Button):
        pass

    @discord.ui.button(label='🔢', style=discord.ButtonStyle.grey)
    async def enter_index(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.send_modal(EnterIndexModal(self))

    @discord.ui.button(label='🚫', style=discord.ButtonStyle.grey, disabled=True)
    async def filler4(self, interaction: discord.Interaction, button: discord.Button):
        pass

    @discord.ui.button(label='↩', style=discord.ButtonStyle.grey, disabled=True)
    async def go_back(self, interaction: discord.Interaction, button: discord.Button):
        self.index = self._last_index
        self.check_borders(self.index, self.index)
        await interaction.response.edit_message(embed=self._pages[self.index], view=self)

    def check_borders(self, current: int, index: int = None):
        first_two = False
        second_two = False
        self._last_index = current
        self.index = index or self.index
        if self.index == 0:
            first_two = True
        if self.index == len(self._pages)-1:
            second_two = True
        self.children[0].disabled, self.children[1].disabled = first_two, first_two
        self.children[3].disabled, self.children[4].disabled = second_two, second_two
        self.children[5].label = f'{self.index + 1}/{len(self.pages)}'
        self.children[9].disabled = False

    def start(self):
        return self._pages[0]

    def sort(self, pages) -> list:
        self._indexes = []
        for page in pages:
            page.book = self
            if page.index in self._indexes:
                raise InvalidIndex('You must provide unique Indexes for every page')
            self._indexes.append(page.index)
        pages.sort()
        return pages

    def __add__(self, other):
        if isinstance(other, Page):
            self._pages.append(other)
        elif isinstance(other, list):
            if all(isinstance(x, Page) for x in other):
                self._pages = self._pages + other
        else:
            raise NotAPage(f"Invalid Operation of type 'Book' and '{type(other)}'! You can only add Pages and lists of Pages to this.")
        self._pages = self.sort(self._pages)

    def __and__(self, other):
        if isinstance(other, Book):
            pass
            # TODO think of a way to reset Indexes, basically an autoindex

    def autoindex(self, pages):
        known_indexes = []
        known_nones = []
        available_indexes = []
        for page in pages:
            if page.index is not None and page.index not in known_indexes:
                known_indexes.append(page)
            else:
                known_nones.append(page)
        if len(known_indexes) == 0 and len(known_nones) >= 1:
            i = 0
            for page in known_nones:
                page.index = i
                i += 1
            return known_nones
        if len(known_nones) < 1:
            return pages
        known_indexes = self.sort(known_indexes)
        for i in range(len(known_indexes)-1):
            if known_indexes[i].index+1 == known_indexes[i+1].index:
                continue
            else:
                difference = get_difference(known_indexes[i + 1].index, known_indexes[i].index)
                if difference > 1:
                    for i2 in range(difference):
                        available_indexes.append(known_indexes[i].index + 1 + i2)
                available_indexes.append(i)
        if known_indexes[0].index > 0:
            difference = known_indexes[0].index
            for i in range(difference):
                available_indexes.append(i)
        if len(available_indexes) < len(known_nones):
            difference = get_difference(len(known_nones), len(available_indexes))
            for i in range(difference):
                available_indexes.append(known_indexes[len(known_indexes)-1].index+i+1)
        for i in range(len(known_nones)):
            known_nones[i].index = available_indexes[i]
        final_indexes = known_indexes + known_nones
        final_indexes = self.sort(final_indexes)

        return final_indexes

    @staticmethod
    def fill_empty_slots(pages):
        if pages[0].index != 0:
            pages[0].index = 0
        for i in range(len(pages)-1):
            if pages[i].index + 1 == pages[i + 1].index:
                continue
            else:
                pages[i + 1].index = pages[i].index + 1
        return pages

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.user is None or interaction.user.id == self.user.id:
            return True
        await interaction.response.send_message(f"You can't use this paginator, it belongs to {self.user.mention}.", ephemeral=True)
        return False




