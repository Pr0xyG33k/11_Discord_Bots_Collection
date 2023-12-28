import discord
import os
import datetime
import requests
import asyncio
import openai
import schedule
import json
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Load the environment variables that contain the Discord API tokens and IDs
load_dotenv()
ID_TOKEN_EVENTS = os.getenv('DISCORD_TOKEN_EVENTS')
ID_TOKEN_COMMANDS = os.getenv('DISCORD_TOKEN_COMMANDS')
ID_TOKEN_OPENAI = os.getenv('OPENAI_TOKEN')
WELCOME_CHANNEL_ID = int(os.getenv('WELCOME_CHANNEL_ID'))
GENERAL_CHANNEL_ID = int(os.getenv('GENERAL_CHANNEL_ID'))
ROLES_CHANNEL_ID = int(os.getenv('ROLES_CHANNEL_ID'))
REACT_CHANNEL_ID = int(os.getenv('REACT_CHANNEL_ID'))
RULES_CHANNEL_ID = int(os.getenv('RULES_CHANNEL_ID'))
MEMBER_JOIN_ID = int(os.getenv('MEMBER_JOIN_ID'))
MEMBER_LEAVE_ID = int(os.getenv('MEMBER_LEAVE_ID'))
ANNOUCEMENTS_CHANNEL_ID = int(os.getenv('ANNOUCEMENTS_CHANNEL_ID'))
VISITOR_ROLE_ID=int(os.getenv('VISITOR_ROLE_ID'))
MEMBER_ROLE_ID=int(os.getenv('MEMBER_ROLE_ID'))
ADMINISTRATOR_ROLE_ID=int(os.getenv('ADMINISTRATOR_ROLE_ID'))
MODERATOR_ROLE_ID=int(os.getenv('MODERATOR_ROLE_ID'))
TRIAL_MODERATOR_ROLE_ID=int(os.getenv('TRIAL_MODERATOR_ROLE_ID'))
LEAD_MODERATOR_ROLE_ID=int(os.getenv('LEAD_MODERATOR_ROLE_ID'))
DEVOPS_ROLE_ID=int(os.getenv('DEVOPS_ROLE_ID'))
INFOSEC_ROLE_ID=int(os.getenv('INFOSEC_ROLE_ID'))
DATA_ROLE_ID=int(os.getenv('DATA_ROLE_ID'))
BOT_ROLE_ID=int(os.getenv('BOT_ROLE_ID'))

# Initialize the bot for handling events
intents_events = discord.Intents.all()
intents_events.members = True
intents_events.typing = True
intents_events.presences = True
bot_events = discord.Client(command_prefix=None, intents=intents_events)
openai_api_key = os.environ.get("ID_TOKEN_OPENAI")
openai.api_key = openai_api_key
previous_alerts = []  # List to store previous alerts

# Initialize the bot for handling commands
intents_commands = discord.Intents.all()
intents_commands.members = True
intents_commands.typing = True
intents_commands.presences = True
bot_commands = commands.Bot(command_prefix="$", intents=intents_commands)
filtered_words_counter = {}
muted_users = {}
kicked_users = {}

# Define a dictionary that maps emojis to role names
emoji_to_role = {
    '💻': 'Devops',
    '🛡️': 'Infosec',
    '📊': 'Data Analyst',
    '🤖': 'Bot Developer'
}

emoji_to_verif = {
    '✅': 'Verified'
}

# Event handler when the bot for handling events is ready
@bot_events.event
async def on_ready():
    print(f'Bot events has connected as {bot_events.user}')
    print('---------------------------------------------------')

# Event handler when the bot for handling commands is ready
@bot_commands.event
async def on_ready():
    print(f'Bot commands has connected as {bot_commands.user}')
    print('---------------------------------------------------')

