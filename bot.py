import cfg
import discord
import datetime as dt
import re
from discord import app_commands
from discord import Interaction
from discord.app_commands.errors import MissingAnyRole
from discord.app_commands.checks import has_any_role

import db

TEST_GUILDS_ID = [1, 2, 3]
TEST_GUILDS = [discord.Object(gid) for gid in TEST_GUILDS_ID]
print([guild.created_at for guild in TEST_GUILDS])
class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    @staticmethod
    async def on_message(message):
        print(f'Message from {message.author}: {message.content}')


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)

tree = app_commands.CommandTree(client)


# @tree.command(name='test', \
#               description='test description', \
#               guild=discord.Object(id=cfg.guilds['sh']))
# async def test(interaction, name: str):
#     await interaction.response.send_message(f'Hi, {name}!')


@tree.command(name='vasserman',
              description='vasserman event',)
async def vasserman(interaction: discord.Interaction,
                    user: discord.User = None,
                    addpoints: float | None = 0.0,
                    removepoints: float | None = 0.0):
    points_delta = addpoints - removepoints
    points_delta = points_delta if points_delta % 1 != 0 else int(points_delta)
    if not user:
        try:
            connect = db.DBConnect()
            select = connect.select(f'SELECT * FROM Vasserman WHERE vsm_points!=0').fetchall()
            select = sorted(select, key=lambda x: x[2], reverse=True)
            print(select)
            desc = f''
            for res in select:
                desc += f'<@{res[0]}>: {res[2] if res[2] % 1 != 0 else int(res[2])}\n'
            print(desc)
            await interaction.response.send_message(embed=discord.Embed(title='Вассерман!', description=desc))
        except ConnectionError:
            print('[ERROR] There was an error during db connect!')
            await interaction.response.send_message \
                (f'При выполнении команды произошла ошибка!')
        
    if not interaction.user.get_role(943843555829510214):
        await interaction.response.send_message('У вас недостаточно прав!')
    try:
        connect = db.DBConnect()
        select = connect.select(f'SELECT * FROM Vasserman WHERE user_id={user.id}').fetchone()
        if select:
            connect.update('Vasserman', f'vsm_points={select[2] + points_delta}', user.id)
        else:
            connect.insert('Vasserman', (user.id, 0, points_delta))
    except ConnectionError:
        print('[ERROR] There was an error during db connect!')
        await interaction.response.send_message \
            (f'При выполнении команды произошла ошибка!')
    # except ValueError:
    #     print('[ERROR] Incorrect values!')
        await interaction.response.send_message \
            (f'При выполнении команды произошла ошибка!')
    else:
        if points_delta >= 0:
            await interaction.response.send_message \
                (embed=discord.Embed(title='Вассерман!',
                                     description=f'К счёту участника {user.mention}\
                                         было добавлено {points_delta} очков!'))
        else:
            await interaction.response.send_message \
                (embed=discord.Embed(title='Вассерман!',
                                     description=f'Со счёта участника {user.mention}\
                                         было вычтено {abs(points_delta)} очков!'))


@tree.command(name='add_emoji',
              description='adds custom emoji')
async def add_emoji(interaction: Interaction, emoji: str, name: str = None):
    try:
        print(re.findall(r":\d+", emoji))
        emoji_id = int(re.findall(r":\d+", emoji).pop(0).strip(":"))
        print(emoji_id)
        emj = interaction.client.get_emoji(emoji_id)
        print(emj)
        if name == None:
            name = emj.name
        await interaction.guild.create_custom_emoji(name=name, image=await emj.read())
    except (Exception) as e:
        print(f"[ERROR] {e}")
        await interaction.response.send_message("Произошла ошибка!")
    else:
        await interaction.response.send_message("Эмодзи был успешно добавлен!")
        
# @vasserman.error
# async def on_application_command_error(ctx: Interaction, error: discord.DiscordException):
#     if isinstance(error, MissingAnyRole):
#         await ctx.edit_original_response("Sorry, only the bot owner can use this command!")
#     else:
#         raise error

@client.event
async def on_ready():
    tree.clear_commands(guild=TEST_GUILDS[2])
    await tree.sync(guild=TEST_GUILDS[2])
    print('Ready!')

@client.event
async def on_message(ctx):
    datetime_format = "%d-%m-%y %H:%M:%S"
    if ctx.guild.id == 542919556155310101:
        with open('msg_log.txt', 'a', encoding='utf-8') as log:
            log.write(f'[{ctx.created_at.strftime(datetime_format)}] {ctx.author}: {ctx.content}\n')
        
        
client.run(cfg.TOKEN)
