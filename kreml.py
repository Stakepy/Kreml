import discord
from discord import Intents 
from discord.ext import tasks, commands
import asyncio
from datetime import datetime
import pytz

TOKEN = ''
GUILD_ID =
CHANNEL_ID =

intents = Intents.default()
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

melodies = {
    0: 'kreml.mp3',
    1: '1.mp3',
    2: '2.mp3',
    3: '3.mp3',
    4: '4.mp3',
    5: '5.mp3',
    6: '6.mp3',
    7: '7.mp3',
    8: '8.mp3',
    9: '9.mp3',
    10: '10.mp3',
    11: '11.mp3',
    12: 'kreml.mp3',
    13: '1.mp3',
    14: '2.mp3',
    15: '3.mp3',
    16: '4.mp3',
    17: '5.mp3',
    18: '6.mp3',
    19: '7.mp3',
    20: '8.mp3',
    21: '9.mp3',
    22: '10.mp3',
    23: '11.mp3'
}

moscow_tz = pytz.timezone('Europe/Moscow')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f'Could not find channel with ID {CHANNEL_ID}')
        return
    await channel.connect()
    play_melody.start()

@tasks.loop(minutes=1)
async def play_melody():
    current_time = datetime.now(moscow_tz)
    if current_time.minute == 0:
        channel = bot.get_channel(CHANNEL_ID)
        if channel and channel.members:
            melody_path = melodies.get(current_time.hour, None)
            if melody_path:
                voice_client = discord.utils.get(bot.voice_clients, guild=channel.guild)
                if voice_client:
                    voice_client.stop()  
                    voice_client.play(discord.FFmpegPCMAudio(melody_path))

@play_melody.before_loop
async def before_play_melody():
    await bot.wait_until_ready()

@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user:
        if after.channel is None or after.channel.id != CHANNEL_ID:
            await asyncio.sleep(1)
            channel = bot.get_channel(CHANNEL_ID)
            if channel:
                voice_client = discord.utils.get(bot.voice_clients, guild=channel.guild)
                if not voice_client or not voice_client.is_connected():
                    await channel.connect()
                elif voice_client.channel.id != CHANNEL_ID:
                    await voice_client.move_to(channel)
    else:
        if before.channel is None and after.channel is not None:
            
            voice_client = discord.utils.get(bot.voice_clients, guild=after.channel.guild)
            if voice_client and voice_client.is_connected():
                voice_client.play(discord.FFmpegPCMAudio('Join.mp3'))

bot.run(TOKEN)
