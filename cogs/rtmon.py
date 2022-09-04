"""
1. Write a pycord cog task that checks a Rotten Tomatos page every 5m and records the Critic Score and Critic Review count and the Audience Score and Audience Review count.
2. Print this to the channel called 'client-arcade' in an embed and use the movie image from RT's page.
3. Track the delta for Audience and Critic score and post the difference with each update. Use a green up arrow emoji for incease and a red down emoji for a decrease.
"""
import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
import json
from bs4 import BeautifulSoup
import re
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))


from clogger import clogger


async def get_html(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()


def get_soup(html):
    return BeautifulSoup(html, 'lxml')


def get_critic_score(soup):
    critic_score = soup.find('span', attrs={'data-qa': 'tomatometer'})
    return int(critic_score.text.strip().replace("%", ""))


def get_critic_reviews(soup):
    critic_reviews = soup.find(
        'small', attrs={'data-qa': 'tomatometer-review-count'})
    return int(critic_reviews.text.strip())


def get_audience_score(soup):
    audience_score = soup.find('span', attrs={'data-qa': 'audience-score'})
    return int(audience_score.text.strip().replace("%", ""))


def get_audience_reviews(soup):
    audience_reviews = soup.find(
        'strong', attrs={'data-qa': 'audience-rating-count'})
    return int(audience_reviews.text.strip().replace("User Ratings: ",""))


def get_movie_image(soup):
    movie_image = soup.find('img', class_='posterImage')
    return movie_image['data-src']


def get_movie_title(soup):
    movie_title = soup.find(
        'h1', class_='movie_title')
    return movie_title.text.strip().split(":")[0]


class RTMon(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.historical_scores = []
        self.monitor_rt.start()

    def cog_unload(self):
        self.monitor_rt.cancel()

    @tasks.loop(minutes=20)
    async def monitor_rt(self):
        #clogger("Checking RT Reviews")
        url = 'https://www.rottentomatoes.com/tv/the_lord_of_the_rings_the_rings_of_power/s01'
        html = await get_html(url)
        soup = get_soup(html)

        critic_score = get_critic_score(soup)
        critic_reviews = get_critic_reviews(soup)
        audience_score = get_audience_score(soup)
        audience_reviews = get_audience_reviews(soup)
        movie_image = get_movie_image(soup)
        movie_title = get_movie_title(soup)

        audience_delta = 0
        critic_delta = 0

        self.historical_scores.append(
            {
                'critic_score': critic_score,
                'critic_reviews': critic_reviews,
                'audience_score': audience_score,
                'audience_reviews': audience_reviews
            }
        )

        clogger((movie_title, critic_score, critic_reviews,
                 audience_score, audience_reviews))

        if len(self.historical_scores) > 1:
            critic_delta = int(self.historical_scores[-1]['critic_score']) - int(
                self.historical_scores[-2]['critic_score'])
            if critic_delta > 0:
                critic_delta = f'+{critic_delta}'
            else:
                critic_delta = str(critic_delta)

            audience_delta = int(self.historical_scores[-1]['audience_score']) - int(
                self.historical_scores[-2]['audience_score'])
            if audience_delta > 0:
                audience_delta = f'+{audience_delta}'
            else:
                audience_delta = str(audience_delta)

        if int(critic_delta) != 0 or int(audience_delta) != 0:
            embed = discord.Embed(title="RT Cheater Monitor - Watching for deleted reviews...",
                              description=f'{movie_title}', color=0xff0000)
            embed.add_field(name='Critic Score',
                            value=f'**{critic_score}%** `({critic_reviews})`\t`Δ: {critic_delta}`', inline=False)
            embed.add_field(name='Audience Score',
                            value=f'**{audience_score}%** `({audience_reviews})`\t`Δ: {audience_delta}`', inline=False)
        else:
            embed = discord.Embed(title="RT Cheater Monitor - Watching for deleted reviews...",
                              description=f'{movie_title}', color=0x00ff00)
            embed.add_field(name='Critic Score',
                            value=f'**{critic_score}%** `({critic_reviews})`\t`Δ: --`', inline=False)
            embed.add_field(name='Audience Score',
                            value=f'**{audience_score}%** `({audience_reviews})`\t`Δ: --`', inline=False)
        embed.set_thumbnail(url=movie_image)

        channel = self.client.get_channel(822886050359148556)
        await channel.send(embed=embed)


def setup(client):
    client.add_cog(RTMon(client))
