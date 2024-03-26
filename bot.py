import requests
import discord
import asyncio
import disnake
from datetime import datetime

# Discord bot token
TOKEN = 'your_bot_token_here'
# Channel ID where you want to send/edit the message
CHANNEL_ID = 123456789  # Replace with your channel ID
# Change server ip to your domain or your IP Adress
SERVER_IP = "YOUR_SERVER_IP_OR_DOMAIN"

API_URL = "https://api.mcsrvstat.us/2/"+SERVER_IP #API by https://api.mcsrvstat.us/ more information on the link

# Channel ID where you want to send/edit the message
CHANNEL_ID = 123456789  # Replace with your channel ID

# API URL to fetch the list of players, change server ip to your domain or your IP Adress
API_URL = "https://api.mcsrvstat.us/2/your_server_ip_here" #API by https://api.mcsrvstat.us/ more information on the link

# Initialize the Discord client
intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

# Function to fetch the list of all players by name from the API
async def fetch_players():
    try:
        response = requests.get(API_URL)
        data = response.json()
        player_list = data['players']['list'] if 'list' in data['players'] else []
        return player_list
    except Exception as e:
        print(f"Failed to fetch player data: {e}")
        return []

# Function to fetch the status of the server whether its online or not from the API
async def fetch_status():
    try:
        response = requests.get(API_URL)
        data = response.json()
        status=data['online']
        return status
    except Exception as e:
        print(f"Failed to fetch server status: {e}")
        return False

# Function to fetch the online player/max player ex (6/64) from the API, this will be displayed on bot activity
async def fetch_activity():
    try:
        response = requests.get(API_URL)
        data = response.json()
        online=data['players']['online']
        maxplayer=data['players']['max']
        actstatus=str(online)+"/"+str(maxplayer)
        return actstatus
    except Exception as e:
        print(f"Failed to fetch activity status: {e}")
        return []

# Event triggered when the bot is ready
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

    # Set bot's activity to the number of online players
    await client.change_presence(activity=discord.Game(name="Loading..."))

    # Fetch the channel where you want to send/edit the message
    channel = client.get_channel(CHANNEL_ID)

    # Delete old message if exists
    async for message in channel.history():
        if message.author == client.user:
            await message.delete()
            break

    while True:
        # Fetch the list of players from the API
        allplayer = ""
        player_list = await fetch_players()
        status = await fetch_status()
        actstatus = await fetch_activity()
        #change the logo to your logo in icon_url, this is just a default avatar logo
        icon = "https://png.pngtree.com/png-vector/20210129/ourmid/pngtree-upload-avatar-by-default-png-image_2854358.jpg"
        k=1
        for j in player_list:
            allplayer += str(k)+" • "+ j + "\n"
            k+=1
        timenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create an embed
        embed = disnake.Embed(title="Server Player List", description="List of players currently online", color=0x00FFFF)
        #change the logo to your logo in icon_url, this is just a default avatar logo
        embed.set_author(name="author_name", url="https://example.com", icon_url=icon) 
        if status == True:
            embed.add_field(name="Server Status", value="✅Online", inline=False)
        else:
            embed.add_field(name="Server Status", value="❌Offline", inline=False)
        embed.set_footer(text=timenow, icon_url=icon)
        
        # Add fields for each player
        if player_list:
            embed.add_field(name="List", value=allplayer, inline=False)
        else:
            embed.add_field(name="No players online", value="No players are currently online.", inline=False)

        # Check if the bot has already sent a message
        if hasattr(client, 'last_message_id'):
            # If yes, edit the message
            message = await channel.fetch_message(client.last_message_id)
            await message.edit(embed=embed)
        else:
            # If not, send a new message
            message = await channel.send(embed=embed)
            client.last_message_id = message.id

        # Set bot's activity to the number of online players and server is offline if the server is offline
        if actstatus:
            await client.change_presence(activity=discord.Game(name=f"Online Players: "+actstatus,))
        else:
            await client.change_presence(activity=discord.Game(name=f"Server is Offline"))
            
        # Wait for 180 seconds before fetching the list again, the list will be updated once in 3 minutes.
        await asyncio.sleep(180)

# Run the Discord bot
client.run(TOKEN)
