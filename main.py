import nextcord
from nextcord.ext import commands
from pymongo import MongoClient
from paw import PAW
import dotenv
import server
import os

# defined constants
MAX_USERNAME_SIZE = 60     # maximum username size
MIN_USERNAME_SIZE = 5      # minimum username size
MAX_PASSWORD_SIZE = 255    # maximum password size
MIN_PASSWORD_SIZE = 1      # minimum password size
MODAL_TIMEOUT = 60 * 5     # setup window display time
MIN_TERMINAL_NAME_SIZE = 1 # minimum terminal name size
ERROR_MSG_DELAY = 30       # error message display time

# load environment variables
dotenv.load_dotenv()

# connect to database
connetion = MongoClient(os.environ['DB_URI'])
db = connetion['pynux-db']
t_guilds = db['guilds']

# create bot instance
bot = commands.Bot("/", intents=nextcord.Intents.all())

@bot.event
async def on_ready():
    """
    ready to work
    """
    print(f"logged in as {bot.user}, ID = {bot.user.id}")

@bot.event
async def on_guild_join(guild: nextcord.Guild):
    """
    handling when it join the server
    """
    # add guild to guilds table
    t_guilds.insert_one({
        "id": str(guild.id),
        "terminal_id": None,
        "username": None,
        "password": None,
    })

    # find inviter
    integrations: list[nextcord.Integration] = await guild.integrations()
    for integration in integrations:
        if isinstance(integration, nextcord.BotIntegration):
            if integration.application.user.name == bot.user.name:
                inviter: nextcord.Member = integration.user
                break

    # send setup message to inviter
    view = setup_view(guild, inviter)
    view.msg = await inviter.send(f"To run pynux on '{guild.name}' server, click the setup button", view=view)

@bot.event
async def on_guild_remove(guild: nextcord.Guild):
    """
    handling when it kick from the server
    """
    # remove server data from database
    try:
        t_guilds.delete_one({'id': str(guild.id)})
    except:
        pass

@bot.event
async def on_message(message: nextcord.Message):
    if message.channel.id != message.author.dm_channel.id: # not dm message
        pass

class setup_view(nextcord.ui.View):
    """
    setup message for on_guild_join
    """
    def __init__(self, guild: nextcord.Guild, inviter: nextcord.Member):
        super().__init__(timeout=None)
        # save msg and inviter for deleting setup message and send `completed successfully message` after setup complete
        self.msg: nextcord.Message = None
        self.inviter = inviter
        self.guild = guild
        self.btn = nextcord.ui.Button(style=nextcord.ButtonStyle.primary, label="Setup", custom_id="setup_btn")

        async def setup(interaction: nextcord.Interaction):
            """
            on click setup button
            """
            # send setup dialog
            await interaction.response.send_modal(setup_dialog(self.callback_call, self.timeout_call))
        self.btn.callback = setup
        self.add_item(self.btn)

    async def callback_call(self, username: str, password: str, terminal_name: str, interaction: nextcord.Integration):
        """
        on submit setup form
        """
        # send `wait to login` message
        self.after_msg = await interaction.send("ok! wait to login ...")
        # disable setup button
        self.btn.disabled = True
        await self.msg.edit(view=self)
        # login
        self.login(username, password, terminal_name)

    async def timeout_call(self):
        """
        on timeout setup form
        """
        pass

    def login(self, username: str, password: str, channel_name: str):
        """
        login into pythonanywhere account and upload server files
        """
        async def inner():
            """
            login task
            """
            try:
                # try to login
                paw = PAW(username, password)
            except Exception as ex: # on login error
                # send error message
                await self.after_msg.edit(f"Error: {ex.args[0]}", delete_after=ERROR_MSG_DELAY)
                # enable setup button
                self.btn.disabled = False
                await self.msg.edit(view=self)
            else: # login successfully
                # send `login successfully message`
                await self.after_msg.edit("login was successful! create/recreate server ...")
                try: # try to delete server
                    paw.delete_server()
                except:
                    pass
                # create/recreate server
                paw.create_server()
                await self.after_msg.edit("server was created! writing data ...")
                try:
                    # try to edit server file
                    paw.edit_file(f"/home/{username}/server/main.py", open("static/scripts/server/main.py", "rb").read())
                except: # error on edit server file
                    # send error message
                    await self.after_msg.edit("Error: cant' write server file!", delete_after=ERROR_MSG_DELAY)
                    # enable setup button
                    self.btn.disabled = False
                    await self.msg.edit(view=self)
                else: # setup successfully
                    try: # try to create terminal channel
                        channel: nextcord.TextChannel = await self.guild.create_text_channel(channel_name)
                    except: # error on creating channel
                        # send error message
                        await self.after_msg.edit("Error: can't create terminal channel!", delete_after=ERROR_MSG_DELAY)
                        # enable setup button
                        self.btn.disabled = False
                        await self.msg.edit(view=self)
                    else:
                        # update database
                        t_guilds.update_one({'id': str(self.guild.id)}, {'$set': {'terminal_id': channel.id, 'username': username, 'password': password}})
                        # delete extera messages
                        await self.msg.delete()
                        await self.after_msg.delete()
                        # send `setup successfully` message
                        await self.inviter.send(f"pynux setup on '{self.guild.name}' server is complete!")
        
        # pass setup task to bot async loop
        bot.loop.create_task(inner())

    

class setup_dialog(nextcord.ui.Modal):
    """
    setup window
    """
    def __init__(self, on_callback_call: callable, on_timeout_call: callable):
        # save callback function for handle events
        self.on_callback_call = on_callback_call
        self.on_timeout_call = on_timeout_call

        # set modal title and that display time
        super().__init__("Setup Pynux", timeout=MODAL_TIMEOUT)

        # create inputs
        self.inp_username = nextcord.ui.TextInput("Username", min_length=MIN_USERNAME_SIZE, max_length=MAX_USERNAME_SIZE, required=True, placeholder="username of pythonanywhere account")
        self.add_item(self.inp_username)
        self.inp_passwd = nextcord.ui.TextInput("Password", min_length=MIN_PASSWORD_SIZE, max_length=MAX_PASSWORD_SIZE, required=True, placeholder="password of pythonanywhere account")
        self.add_item(self.inp_passwd)
        self.inp_terminal_name = nextcord.ui.TextInput("Terminal channel", min_length=MIN_TERMINAL_NAME_SIZE, required=True, placeholder="text channel for running commands", default_value="Shell")
        self.add_item(self.inp_terminal_name)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        """
        handle on submit setup form
        """
        # run callback
        await self.on_callback_call(self.inp_username.value, self.inp_passwd.value, self.inp_terminal_name.value, interaction)

    async def on_timeout(self) -> None:
        """
        handle on timeout
        """
        # run callback
        await self.on_timeout_call()



if __name__ == "__main__":
    server.run_as_thread() # run keep alive server as a thread
    try: # try to run application
        bot.run(os.environ['DISCORD_TOKEN'])
    except nextcord.errors.HTTPException: # handle HTTPException (429 too many requests)
        os.system("kill 1") # switch to new container