# Event handler when a member joins the server
@bot_events.event
async def on_member_join(member):
    # Your existing code to send a welcome message in DM and in the welcome channel
    guild = member.guild

    # Send the welcome message in a direct message
    message = discord.Embed(title=f'Welcome to our server! {guild}',
                            description="I'm a bot and I help welcome new members",
                            color=0x000000)
    message.add_field(name="How to enter the server",
                      value="➥ Fill out the Captcha and validate the rules.",
                      inline=False)
    message.add_field(name="What the server talks about",
                      value="➥ Computer science, autonomy, finance. The subjects are diverse and varied, and we can address serious topics.",
                      inline=False)
    message.add_field(name="Warning",
                      value="➥ If you leave this server, you will be banned from it and you will not be able to join it again unless a moderation member allows you to return.",
                      inline=False)
    message.add_field(name="Tips",
                      value="➥ After joining the server, select roles to gain access.",
                      inline=False)
    message.add_field(name="Questions about the server",
                      value="➥ Bot.",
                      inline=False)
    await member.send(embed=message)

    # Send a notification in the 'join-member' channel
    channel = discord.utils.get(guild.channels, id=MEMBER_JOIN_ID)
    if channel:
        mention = member.mention
        embed = discord.Embed(title=str("***New Member Joined***"),
                              colour=0x33c946,
                              description=str(f'{mention} joined the {guild}').format(mention=mention, guild=guild))
        try:
            embed.set_thumbnail(url=member.avatar)
        except:
            embed.remove_thumbnail()
            embed.set_thumbnail(url=member.default_avatar)
        embed.timestamp=datetime.datetime.utcnow()
        embed.add_field(name='User Name :', value=member.display_name, inline=True)
        embed.add_field(name='Server Name :', value=guild, inline=True)
        embed.add_field(name='User Serial :', value=len(list(guild.members)), inline=True)
        embed.add_field(name='Created_at :', value=member.created_at.strftime('%a, %#d %B %Y, %I:%M %p UTC'), inline=True)
        embed.add_field(name='Joined_at :', value=member.joined_at.strftime('%a, %#d %B %Y, %I:%M %p UTC'), inline=True)
        await channel.send(embed=embed)

     # Send a notification in the 'general' channel
    general_channel = discord.utils.get(guild.channels, id=GENERAL_CHANNEL_ID)
    if general_channel:
    # Create an embed with the roles message in multiple parts
        embed = discord.Embed(title="Welcome to the Server!",
                          description=f"Welcome to the server {member.mention}!\n\n"
                                      f"We're delighted to have you with us. "
                                      f"Take a moment to read the rules in <#{WELCOME_CHANNEL_ID}>.\n\n"
                                      f"If you have any questions, don't hesitate to ask. "
                                      f"Have a great time here!",
                          color=0x00ff00)  # You can change the color as desired
        message = await general_channel.send(embed=embed)
        await asyncio.sleep(10)
        await message.delete()

#  Member Leave Notification
@bot_events.event
async def on_member_remove(member):
    #print(f"Member {member.display_name} has left the server.")
    channel = discord.utils.get(member.guild.channels, id=MEMBER_LEAVE_ID)
    mention = member.mention
    guild = member.guild
    embed = discord.Embed(title=str("***New Member Leaved***"), colour=0x33c946, description=str(f'{mention} leave from {guild}').format(mention=mention, guild=guild))
    try:
         embed.set_thumbnail(url=member.avatar)
    except:
        embed.remove_thumbnail()
        embed.set_thumbnail(url=member.default_avatar)
    embed.timestamp=datetime.datetime.utcnow()
    #embed.add_field(name='User ID :', value=member.id, inline=False)
    embed.add_field(name='User Name :', value=member.display_name, inline=True)
    embed.add_field(name='Server Name :', value=guild, inline=True)
    embed.add_field(name='User Serial :', value=len(list(guild.members)), inline=True)
    embed.add_field(name='Created_at :', value=member.created_at.strftime('%a, %#d %B %Y, %I:%M %p UTC'), inline=True)
    embed.add_field(name='leaved_at :', value=member.joined_at.strftime('%a, %#d %B %Y, %I:%M %p UTC'), inline=True)
    await channel.send(embed=embed)

# Function to load the blacklist words from a file
def load_blacklist(file_name):
    # Load the blacklist words from the file
    blacklist = []
    with open(file_name, 'r') as file:
        for line in file:
            word = line.strip()
            if word:
                blacklist.append(word)
    return blacklist

# Function to load the phishinglist words from a file
def load_phishinglist(file_name):
    # Load the phishinglist words from the file
    phishinglist = []
    with open(file_name, 'r') as file:
        for line in file:
            word = line.strip()
            if word:
                phishinglist.append(word)
    return phishinglist

