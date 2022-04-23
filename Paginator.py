#  this package will represent a hopefully easy to use Paginator System for discord embeds
# as a general idea, we will have multiple classes representing:
#  - a page
#  - a "book"/ the embed and discord.View we are working with
import datetime
import typing
from operator import itemgetter

from utils.errors import InvalidIndex, NotAPage
import discord as discord


indexes = []


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
    __image_url__: a url pointing to an image on the web
    Returns Something
    """
    def __init__(self, index: int = None,
                 color: typing.Optional[int] = None,
                 title: typing.Optional[str] = None,
                 url: typing.Optional[str] = None,
                 description: typing.Optional[str] = None,
                 timestamp: typing.Optional[datetime.datetime] = None,
                 fields: typing.Optional[list] = None,
                 author: typing.Optional[dict] = None,
                 image_url: typing.Optional[str] = None,
                 thumbnail: typing.Optional[str] = None):
        if index is None:
            raise InvalidIndex('You must provide an Index for this page!')
        if index in indexes:
            raise InvalidIndex('You must provide a unique index for every page!')
        indexes.append(index)
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
        super().__init__(title=self.title, description=self.description, color=self.color, url=self.url, timestamp=self.timestamp,  )

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
        indexes.remove(self._index)
        if self._book is not None:
            if value in self._book.indexes:
                raise InvalidIndex('You must provide a unique index for every page!')
        self._index = value

    def __lt__(self, other):
        return self.index < other.index

    def __add__(self, other):
        if not isinstance(other, Page):
            raise NotAPage(f"Invalid Operation of type 'Page' and '{type(other)}'")
        if self._index == other.index and self._index is not None:
            raise InvalidIndex('You must provide a unique index for every page!')
        return Book([self, other])


class Book(discord.ui.View):
    def __init__(self, pages: typing.Optional[list], autoindex: bool = True):
        if None in [x.index for x in pages] and autoindex:
            self.autoindex(pages)
        self._pages = self.sort(pages)
        self.index = 0
        self._indexes = []
        super().__init__(timeout=None)

    @discord.ui.button(label='<<', style=discord.ButtonStyle.grey, disabled=True)
    async def first_page(self, interaction: discord.Interaction, button: discord.Button):
        self.index = 0
        self.check_borders()
        await interaction.response.edit_message(embed=self._pages[0], view=self)

    @discord.ui.button(label='<', style=discord.ButtonStyle.grey, disabled=True)
    async def previous_page(self, interaction: discord.Interaction, button: discord.Button):
        self.index -= 1
        self.check_borders()
        await interaction.response.edit_message(embed=self._pages[self.index], view=self)

    @discord.ui.button(label='🤖', style=discord.ButtonStyle.grey)
    async def reload(self, interaction: discord.Interaction, button: discord.Button):
        pass

    @discord.ui.button(label='>', style=discord.ButtonStyle.grey)
    async def next_page(self, interaction: discord.Interaction, button: discord.Button):
        self.index += 1
        self.check_borders()
        await interaction.response.edit_message(embed=self._pages[self.index], view=self)

    @discord.ui.button(label='>>', style=discord.ButtonStyle.grey)
    async def last_page(self, interaction: discord.Interaction, button: discord.Button):
        self.index = len(self._pages) - 1
        self.check_borders()
        await interaction.response.edit_message(embed=self._pages[self.index], view=self)

    def check_borders(self):
        first_two = False
        second_two = False
        if self.index == 0:
            first_two = True
        if self.index == len(self._pages)-1:
            second_two = True
        self.children[0].disabled, self.children[1].disabled = first_two, first_two
        self.children[3].disabled, self.children[4].disabled = second_two, second_two

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
        if len(known_nones) < 1:
            return pages
        known_indexes = self.sort(known_indexes)
        for i in range(len(known_indexes)-1):
            if known_indexes[i].index+1 == known_indexes[i+1].index:
                continue
            else:
                difference = known_indexes[i].index + 1 - known_indexes[i + 1].index
                if difference > 1:
                    for i2 in range(difference):
                        available_indexes.append(known_indexes[i].index + 1 + i2)
                        continue
                available_indexes.append(i)
        if len(available_indexes) < len(known_nones):
            difference = len(known_nones) - len(available_indexes)
            for i in range(difference):
                available_indexes.append(known_indexes[len(known_indexes)+1]+i)
        for none in known_nones:
            none.index = available_indexes[0]
            available_indexes.pop(0)
        final_indexes = known_indexes + known_nones
        final_indexes = self.sort(final_indexes)
        return final_indexes




