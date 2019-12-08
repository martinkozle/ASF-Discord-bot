import discord
from discord.ext import commands
import requests
import json
from time import sleep


# ctx methods
# ['fetch_message', 'history', 'invoke', 'pins', 'reinvoke', 'send', 'send_help', 'trigger_typing', 'typing']

def settings(key):
    return settingsJson[key] if key in settingsJson else key + " not set"


def log(command, author, message=""):
    print(str(author) + " requested: " + botPrefix + command + " " + message)


class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.commandsHelp = [
            ('help', 'Shows this message'),
            ('ping', 'Writes back pong!'),
            ('2fa', 'Request two factor authentication for an account'),
            ('asf', 'Request an asf command')
        ]
        self.voiceClients = {}

    @commands.command(pass_context=True)
    async def help(self, ctx):
        log("help", ctx.message.author)
        embed = discord.Embed(colour=discord.Color.orange())
        embed.set_author(name='Help')
        for commandHelp in self.commandsHelp:
            embed.add_field(name=commandHelp[0], value=commandHelp[1], inline=False)
        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        log("ping", ctx.message.author)
        await ctx.send('pong!')

    @commands.command(pass_context=True, name="2fa")
    async def _2fa(self, ctx, *, message=""):
        if str(ctx.message.channel.id) not in settings("allowedChannels"):
            return
        log("2fa", ctx.message.author, message)
        author = str(ctx.message.author.id)
        if message is "":
            output = "Allowed requests: " + \
                     str(settings("allowedAccounts")[author]) if author in settings("allowedAccounts") else "[]"
        elif author in settings("allowedAccounts") and (
                (settings("allowedAccounts")[author] == "All") or (message in settings("allowedAccounts")[author])):
            responseJson = requests.get(settings("2faApi").format(message)).json()
            if responseJson["Success"] and responseJson["Result"][message]["Success"]:
                output = responseJson["Result"][message]["Result"]
            else:
                output = "API request unsuccessful, user possibly misspelled?"
        else:
            output = "You do not have permission to use this command."
        print("\t" + output)
        await ctx.send(output)

    async def on_message(self, message):
        print(message.content)

    @commands.command(pass_context=True)
    async def asf(self, ctx, *, message=""):
        if str(ctx.message.channel.id) not in settings("allowedChannels"):
            return
        log("asf", ctx.message.author, message)
        author = str(ctx.message.author.id)
        if author in settings("allowedAccounts") and settings("allowedAccounts")[author] == "All":
            response = requests.post(settings("asfApi"), json={"Command": message}, headers={"Content-Type": "application/json"})
            responseJson = response.json()
            if responseJson["Success"]:
                output = responseJson["Result"]
            else:
                output = "API request unsuccessful."
        else:
            output = "You do not have permission to use this command."
        print("\t" + output)
        codeBlock = "```"
        for line in output.split("\n"):
            codeBlock += line
            if len(codeBlock) > 1500:
                await ctx.send(codeBlock + "```")
                codeBlock = "```"
        await ctx.send(codeBlock + "```")


try:
    settingsJson = json.load(open("settings.json", 'r'))
except FileNotFoundError:
    print("settings.json doesn't exist in script location")
    exit()
    
    
botPrefix = settings("Prefix")
bot = commands.Bot(command_prefix=botPrefix)
bot.remove_command('help')
bot.add_cog(MainCog(bot))
token = settings("Token")
botName = settings("BotName")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="!help"))
    print(botName + " has connected to:")
    for guild in bot.guilds:
        print("\t" + str(guild), end=" - id:")
        print(guild.id)


try:
    bot.run(token, bot=True, reconnect=True)
except KeyboardInterrupt:
    bot.close()
    sleep(0.5)