# Create a dictionary to track user messages
message_history = {}
# Load the blacklist words from the 'blacklist.txt' file
blacklist = load_blacklist('blacklist.txt')
# Load the phishinglist words from the 'phishinglist.txt' file
phishinglist = load_phishinglist('phishinglist.txt')

# Event handler when a message is sent in a channel
@bot_events.event
async def on_message(message):
    # Ignore messages sent by bots
    if message.author.bot:
        return

    # Check if the message contains any blacklisted words
    for word in blacklist:
        if word in message.content.lower():
            # Delete the message
            await message.delete()

            # Create an embed to display information about the banned word
            embed = discord.Embed(color=0xff0000)
            embed.set_author(name="Banned Word")
            embed.add_field(name="Username:",
                            value=f"{message.author.mention}", inline=False)
            embed.add_field(name="Banned Word:", value=f"{word}", inline=True)
            embed.add_field(name="Message:",
                            value=f"{message.content}", inline=True)
            embed.add_field(name="Reason:",
                        value="Your message contained a banned word. Please refrain from using such language in the future.", inline=False)
            embed.set_footer(text=f'User ID: {message.author.id}')
            embed.timestamp = datetime.datetime.utcnow()
            embed_message = await message.channel.send(embed=embed)
            await asyncio.sleep(3)  # Delete the embed after 5 seconds
            await embed_message.delete()

            # Check if the user is already muted or banned
            if message.author.id in kicked_users:
                return

            # Increment the counter for the user
            if not filtered_words_counter.get(message.author.id):
                filtered_words_counter[message.author.id] = 1
            else:
                filtered_words_counter[message.author.id] += 1

            # Mute the user for 10 seconds if they reached the mute threshold (3 times)
            if filtered_words_counter[message.author.id] == 3:
                # Mute the user in the channel for 10 seconds
                await message.channel.set_permissions(message.author, send_messages=False)
                # Send mute message
                muted_embed = discord.Embed(color=0xff0000)
                muted_embed.add_field(name="Action: Mute", value=f"{message.author.mention} has been muted for using a prohibited word.", inline=False)
                muted_message = await message.channel.send(embed=muted_embed)
                # Wait for 5 seconds
                await asyncio.sleep(5)
                await muted_message.delete()  # Delete the mute message after 5 seconds
                await asyncio.sleep(5)  # Wait for 5 more seconds
                # Notify the user that they have been unmuted
                unmuted_embed = discord.Embed(color=0x00ff00)
                unmuted_embed.add_field(name="Action: Unmute", value=f"{message.author.mention} has been unmuted after 10 seconds.", inline=False)
                unmuted_message = await message.channel.send(embed=unmuted_embed)
                # Wait for 5 seconds
                await asyncio.sleep(5)
                await unmuted_message.delete()  # Delete the unmute message after 5 seconds
                await message.channel.set_permissions(message.author, send_messages=True)

            # Kick the user if they reached the ban threshold (5 times)
            elif filtered_words_counter[message.author.id] > 4:
                # Kick the user from the server
                kicked_users[message.author.id] = True
                member = message.guild.get_member(int(message.author.id))
                await member.kick(reason="Exceeded maximum allowed warnings.")
                # Delete all messages from the kicked user
                await message.channel.purge(check=lambda m: m.author == member)
                embed = discord.Embed(color=0xff0000)
                embed.set_author(name="Banned Users")
                embed.add_field(
                    name="Username:", value=f"{message.author.mention}", inline=False)
                embed.add_field(name="Banned Word:",
                                value=f"{word}", inline=True)
                embed.add_field(name="Message:",
                                value=f"{message.content}", inline=True)
                embed.add_field(name="Reason:",
                                value="You were kicked from the server for exceeding the maximum allowed warnings.", inline=False)
                embed.set_footer(text=f'User ID: {message.author.id}')
                embed.set_image(
                    url="https://media.tenor.com/9zCgefg___cAAAAC/bane-no.gif")
                embed_message = await message.channel.send(embed=embed)
                await asyncio.sleep(5)  # Delete the embed after 5 seconds
                await embed_message.delete()

                # Reset the counter to zero since the user has been kicked
                filtered_words_counter[message.author.id] = 0
    
    # Check if the message contains any blacklisted words
    for word in phishinglist:
        if word in message.content.lower():
            # Delete the message
            await message.delete()

            # Create an embed to display information about the banned word
            embed = discord.Embed(color=0x0000FF)
            embed.set_author(name="Phishing Word")
            embed.add_field(name="Username:",
                            value=f"{message.author.mention}", inline=False)
            embed.add_field(name="Banned Phishing:", value=f"{word}", inline=True)
            embed.add_field(name="Message:",
                            value=f"{message.content}", inline=True)
            embed.add_field(name="Reason:",
                        value="Your message contained a potentially dangerous element associated with phishing. Please exercise caution when sharing information.", inline=False)
            embed.set_footer(text=f'User ID: {message.author.id}')
            embed.timestamp = datetime.datetime.utcnow()
            embed_message = await message.channel.send(embed=embed)
            await asyncio.sleep(3)  # Delete the embed after 5 seconds
            await embed_message.delete()

            # Check if the user is already muted or banned
            if message.author.id in kicked_users:
                return

            # Increment the counter for the user
            if not filtered_words_counter.get(message.author.id):
                filtered_words_counter[message.author.id] = 1
            else:
                filtered_words_counter[message.author.id] += 1

            # Mute the user for 10 seconds if they reached the mute threshold (3 times)
            if filtered_words_counter[message.author.id] == 3:
                # Mute the user in the channel for 10 seconds
                await message.channel.set_permissions(message.author, send_messages=False)
                # Send mute message
                muted_embed = discord.Embed(color=0xff0000)
                muted_embed.add_field(name="Action: Mute", value=f"{message.author.mention} has been muted for using a prohibited word.", inline=False)
                muted_message = await message.channel.send(embed=muted_embed)
                # Wait for 5 seconds
                await asyncio.sleep(5)
                await muted_message.delete()  # Delete the mute message after 5 seconds
                await asyncio.sleep(5)  # Wait for 5 more seconds
                # Notify the user that they have been unmuted
                unmuted_embed = discord.Embed(color=0x00ff00)
                unmuted_embed.add_field(name="Action: Unmute", value=f"{message.author.mention} has been unmuted after 10 seconds.", inline=False)
                unmuted_message = await message.channel.send(embed=unmuted_embed)
                # Wait for 5 seconds
                await asyncio.sleep(5)
                await unmuted_message.delete()  # Delete the unmute message after 5 seconds
                await message.channel.set_permissions(message.author, send_messages=True)

            # Kick the user if they reached the ban threshold (5 times)
            elif filtered_words_counter[message.author.id] > 4:
                # Kick the user from the server
                kicked_users[message.author.id] = True
                member = message.guild.get_member(int(message.author.id))
                await member.kick(reason="Exceeded maximum allowed warnings.")
                # Delete all messages from the kicked user
                await message.channel.purge(check=lambda m: m.author == member)
                embed = discord.Embed(color=0x0000FF)
                embed.set_author(name="Banned Users")
                embed.add_field(
                    name="Username:", value=f"{message.author.mention}", inline=False)
                embed.add_field(name="Banned Phishing:",
                                value=f"{word}", inline=True)
                embed.add_field(name="Message:",
                                value=f"{message.content}", inline=True)
                embed.add_field(name="Reason:",
                                value="You were kicked from the server for exceeding the maximum allowed warnings.", inline=False)
                embed.set_footer(text=f'User ID: {message.author.id}')
                embed.set_image(
                    url="https://media.tenor.com/9zCgefg___cAAAAC/bane-no.gif")
                embed_message = await message.channel.send(embed=embed)
                await asyncio.sleep(5)  # Delete the embed after 5 seconds
                await embed_message.delete()

                # Reset the counter to zero since the user has been kicked
                filtered_words_counter[message.author.id] = 0
    
    # Anti-spam logic
    user_id = message.author.id
    if user_id not in message_history:
        message_history[user_id] = []
    
    # Limit the number of allowed messages in a certain timeframe
    message_history[user_id].append(message.created_at)
    if len(message_history[user_id]) > 5:  # Limit to 5 messages
        time_difference = message.created_at - message_history[user_id][0]
        if time_difference.total_seconds() < 10:  # Limit to 10 seconds
            # Delete messages if the user is spamming
            await message.delete()

            # Create an embed to display the spam warning
            embed = discord.Embed(color=0x00FF00)
            embed.set_author(name="Spam Word")
            embed.add_field(name="Username:",
                            value=f"{message.author.mention}", inline=False)
            embed.add_field(name="Banned Spam:", value=f"{word}", inline=True)
            embed.add_field(name="Message:",
                                value=f"{message.content}", inline=True)
            embed.add_field(name="Reason:",
                            value="Please refrain from spamming in the channel.", inline=False)
            embed.set_footer(text=f'User ID: {message.author.id}')
            embed.timestamp = datetime.datetime.utcnow()
            embed_message = await message.channel.send(embed=embed)
            await asyncio.sleep(3)  # Delete the embed after 5 seconds
            await embed_message.delete()

            # Check if the user is already muted or banned
            if message.author.id in kicked_users:
                return

            # Increment the counter for the user
            if not filtered_words_counter.get(message.author.id):
                filtered_words_counter[message.author.id] = 1
            else:
                filtered_words_counter[message.author.id] += 1

            # Mute the user for 10 seconds if they reached the mute threshold (3 times)
            if filtered_words_counter[message.author.id] == 3:
                # Mute the user in the channel for 10 seconds
                await message.channel.set_permissions(message.author, send_messages=False)
                # Send mute message
                muted_embed = discord.Embed(color=0xff0000)
                muted_embed.add_field(name="Action: Mute", value=f"{message.author.mention} has been muted for using a prohibited word.", inline=False)
                muted_message = await message.channel.send(embed=muted_embed)
                # Wait for 5 seconds
                await asyncio.sleep(5)
                await muted_message.delete()  # Delete the mute message after 5 seconds
                await asyncio.sleep(5)  # Wait for 5 more seconds
                # Notify the user that they have been unmuted
                unmuted_embed = discord.Embed(color=0x00ff00)
                unmuted_embed.add_field(name="Action: Unmute", value=f"{message.author.mention} has been unmuted after 10 seconds.", inline=False)
                unmuted_message = await message.channel.send(embed=unmuted_embed)
                # Wait for 5 seconds
                await asyncio.sleep(5)
                await unmuted_message.delete()  # Delete the unmute message after 5 seconds
                await message.channel.set_permissions(message.author, send_messages=True)
            
            return
        else:
            message_history[user_id].pop(0)

    # Let the bot process commands after handling messages
    await bot_events.process_commands(message)


