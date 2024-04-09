import os
import json
import random
import asyncio
import discord
import requests
from discord.ext import commands

client = commands.Bot(command_prefix='-')

key = 'Your AC Key'
token = 'Your Discord Token'

guilds = [123456,123456] # Allowed Guilds

spam_id = 123456 # Channel ID To Spam
spam = False

stats = {
    'caught': 0,
    'fled': 0
}

api_endpoint = "http://5.161.72.213:5663/pokemon"

@client.event
async def on_ready():
    print(f'Logged As =========== {client.user.name}')


async def send_normal_message(message):

    global spam
    global spam_id

    if spam == True and message.channel.id == spam_id:

        with open (r'Messages\Normal.txt','r', encoding='utf-8') as f:
            normal = f.read().splitlines()


            random_msg = random.choice(normal)
            await message.channel.send(random_msg)

async def send_catch_message(message):

    with open (r'Messages\Happy.txt','r', encoding='utf-8') as f:
        catch = f.read().splitlines()

        random_msg = random.choice(catch)
        await message.channel.send(random_msg)


@client.event
async def on_message(message):

    global spam

    try:
        if message.guild.id not in guilds:
            return

        if message.author.id == 716390085896962058:
            if "Congratulations" in message.content:
                stats['caught'] += 1

                spam = True
                await send_catch_message(message)

            if not message.embeds or len(message.embeds) == 0 or "wild pokémon has appeared!" not in message.embeds[0].title:
                return

            spam = False

            response = requests.post(api_endpoint, headers={'Content-Type': 'application/json'},
                                     json={'key': key, 'image_url': message.embeds[0].image.url})
            data = response.json()
            name = data['pokemon'][0]
            print(name)
            await message.channel.send(f'<@716390085896962058> c {name}')
            print('Sent')   
            if "fled" in message.embeds[0].title:
                stats['fled'] += 1
        
        else:
            if message.content.lower().startswith("-stats"):
                den = stats['caught'] + stats['fled'] if stats['caught'] + stats['fled'] != 0 else 1
                await message.channel.send(
                    f"\nTotal Caught: {stats['caught']} \nTotal Missed: {stats['fled']}\n\nAccuracy: {((stats['caught'] / den) * 100):.3f}%")
            elif message.content.lower().startswith("-say"):
                say_message = message.content[len("-say"):].strip()
                await message.channel.send(say_message)
            elif message.content.lower().startswith("-start"):

                global spam_id

                spam = True
                spam_id = message.channel.id

                await message.channel.send("Started Rocking Hard")

                intervals = [3.2, 3.4, 3.6, 3.8, 4.0, 4.2]

                while spam == True:
                    await send_normal_message(message)
                    await asyncio.sleep(random.choice(intervals))

            elif message.content.lower().startswith("-stop"):

                spam = False
                await message.channel.send("Stopped. I Promise To Be Quiet")
        
    except Exception as e:
        print(e)

client.run(token)
