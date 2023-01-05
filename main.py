import nextcord
from nextcord.ext import commands
import dotenv
import os

# load environment variables
dotenv.load_dotenv()

bot = commands.Bot("/", intents=nextcord.Intents.all())

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}, ID = {bot.user.id}")

if __name__ == "__main__":
    bot.run(os.environ['DISCORD_TOKEN'])