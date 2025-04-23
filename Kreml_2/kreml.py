import discord
from discord import Intents
from discord.ext import commands
import asyncio
from datetime import datetime
import pytz

TOKEN = ''
GUILD_CHANNEL_MAP = {
    'guild_id': 'channel_id',
    # Add more guild and channel ID pairs as needed
}

intents = Intents.default()
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

moscow_tz = pytz.timezone('Europe/Moscow')
current_month = datetime.now(moscow_tz).month
is_winter_or_fall = current_month in [9, 10, 11, 12, 1, 2]  # Осень и зима

# Генерация словаря мелодий по времени года
if is_winter_or_fall:
    print("Сейчас осень или зима — используются мелодии 1.mp3 - 12.mp3")
    melodies = {
        hour: f'{(hour % 12) + 1}.mp3'  # 1.mp3 - 12.mp3
        for hour in range(24)
    }
else:
    print("Сейчас весна или лето — используются мелодии kreml_1.mp3 - kreml_12.mp3")
    melodies = {
        hour: f'kreml_{(hour % 12) + 1}.mp3'  # kreml_1.mp3 - kreml_12.mp3
        for hour in range(24)
    }

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    for guild_id, channel_id in GUILD_CHANNEL_MAP.items():
        guild = bot.get_guild(int(guild_id))
        channel = bot.get_channel(int(channel_id))
        if not channel:
            print(f'Could not find channel with ID {channel_id} in guild {guild.name}')
            continue
        await connect_to_channel(channel)
    bot.loop.create_task(play_melody_every_hour())  # Start the melody loop

async def connect_to_channel(channel):
    while True:
        try:
            await channel.connect()
            break
        except discord.DiscordException as e:
            print(f'Error connecting to channel: {e}')
            await asyncio.sleep(5)  # Wait before retrying

async def play_melody_every_hour():
    while True:
        current_time = datetime.now(moscow_tz)
        if current_time.minute == 0 and current_time.second == 0:
            for guild_id, channel_id in GUILD_CHANNEL_MAP.items():
                channel = bot.get_channel(int(channel_id))
                if channel and channel.members:  # Only play if there are members in the channel
                    melody_path = melodies.get(current_time.hour, None)
                    if melody_path:
                        voice_client = discord.utils.get(bot.voice_clients, guild=channel.guild)
                        if voice_client:
                            voice_client.stop()  # Stop any existing audio before playing
                            voice_client.play(discord.FFmpegPCMAudio(melody_path))
                            print(f'Playing melody {melody_path} in {channel.guild.name} at {current_time}')
        await asyncio.sleep(1)  # Check every second

@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user:
        # Handle the bot moving between channels
        for guild_id, channel_id in GUILD_CHANNEL_MAP.items():
            if after.channel is None or after.channel.id != int(channel_id):
                await asyncio.sleep(1)
                channel = bot.get_channel(int(channel_id))
                if channel:
                    voice_client = discord.utils.get(bot.voice_clients, guild=channel.guild)
                    if not voice_client or not voice_client.is_connected():
                        await connect_to_channel(channel)
                    elif voice_client.channel.id != int(channel_id):
                        await voice_client.move_to(channel)
    else:
        # Handle a user joining the channel and playing a sound
        if before.channel is None and after.channel is not None:
            voice_client = discord.utils.get(bot.voice_clients, guild=after.channel.guild)
            if voice_client and voice_client.is_connected():
                print(f'{member.name} joined the voice channel: {after.channel.name}')
                if not voice_client.is_playing():
                    voice_client.play(discord.FFmpegPCMAudio('Join.mp3'))

bot.run(TOKEN)