@bot_events.event
async def on_raw_reaction_add(payload):
    user_id = payload.user_id
    channel_id = payload.channel_id
    guild_id = payload.guild_id
    emoji = payload.emoji.name

    # Check if the reaction is in the roles channel and the specified message
    if channel_id == ROLES_CHANNEL_ID and payload.message_id == REACT_CHANNEL_ID:
        guild = bot_events.get_guild(guild_id)
        member = guild.get_member(user_id)

        # Check if the emoji is in the roles dictionary
        if emoji in emoji_to_role:
            role_name = emoji_to_role[emoji]
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                await member.add_roles(role)

    # Check if the reaction is in the welcome channel and the specified message
    if channel_id == WELCOME_CHANNEL_ID and payload.message_id == RULES_CHANNEL_ID:
        guild = bot_events.get_guild(guild_id)
        member = guild.get_member(user_id)

        # Check if the emoji is in the verification dictionary
        if emoji in emoji_to_verif:
            role_name = emoji_to_verif[emoji]
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                await member.add_roles(role)

@bot_events.event
async def on_raw_reaction_remove(payload):
    user_id = payload.user_id
    channel_id = payload.channel_id
    guild_id = payload.guild_id
    emoji = payload.emoji.name

    # Check if the reaction is in the roles channel and the specified message
    if channel_id == ROLES_CHANNEL_ID and payload.message_id == REACT_CHANNEL_ID:
        guild = bot_events.get_guild(guild_id)
        member = guild.get_member(user_id)

        # Check if the emoji is in the roles dictionary
        if emoji in emoji_to_role:
            role_name = emoji_to_role[emoji]
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                await member.remove_roles(role)

    # Check if the reaction is in the welcome channel and the specified message
    if channel_id == WELCOME_CHANNEL_ID and payload.message_id == RULES_CHANNEL_ID:
        guild = bot_events.get_guild(guild_id)
        member = guild.get_member(user_id)

        # Check if the emoji is in the verification dictionary
        if emoji in emoji_to_verif:
            role_name = emoji_to_verif[emoji]
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                await member.remove_roles(role)

