import nextcord
from nextcord.ext import commands
from pymongo import MongoClient
import dotenv
import server
import os

# load environment variables
dotenv.load_dotenv()

# connect to database
connetion = MongoClient(os.environ['DB_URI'])
db = connetion['pynux-db']
t_guilds = db['guilds']

bot = commands.Bot("/", intents=nextcord.Intents.all())

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}, ID = {bot.user.id}")

if __name__ == "__main__":
    server.run_as_thread()
    bot.run(os.environ['DISCORD_TOKEN'])