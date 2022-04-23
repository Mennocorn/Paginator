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
    page1 = Page(index=0, color=None, title='hey', url=None, description='Just a funny hello', timestamp=datetime.datetime.now(), fields=None, author=None, image_url=None, thumbnail=None)
    page2 = Page(index=1, color=None, title='hey2222', url=None, description='Just a funny hello', timestamp=datetime.datetime.now(), fields=None, author=None, image_url=None, thumbnail=None)
    book = page1 + page2
    await ctx.reply(content=None, embed=book.start(), view=book)


bot.run(config.token)