# Command to send the annoucements message
@bot_commands.command()
async def annoucements(ctx):
    # Find the roles channel in the server
    annoucements_channel = discord.utils.get(ctx.guild.channels, id=ANNOUCEMENTS_CHANNEL_ID)
    if annoucements_channel:
        # Create an embed with the roles message in multiple parts
        message = discord.Embed(title="ProxySec server event/announcement",
                                description=" New Discord Server ",
                                color=0xFF0000)
        message.add_field(name="🇬🇧  Dear esteemed members (Part 1)",
                          value=EN_RULES_PART00, inline=False)
        message.add_field(name="🇬🇧  Dear esteemed members (Part 2)",
                          value=EN_RULES_PART01, inline=False)
        message.add_field(
            name="_", value="A problem? Contact our staff in #support-staff channel!", inline=False)
        await annoucements_channel.send(embed=message)
    else:
        await ctx.send("Channel 'annoucements' not found in the server.")

# Command to send the welcome message
@bot_commands.command()
async def welcome(ctx):
    # Find the welcome channel in the server
    welcome_channel = discord.utils.get(
        ctx.guild.channels, id=WELCOME_CHANNEL_ID)
    if welcome_channel:
        # Create an embed with the welcome message in multiple parts
        message = discord.Embed(title="ProxySec server rules organisation",
                                description="Like any community, the use of this ProxySec server is subject to rules that must be carefully respected.",
                                color=0xFF0000)
        message.add_field(name="🇬🇧  Rules for using this Discord server (Part 1)",
                          value=EN_RULES_PART1, inline=False)
        message.add_field(name="🇬🇧  Rules for using this Discord server (Part 2)",
                          value=EN_RULES_PART2, inline=False)
        message.add_field(name="🇬🇧  Rules for using this Discord server (Part 3)",
                          value=EN_RULES_PART3, inline=False)
        message.add_field(
            name="_", value="A problem? Contact our staff in #support-staff channel!", inline=False)
        await welcome_channel.send(embed=message)
    else:
        await ctx.send("Channel 'welcome-and-rules' not found in the server.")

