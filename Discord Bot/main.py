import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import asyncio

from apikeys import *

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('Bot is ready for use.')
    print("--------------------")

@bot.command()
async def hello(ctx):
    await ctx.send('Hello, I am a bot.')

@bot.command()
async def bye(ctx):
    await ctx.send('Goodbye, see you soon!')

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.event
async def on_member_join(member):
   await member.send(f'Welcome to the server {member.mention}!')

@bot.command(pass_context=True)
async def join(ctx):
    if(ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        source = FFmpegPCMAudio("night-in-kyoto.wav")
        voice.play(source)
    else:
        await ctx.send("You are not in a voice channel.")

@bot.command(pass_context=True)
async def leave(ctx):
    if(ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("I left the voice channel.")
    else:
        await ctx.send("I am not in a voice channel.")

@bot.command()
async def clear(ctx, amount=5):
    """Clear a specified number of messages in the channel."""
    await ctx.channel.purge(limit=amount + 1)

@bot.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    if member.guild_permissions.administrator:
        await ctx.send("I cannot kick admins!")
    else:
        await member.kick(reason=reason)
        await ctx.send(f'{member.mention} has been kicked.')

@bot.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    """Ban a member from the server."""
    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} has been banned.')

@bot.command()
async def unban(ctx, *, member):
    """Unban a member from the server."""
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'{user.mention} has been unbanned.')
            return

    await ctx.send(f'Could not find a banned user with the name {member}.')

@bot.command()
async def mute(ctx, member: discord.Member, duration: int = None):
    # Check if the command issuer has the 'mute' permission
    if not ctx.author.guild_permissions.mute_members:
        await ctx.send("You don't have the required permissions to use this command.")
        return

    # Get the mute role or create it if it doesn't exist
    mute_role = discord.utils.get(ctx.guild.roles, name='Muted')
    if not mute_role:
        mute_role = await ctx.guild.create_role(name='Muted', reason='Creating mute role')

        # Modify channel permissions to disallow speaking for muted role
        for channel in ctx.guild.channels:
            await channel.set_permissions(mute_role, send_messages=False, read_message_history=True, read_messages=True)

    # Mute the member
    await member.add_roles(mute_role, reason=f'Muted by {ctx.author.display_name}')

    # Send a message indicating the mute
    await ctx.send(f"{member.mention} has been muted.")

    # If a duration is provided, schedule an unmute after the specified time
    if duration:
        await ctx.send(f"The mute will be automatically lifted in {duration} seconds.")
        await asyncio.sleep(duration)
        await member.remove_roles(mute_role, reason='Automatic unmute')

@bot.command()
async def unmute(ctx, member: discord.Member):
    # Check if the command issuer has the 'mute' permission
    if not ctx.author.guild_permissions.mute_members:
        await ctx.send("You don't have the required permissions to use this command.")
        return

    # Get the mute role
    mute_role = discord.utils.get(ctx.guild.roles, name='Muted')
    if not mute_role:
        await ctx.send("There is no mute role to remove.")
        return

    # Unmute the member
    await member.remove_roles(mute_role, reason=f'Unmuted by {ctx.author.display_name}')

    # Send a message indicating the unmute
    await ctx.send(f"{member.mention} has been unmuted.")


url = 'https://www.youtube.com/watch?v=mmKguZohAck'
@bot.command()
async def play(ctx, url=url):
    """Play a song from a YouTube URL."""
    if not ctx.voice_client:
        if ctx.author.voice:  # Check if the command issuer is in a voice channel
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
        else:
            await ctx.send("You are not in a voice channel.")
            return

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    ctx.voice_client.play(discord.FFmpegPCMAudio(url))

@bot.command()
async def stop(ctx):
    """Stop playing audio."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Stopped playback.")
    else:
        await ctx.send("I am not playing anything.")

    
@bot.command()
async def commands(ctx):
    embed = discord.Embed(title="Help", description="List of available commands:", color=0xeee657)
    embed.add_field(name="!hello", value="Greets the user.")
    embed.add_field(name="!bye", value="Says goodbye to the user.")
    embed.add_field(name="!ping", value="Returns the bot's latency.")
    embed.add_field(name="!join", value="Joins the user's voice channel and plays a song.")
    embed.add_field(name="!leave", value="Leaves the voice channel.")
    embed.add_field(name="!clear", value="Clears a specified number of messages in the channel.")
    embed.add_field(name="!kick", value="Kicks a member from the server.")
    embed.add_field(name="!ban", value="Bans a member from the server.")
    embed.add_field(name="!unban", value="Unbans a member from the server.")
    embed.add_field(name="!mute", value="Mutes a member in the server.")
    embed.add_field(name="!unmute", value="Unmutes a member in the server.")
    embed.add_field(name="!help", value="Shows this message.")

    await ctx.send(embed=embed)


bot.run(token)

