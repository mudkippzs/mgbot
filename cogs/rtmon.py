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
import time

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
    return int(audience_reviews.text.strip().replace("User Ratings: ", ""))


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
        self.url = None
        self.active = False
        self.channel = None

    def cog_unload(self):
        self.monitor_rt.cancel()

    @commands.slash_command(name="rttarget", description="Set the target for the RT monitor")
    @commands.has_role('Admin')
    async def rttarget(self, ctx, url: str = None):
        if url == None:
            await ctx.send_response("```Please provide a Rotten Tomatos URL. Ex: https://www.rottentomatoes.com/tv/the_lord_of_the_rings_the_rings_of_power/s01```", delete_after=15)

        if url.startswith("https") == False:
            await ctx.send_response("```Please provide a Rotten Tomatos URL. Ex: https://www.rottentomatoes.com/tv/the_lord_of_the_rings_the_rings_of_power/s01```", delete_after=15)

        self.url = url
        await ctx.send_response(f"```RT Monitor URL updated: {url}```", delete_after=10)

    @commands.slash_command(name="rtchannel", description="Set the target Channel the RT monitor to send updates to.")
    @commands.has_role('Admin')
    async def rtchannel(self, ctx, channel: discord.channel.TextChannel = None):
        if channel == None:
            await ctx.send_response("```Please provide a channel ID or #channel_name```", delete_after=15)

        self.channel = channel
        await ctx.send_response(f"```RT Monitor Channel updated: {channel}```", delete_after=10)

    @commands.slash_command(name="rttoggle", description="Toggle the updater ON or OFF, for the RT monitor")
    @commands.has_role('Admin')
    async def rttoggle(self, ctx, url: str = None):
        if self.active == False:
            self.active = True
            state = "ON"
        else:
            self.active = False
            state = "OFF"

        await ctx.send_response(f"```RT Monitor: {state}```", delete_after=15)

    @commands.slash_command(name="rttest", description="Test the RT monitor")
    @commands.has_role('Admin')
    async def rttest(self, ctx, count: int = 5):
        await ctx.send_response("```RT Monitor Test Initiated...please wait.```")
        self.url = "https://www.rottentomatoes.com/tv/the_lord_of_the_rings_the_rings_of_power/s01"
        # get the channel for channel id 823656840701149194
        self.channel = self.client.get_channel(823656840701149194)
        self.active = False
        try:
            for i in range(count):
                time.sleep(1.5)
                await self.get_rt_reviews()

            await ctx.send_followup("```RT Mon Test Completed```")
        except Exception as e:
            await ctx.send_followup(f"```markdown**RT Mon Error:**\n{e}```")
            pass

        self.url = None
        self.channel = None

    @tasks.loop(minutes=20)
    async def monitor_rt(self):
        if self.active:
            if self.channel:
                if self.url:
                    self.get_rt_reviews()
                else:
                    clogger("```Please set a target URL.```")
            else:
                clogger("```Please set a target channel for updates.```")

    async def get_rt_reviews(self):
        #clogger("Checking RT Reviews")
        url = self.url
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

        # clogger((movie_title, critic_score, critic_reviews,
        #         audience_score, audience_reviews))

        if len(self.historical_scores) > 1:
            # clogger(self.historical_scores)
            critic_delta = int(self.historical_scores[-1]['critic_reviews']) - int(
                self.historical_scores[-2]['critic_reviews'])

            if critic_delta != 0:
                critic_delta = f'{critic_delta}'
            else:
                critic_delta = str(critic_delta)

            audience_delta = int(self.historical_scores[-1]['audience_reviews']) - int(
                self.historical_scores[-2]['audience_reviews'])

            if audience_delta != 0:
                audience_delta = f'{audience_delta}'
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

        channel = self.channel
        await channel.send(embed=embed)


def setup(client):
    client.add_cog(RTMon(client))
