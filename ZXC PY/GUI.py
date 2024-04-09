import os
import json
import random
import asyncio
import discord
import requests
import tkinter as tk
from tkinter import scrolledtext
from discord.ext import commands
import configparser

client = commands.Bot(command_prefix='-')

config = configparser.ConfigParser()

# Default values
config['DEFAULT'] = {
    'key': 'Your AC Key',
    'token': 'Your Discord Token',
    'guilds': '123456,123456',  # Allowed Guilds
    'spam_id': '123456',  # Channel ID To Spam
    'stats_command': '-stats',
    'say_command': '-say',
    'start_command': '-start',
    'stop_command': '-stop'
}

config_file = 'config.ini'

if os.path.exists(config_file):
    config.read(config_file)

key = config['DEFAULT']['key']
token = config['DEFAULT']['token']
guilds = [int(guild_id) for guild_id in config['DEFAULT']['guilds'].split(',')]
spam_id = int(config['DEFAULT']['spam_id'])
stats_command = config['DEFAULT']['stats_command']
say_command = config['DEFAULT']['say_command']
start_command = config['DEFAULT']['start_command']
stop_command = config['DEFAULT']['stop_command']

spam = False

stats = {
    'caught': 0,
    'fled': 0
}

api_endpoint = "http://5.161.72.213:5663/pokemon"

def save_config():
    global key, token, guilds, spam_id, stats_command, say_command, start_command, stop_command
    key = key_entry.get()
    token = token_entry.get()
    guilds = [int(guild_id.strip()) for guild_id in guilds_entry.get().split(',')]
    spam_id = int(spam_id_entry.get())
    stats_command = stats_command_entry.get()
    say_command = say_command_entry.get()
    start_command = start_command_entry.get()
    stop_command = stop_command_entry.get()
    
    config['DEFAULT']['key'] = key
    config['DEFAULT']['token'] = token
    config['DEFAULT']['guilds'] = ','.join(str(guild_id) for guild_id in guilds)
    config['DEFAULT']['spam_id'] = str(spam_id)
    config['DEFAULT']['stats_command'] = stats_command
    config['DEFAULT']['say_command'] = say_command
    config['DEFAULT']['start_command'] = start_command
    config['DEFAULT']['stop_command'] = stop_command
    
    with open(config_file, 'w') as configfile:
        config.write(configfile)

def load_config():
    global key, token, guilds, spam_id, stats_command, say_command, start_command, stop_command
    key = config['DEFAULT']['key']
    token = config['DEFAULT']['token']
    guilds = [int(guild_id) for guild_id in config['DEFAULT']['guilds'].split(',')]
    spam_id = int(config['DEFAULT']['spam_id'])
    stats_command = config['DEFAULT']['stats_command']
    say_command = config['DEFAULT']['say_command']
    start_command = config['DEFAULT']['start_command']
    stop_command = config['DEFAULT']['stop_command']
    
    key_entry.delete(0, tk.END)
    key_entry.insert(tk.END, key)
    
    token_entry.delete(0, tk.END)
    token_entry.insert(tk.END, token)
    
    guilds_entry.delete(0, tk.END)
    guilds_entry.insert(tk.END, ','.join(str(guild_id) for guild_id in guilds))
    
    spam_id_entry.delete(0, tk.END)
    spam_id_entry.insert(tk.END, spam_id)
    
    stats_command_entry.delete(0, tk.END)
    stats_command_entry.insert(tk.END, stats_command)
    
    say_command_entry.delete(0, tk.END)
    say_command_entry.insert(tk.END, say_command)
    
    start_command_entry.delete(0, tk.END)
    start_command_entry.insert(tk.END, start_command)
    
    stop_command_entry.delete(0, tk.END)
    stop_command_entry.insert(tk.END, stop_command)

def start_bot():
    global spam
    global spam_id
    spam = True
    spam_id = int(spam_id_entry.get())
    save_config()
    log_area.insert(tk.END, "Started Rocking Hard\n")
    client.loop.create_task(bot_task())