# Command to send the roles message
@bot_commands.command()
async def roles(ctx):
    # Find the roles channel in the server
    roles_channel = discord.utils.get(ctx.guild.channels, id=ROLES_CHANNEL_ID)
    if roles_channel:
        # Create an embed with the roles message in multiple parts
        message = discord.Embed(title="ProxySec server roles organisation",
                                description="We give specific roles to users, they all have a utility and are used for the proper functioning of the server.",
                                color=0xFF0000)
        message.add_field(name="🇬🇧  Status roles (Part 1)",
                          value=EN_RULES_PART4, inline=False)
        message.add_field(name="🇬🇧  Status roles (Part 2)",
                          value=EN_RULES_PART5, inline=False)
        message.add_field(
            name="_", value="A problem? Contact our staff in #support-staff channel!", inline=False)
        await roles_channel.send(embed=message)
    else:
        await ctx.send("Channel 'roles' not found in the server.")

# Command to send the react message
@bot_commands.command()
async def react(ctx):
    react_channel = discord.utils.get(ctx.guild.channels, id=ROLES_CHANNEL_ID)
    if react_channel:
        # Create an embed with the roles message in multiple parts
        message = discord.Embed(title="ProxySec server roles organisations",
                                description="React to this message to get the Event and/or Announcement roles according to your needs.",
                                color=0xFF0000)
        message.add_field(name="🇬🇧  Status roles (Part 3)",
                          value=EN_RULES_PART6, inline=False)
        message.add_field(
            name="_", value="A problem? Contact our staff in #support-staff channel!", inline=False)
        await react_channel.send(embed=message)
    else:
        await ctx.send("Channel 'react' not found in the server.")

