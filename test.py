import datetime

import discord
from discord.ext import commands

import config
from Paginator import Page, Book
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='§', intents=intents)


@bot.listen()
async def on_ready():
    print('ready')


@bot.command()
async def test(ctx):
    print('command reached')
    pages = []
    for i in range(1, 21):
        pages.append(Page(color=None, title=str(i), url=None, description='Just a funny hello', timestamp=datetime.datetime.now(), fields=None, author=None, image_url=None, thumbnail=None))
    pages.append(Page(index=45, color=None, title=str(21), url=None, description='Just a funny hello', timestamp=datetime.datetime.now(), fields=None, author=None, image_url=None, thumbnail=None))
    book = Book(pages, autoindex=True, user=ctx.author)
    await ctx.reply(content=None, embed=book.start(), view=book)


bot.run(config.token)