async def bot_task():
    intervals = [3.2, 3.4, 3.6, 3.8, 4.0, 4.2]
    while spam:
        await send_normal_message(None)
        await asyncio.sleep(random.choice(intervals))

def stop_bot():
    global spam
    spam = False
    save_config()
    log_area.insert(tk.END, "Stopped. I Promise To Be Quiet\n")

async def send_normal_message(message):
    global spam
    global spam_id
    if spam and spam_id:
        with open(r'Messages\Normal.txt', 'r', encoding='utf-8') as f:
            normal = f.read().splitlines()
            random_msg = random.choice(normal)
            log_area.insert(tk.END, f"{random_msg}\n")

def send_catch_message(message):
    with open(r'Messages\Happy.txt', 'r', encoding='utf-8') as f:
        catch = f.read().splitlines()
        random_msg = random.choice(catch)
        log_area.insert(tk.END, f"{random_msg}\n")

@client.event
async def on_ready():
    log_area.insert(tk.END, f'Logged As =========== {client.user.name}\n')

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
            if message.content.lower().startswith(stats_command):
                den = stats['caught'] + stats['fled'] if stats['caught'] + stats['fled'] != 0 else 1
                await message.channel.send(
                    f"\nTotal Caught: {stats['caught']} \nTotal Missed: {stats['fled']}\n\nAccuracy: {((stats['caught'] / den) * 100):.3f}%")
            elif message.content.lower().startswith(say_command):
                say_message = message.content[len(say_command):].strip()
                await message.channel.send(say_message)
            elif message.content.lower().startswith(start_command):
                spam = True
                spam_id = message.channel.id
                save_config()
                await message.channel.send("Started Rocking Hard")
                await bot_task()
            elif message.content.lower().startswith(stop_command):
                spam = False
                save_config()
                await message.channel.send("Stopped. I Promise To Be Quiet")
    except Exception as e:
        print(e)

root = tk.Tk()
root.title("Discord Bot GUI")

log_area = scrolledtext.ScrolledText(root, width=80, height=20)
log_area.grid(row=0, column=0, columnspan=3)

key_label = tk.Label(root, text="Token:")
key_label.grid(row=1, column=0)
key_entry = tk.Entry(root)
key_entry.grid(row=1, column=1)

token_label = tk.Label(root, text="Key:")
token_label.grid(row=2, column=0)
token_entry = tk.Entry(root)
token_entry.grid(row=2, column=1)

guilds_label = tk.Label(root, text="Guilds (comma-separated):")
guilds_label.grid(row=3, column=0)
guilds_entry = tk.Entry(root)
guilds_entry.grid(row=3, column=1)

spam_id_label = tk.Label(root, text="Spam Channel ID:")
spam_id_label.grid(row=4, column=0)
spam_id_entry = tk.Entry(root)
spam_id_entry.grid(row=4, column=1)

stats_command_label = tk.Label(root, text="Stats Command:")
stats_command_label.grid(row=5, column=0)
stats_command_entry = tk.Entry(root)
stats_command_entry.grid(row=5, column=1)

say_command_label = tk.Label(root, text="Say Command:")
say_command_label.grid(row=6, column=0)
say_command_entry = tk.Entry(root)
say_command_entry.grid(row=6, column=1)

start_command_label = tk.Label(root, text="Start Command:")
start_command_label.grid(row=7, column=0)
start_command_entry = tk.Entry(root)
start_command_entry.grid(row=7, column=1)

stop_command_label = tk.Label(root, text="Stop Command:")
stop_command_label.grid(row=8, column=0)
stop_command_entry = tk.Entry(root)
stop_command_entry.grid(row=8, column=1)

start_bot_button = tk.Button(root, text="Start Bot", command=start_bot)
start_bot_button.grid(row=9, column=0)

stop_bot_button = tk.Button(root, text="Stop Bot", command=stop_bot)
stop_bot_button.grid(row=9, column=1)

save_button = tk.Button(root, text="Save Config", command=save_config)
save_button.grid(row=10, column=0)

load_button = tk.Button(root, text="Load Config", command=load_config)
load_button.grid(row=10, column=1)

load_config() # Load config when GUI is opened

root.mainloop()