EN_RULES_PART00 = """
➥ Annoucements n°1: Platform
We are delighted to announce the launch of our latest venture: Cybersecurity and Technology Discord server! 🚀
This platform has been meticulously curated to foster a community of dedicated professionals, experts, and enthusiasts in the realms of cybersecurity and technology. 
Whether you're a seasoned industry veteran or an inquisitive newcomer, 
we extend a warm welcome to collaborate, exchange knowledge, and engage in insightful discussions pertaining to the ever-evolving landscape of information security.
➥ Annoucements n°2: Offer
🌐 Thought-provoking dialogues on cutting-edge cybersecurity methodologies and technological advancements
🔒 Pragmatic strategies for fortifying your systems and networks
💡 Curated resources, peer-reviewed articles, and curated news feeds focused on cybersecurity
💬 Tailored channels for in-depth discussions concerning technology trends and security best practices
"""
EN_RULES_PART01 = """
➥ Annoucements n°3: Conclusion
Join us now and become an integral part of this thriving professional community! We also encourage you to extend invitations to like-minded peers and colleagues.
We anticipate a stimulating exchange of ideas and the forging of valuable connections within the domain of cybersecurity and technology.
Looking forward to your participation!
"""
EN_RULES_PART1 = """
➥ Rule n°1: General attitude
Comply with the Discord Community Guidelines. Have a correct attitude on the server.
➥ Rule n°2: ProxySec Terms of Service
Respect the ProxySec Legal Disclaimer and the Terms of Service. No cheats, leaks, or illegal requests.
"""
EN_RULES_PART2 = """
➥ Rule n°3: Spamming
No spam. Any advertising for an external service for financial or malicious purposes is prohibited.
"""
EN_RULES_PART3 = """
➥ Rule n°5: Unsolicited private messages
It is forbidden to spontaneously send a private message to a person who does not invite you to do so, in order to ask for help. Use the channels available to you.
➥ Rule n°6: Vulnerability exploitation
Any vulnerability exploitation in bots, discord, or any ProxySec related system for malicious purposes (like abusing bots for pinging everyone, even for joking) will result in a permanent ban.
➥ Rule n°7: Political reference
Talks about politics or any reference to your political opinion is forbidden.
"""
EN_RULES_PART4 = f"""
➥ Roles n°1 : <@&{VISITOR_ROLE_ID}>
This role is given to anyone with an account on the site. It makes it easier for people to recognize your account in order to provide challenge help or staff support.
➥ Roles n°2 : <@&{MEMBER_ROLE_ID}>
This role is given to anyone who has a valid paid membership fee. More information on the membership page. This role provides access to member private channels.
➥ Roles n°3 : <@&{ADMINISTRATOR_ROLE_ID}>
This role is reserved for the head staff and gives administrator privileges on the discord server.
"""
EN_RULES_PART5 = f"""
➥ Roles n°4 : <@&{TRIAL_MODERATOR_ROLE_ID}>
This role is given to new moderators while they are in a trial period.
➥ Roles n°5 : <@&{MODERATOR_ROLE_ID}>
This role provides access to the moderation of the discord server. It is granted to members of the association motivated to participate in the active moderation of the server.
➥ Roles n°6 : <@&{LEAD_MODERATOR_ROLE_ID}>
This role can appoint new moderators and have more permissions on the discord server (like managing channels and roles below them). They act as managers for the moderation team.
"""
EN_RULES_PART6 = f"""
➥ Roles n°1 : <@&{DEVOPS_ROLE_ID}> 💻
This role is given to responsible for the integration and collaboration between software development and IT operations to streamline processes and enhance software deployment..
➥ Roles n°2 : <@&{INFOSEC_ROLE_ID}> 🛡️
This role provides access to the ensures the confidentiality, integrity, and availability of data and systems by implementing security measures and mitigating cyber threats..
➥ Roles n°3 : <@&{DATA_ROLE_ID}> 📊
This role can appoint new analyzes and interprets data to provide valuable insights and make data-driven decisions, aiding businesses in improving performance and strategies
➥ Roles n°4 : <@&{BOT_ROLE_ID}> 🤖
This role can appoint new designs, creates, and maintains bots and automation tools to enhance user experiences and functionality on various platforms, including Discord.
"""

# Function to start both bots concurrently
async def start_bots():
    
    await asyncio.gather(
        bot_events.start(ID_TOKEN_EVENTS),
        bot_commands.start(ID_TOKEN_COMMANDS)
    )

# Use asyncio.run to run the start_bots function
asyncio.run(start_bots())
