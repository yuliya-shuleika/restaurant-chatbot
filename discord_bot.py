import discord
import requests

# Rasa endpoint
RASA_URL = "http://0.0.0.0:5005/webhooks/rest/webhook"

# Discord bot token
DISCORD_TOKEN = "MTMzNTM2ODY1NDE0NDkyOTkxNA.Gbtust.D51pCRKcuyTJ6DeA6gZ77SX9MZMKm7nzPAzEYk"

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    print(f"Received message from {message.author}: {message.content}")

    # Don't let the bot respond to itself
    if message.author == client.user:
        return

    # Send the message to Rasa for processing
    payload = {
        'sender': message.author.name,
        'message': message.content
    }
    response = requests.post(RASA_URL, json=payload)

    # If Rasa responds with a message, send it back to Discord
    if response.status_code == 200:
        rasa_reply = response.json()
        for reply in rasa_reply:
            await message.channel.send(reply.get('text'))

# Start the bot
client.run(DISCORD_TOKEN)
