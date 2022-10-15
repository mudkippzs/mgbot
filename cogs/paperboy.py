"""
1. Check if each guild has a channel called 'newswire'.
2. If it does, iterate through the news items in 'news' and post them as embeds to that 'newswire' channel.
3. Include the article title, article url, set the image to the article image url, take the first paragraph from the extracted article, the language, the publish date, the news source, the authors if they're not empty.
4. The last embed should be a summary of the update listing the headlines + publish date + urls grouped by news source with the server banner as the image.
"""
import discord
import json
import asyncio
import datetime
import os
import requests
import sys
import pytz

from discord.ext import commands, tasks
from paginator import Paginator, Page

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))

from clogger import clogger
from utils import *
from db import DB


class Paperboy(commands.Cog):

    def __init__(self, client):
        self.client = client
        # Check if the task loop is already running
        self.paperrun_task.start()
        config = load_json_config('config.json')
        self.translate_api_key = config['translatekey']
        self.paginator = Paginator(self.client)

    def cog_unload(self):
        self.paperrun_task.cancel()

    def get_news_top_trending_news(self):
        db = DB("config.json")
        db.connect()
        news = db.get_top_trending_articles_by_keywords_per_hour_last_n_days()
        db.disconnect()
        return news

    @tasks.loop(seconds=30)
    async def paperrun_task(self):        
        #clogger("+ Quota reset running")
        now = datetime.datetime.now(pytz.timezone('Europe/Dublin'))
        DEBUG = False
        if str(now.minute) in ["1"] or DEBUG is True:
            clogger("Paperboy running")
            top_trending_news = self.get_news_top_trending_news()
            clogger(f"Got {len(top_trending_news)} articles")
            for guild in self.client.guilds:
                # Get the newswire channel
                newswire_channel = discord.utils.get(guild.channels, name='🌐newswire')
                # If it exists
                if newswire_channel:
                    # Create a list of embeds to send
                    embeds = []
                    embed_links = {}
                    articles_by_country = {}
                    
                    for item in top_trending_news:
                        if len(item[11].split('\n')[0]) > 50:
                            # Create an embed object
                            embed = discord.Embed()
                        
                            # Set the title and url of the article
                            try:
                                embed.title = item[15] # Gets translated title
                            except:
                                clogger(item)

                            if item[8].lower() != 'en':
                                description = translate_string(item[11].split('\n')[0], item[8], self.translate_api_key)
                            else:
                                description = item[11].split('\n')[0]

                            embed.url = item[12]
                            # Set the image to the article image url
                            embed.set_image(url=item[13])
                            # Take the first paragraph from the extracted article
                            embed.description = f"```{description}```"
                            # Set the language of the article
                            embed.add_field(name="Country", value=f"```{item[5]}```")
                            # Set the publish date of the article
                            try:
                                embed.set_footer(text=f"React with 🌐 to share to 🌍world-news!\nDate Published: {item[1].strftime('%d-%m-%Y %H:%M:%S')}", icon_url=guild.icon.url)                                
                            except:
                                embed.set_footer(text="React with 🌐 to share to 🌍world-news!", icon_url=guild.icon.url)                                

                            # Set the news source of the article
                            embed.add_field(name="Source", value=f"```{item[6]}```")

                            if item[9] != "":
                                # Set the authors if they're not empty
                                authors = item[9].replace("{", "").replace("}","").replace("\"","")
                                if len(authors):
                                    embed.add_field(name="Authors", value=f"```{authors}```")
                                

                            try:
                                embed_link = await newswire_channel.send(embed=embed)
                                await embed_link.add_reaction("🌐")
                                embed_links[item[15]] = embed_link.jump_url
                            except:
                                continue
                            
                            if item[5] not in articles_by_country.keys():
                                articles_by_country[item[5]] = []
                            articles_by_country[item[5]].append(item)

                    # Create a summary embed
                    summary_embeds = []
                    for country in articles_by_country:                        
                        summary_embed = discord.Embed(title=f"MG Newsire Latest Headlines for: {country}")                        
                        for article in articles_by_country[country]:
                            summary_embed.add_field(name="\u200b", value=f"[{article[15]}]({embed_links[article[15]]})```{article[12]}```\n", inline=False)
                        summary_embed.set_footer(text="MG Newswire: Click the link to jump to the embed preview above or open the direct URL in your browser.", icon_url=guild.icon.url)
                        summary_embeds.append(summary_embed)

                    for summary in summary_embeds:
                        await newswire_channel.send(embed=summary)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):                        
        # Get the guild
        guild = self.client.get_guild(payload.guild_id)
        # Get the channel
        channel = self.client.get_channel(payload.channel_id)
        # Get the message
        message = await channel.fetch_message(payload.message_id)
        # Get the user
        user = self.client.get_user(payload.user_id)
        # Get the emoji
        emoji = payload.emoji
        # Get the newswire channel
        newswire_channel = discord.utils.get(guild.channels, name='🌐newswire')
        # If it exists
        if newswire_channel:
            # If the reaction is 🌐
            if emoji.name == '🌐':
                # If the message is in the newswire channel
                if channel == newswire_channel:
                    # If the user is not a bot
                    if not user.bot:
                        # Get the world news channel
                        world_news_channel = discord.utils.get(guild.channels, name='🌍world-news')
                        # If it exists
                        if world_news_channel:
                            # Edit the embed to mention the user who reacted and send the message to the world news channel.                            
                            embed = message.embeds[0]
                            if 'MG Newsire Latest Headlines for' not in embed.title:
                                embed.description = f"{user.mention} shared: {embed.description}"
                                await world_news_channel.send(embed=embed)

    def get_all_news_tables(self, db):
        try:
            db.connect()
            query = "SELECT table_name FROM information_schema.tables where table_type='BASE TABLE' AND table_schema='public' AND table_name like 'news_articles_%'"
            db.cur.execute(query)
            tables = db.cur.fetchall()
            db.conn.commit()
            return tables
        except Exception as e:
            clogger('Error getting news tables: {}'.format(e))
            clogger(e)
        finally:
            db.disconnect()

    @commands.slash_command(name='newssearch', description='Search MG\'s DB of news!')
    async def news_search(self, ctx, keywords=[], title=None, article_text=None, country=None, country_code=None):
        # @TODO - implement author and date range filterings
        date_range = [None, None]
        authors = []
        
        """Search MG's DB of news!"""
        if len(keywords) == 0 and title is None and article_text is None and date_range[0] is None and country is None and country_code is None and len(authors) == 0:
            await ctx.send_response("```You did not provide any search terms.```", delete_after=5)
        else:
            query = None
            params = []
            search_filter = {}
            await ctx.send_response("```Searching the Newswire DB...```", delete_after=5)


            db = DB('config.json')
            
            # Build the query string to get the keyword IDs from the keyword table. The keyword param may be a single keyword or a 'list,of,keywords' as string.
            if len(keywords) > 0:
                search_filter['keywords'] = keywords
                db.connect()
                if "," in keywords:
                    keyword_list = [k.strip() for k in keywords.split(",")]
                    query = "SELECT id FROM keywords where term in ({})".format(','.join(["%s"] * len(keyword_list)))                    
                    db.cur.execute(query, keyword_list)
                else:
                    query = "SELECT id FROM keywords where term = %s"
                    params.append(keywords)
                    db.cur.execute(query, params)

                keyword_results = db.cur.fetchall()
                db.conn.commit()
                db.disconnect()
            
            # Build main article search query and add in all WHERE clause params.
            query = "SELECT title, date_published, country_name, news_source, authors, language, article_url, image_url, keywords, extracted_article FROM %table% WHERE "

            if len(keywords) > 0:
                query += "keywords @> ARRAY[{}] AND ".format(','.join([str(x[0]) for x in keyword_results]))
            if title is not None:
                search_filter["title "] = title
                if ',' in title:
                    title_list = title.split(',')
                    for t in title_list:
                        query += "title ilike %s OR "
                        params.append(f"%{t}%")
                else:
                    query += "title ilike %s AND "
                    params.append(f"%{title}%")
            if article_text is not None:
                search_filter["article_text "] = article_text 
                if ',' in article_text:
                    article_term_list = article_text.split(',')
                    for at in article_term_list:
                        query += "extracted_article ilike %s OR "
                        params.append(f"%{at}%")
                else:
                    query += "extracted_article ilike %s AND "
                    params.append(f"%{article_text}%")

            if date_range[0] is not None:
                search_filter["0] "] = 0 
                query += "date_published BETWEEN %s AND %s AND "
                params.append(date_range[0])
                params.append(date_range[1])
            if country is not None:
                search_filter["country "] = country 
                query += "country_name ilike %s AND "
                params.append(f"%{country}%")
            if country_code is not None:
                search_filter["country_code "] = country_code 
                query += "country_code ilike %s AND "
                params.append(f"%{country_code}%")
            if len(authors) > 0:
                search_filter["authors"] = authors
                query += "authors ilike %s AND "
                params.append(f"%{authors}%")
            query = query[:-4]

            terms = ','.join([k + ": " + v for k,v in search_filter.items()])
            await ctx.send_followup(f"```Searching for: {terms}...searching can take some time, please wait...```", delete_after=10)
            tables = [t[0] for t in self.get_all_news_tables(db)]
            query_list = []
            data = []
            
            for table in tables:
                query_list.append(query.replace("%table%", table))                    

            try:
                db.connect()
                clogger([query, params])
                for q in query_list:
                    db.cur.execute(q, params)
                    table_data = db.cur.fetchall()
                    db.conn.commit()                    
                    for article in table_data:
                        data.append(article)
                    clogger(db.cur.query)
            except Exception as e:
                clogger(e)
                await ctx.send_followup(f"```Error searching for articles...```")
            finally:
                db.disconnect()

            if len(data) < 1:
                await ctx.send_followup(f"```There was no articles found for your terms: {terms}...```")
                return

            # Create Embed Pages and add to paginator and send.
            pages = []
            index = 1
            for item in data:
                if item[9] is None:
                    continue
                # Create an embed object
                embed = discord.Embed()
                # Set the title and url of the article
                embed.title = item[0]
                embed.url = item[6]
                # Set the image to the article image url
                embed.set_image(url=item[7])
                # Take the first paragraph from the extracted article
                description = item[9].split('\n')[0]
                embed.description = f"```{description}```"
                # Set the language of the article
                embed.add_field(name="```Language```", value=f"```{item[5]}```")
                # Set the publish date of the article
                if item[1]:
                    embed.set_footer(text=f"Date Published: {item[1].strftime('%d-%m-%Y %H:%M:%S')}", icon_url=ctx.guild.icon.url)
                else:
                    embed.set_footer(text=f"No publish date available.", icon_url=ctx.guild.icon.url)

                # Set the news source of the article
                embed.add_field(name="```Source```", value=f"```{item[3]}```")

                if item[4] != "":
                    # Set the authors if they're not empty
                    authors = item[4].replace("{", "").replace("}","").replace("\"","")
                    if len(authors):
                        embed.add_field(name="```Authors```", value=f"```{authors}```")

                # Set the index of the article
                embed.set_author(name=f"Article: {index}/{len(data)}")

                # Add the embed to the pages list
                pages.append(Page(embed=embed))
                index += 1


            await ctx.send_followup(f"```Found ({len(data)}) for query: {terms}...paginating results, please wait!```", delete_after=10)
            if len(data) < 1:
                return

            await self.paginator.send(ctx.channel, pages, type=2, author=ctx.author, disable_on_timeout=True)
            # Add reacts to search_results and listen for a response from the author, display the article for the selected number emoji clicked.
            def check(payload):
                return payload.user_id == ctx.author.id and payload.message_id == search_results.id and payload.emoji.name in [f"{x}\u20E3" for x in range(1,10)]
            try:
                payload = await self.client.wait_for('raw_reaction_add', check=check, timeout=60)
            except asyncio.TimeoutError:
                try:
                    await search_results.delete()
                    await ctx.send_response(f"```No activity detected - deleting results...```", delete_after=10)
                except:
                    pass
            else:
                index = int(payload.emoji.name.replace("\u20E3", ""))
                selected_article = data[index-1]
                selected_article_embed = discord.Embed()
                # Set the title and url of the article
                selected_article_embed.title = selected_article[0]
                selected_article_embed.url = selected_article[6]
                # Set the image to the article image url
                selected_article_embed.set_image(url=selected_article[7])
                # Take the first paragraph from the extracted article
                selected_article_embed.description = f"```{selected_article[9]}```"
                # Set the language of the article
                selected_article_embed.add_field(name="Language", value=f"```{selected_article[5]}```")
                # Set the publish date of the article
                if selected_article[1]:
                    selected_article_embed.set_footer(text=f"Date Published: {selected_article[1].strftime('%d-%m-%Y %H:%M:%S')}", icon_url=ctx.guild.icon.url)
                else:
                    selected_article_embed.set_footer(text=f"No publish date available.", icon_url=ctx.guild.icon.url)
                # Set the news source of the article
                selected_article_embed.add_field(name="Source", value=f"```{selected_article[3]}```")
                # Set the authors if they're not empty
                if selected_article[4] != "{}":
                    authors = selected_article[4].replace('{', '').replace('}', '').replace('\"', '')
                    selected_article_embed.add_field(name="Authors", value=f"```{authors}```")
                # Set the index of the article
                selected_article_embed.set_author(name=f"Article #{index}")

                await search_results.delete()
                await ctx.channel.send(embed=selected_article_embed)

def setup(client):
    client.add_cog(Paperboy(client))
    clogger("Paperboy loaded")