import aiohttp
import discord
from discord import Interaction, app_commands
from discord.app_commands.checks import has_any_role
from discord.app_commands.errors import MissingAnyRole

import cfg
import db

TEST_GUILDS_ID = cfg.TEST_GUILDS_ID
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
            select = connect.select(
                f'SELECT * FROM Vasserman WHERE vsm_points!=0').fetchall()
            select = sorted(select, key=lambda x: x[2], reverse=True)
            print(select)
            desc = f''
            for res in select:
                desc += f'<@{res[0]}>: {res[2] if res[2] %
                                        1 != 0 else int(res[2])}\n'
            print(desc)
            await interaction.response.send_message(embed=discord.Embed(title='Вассерман!', description=desc))
        except ConnectionError:
            print('[ERROR] There was an error during db connect!')
            await interaction.response.send_message(f'При выполнении команды произошла ошибка!')

    if not interaction.user.get_role(943843555829510214):
        await interaction.response.send_message('У вас недостаточно прав!')
    try:
        connect = db.DBConnect()
        select = connect.select(
            f'SELECT * FROM Vasserman WHERE user_id={user.id}').fetchone()
        if select:
            connect.update('Vasserman', f'vsm_points={
                           select[2] + points_delta}', user.id)
        else:
            connect.insert('Vasserman', (user.id, 0, points_delta))
    except ConnectionError:
        print('[ERROR] There was an error during db connect!')
        await interaction.response.send_message(f'При выполнении команды произошла ошибка!')
    except ValueError:
        print('[ERROR] Incorrect values!')
        await interaction.response.send_message(f'При выполнении команды произошла ошибка!')
    else:
        if points_delta >= 0:
            await interaction.response.send_message(embed=discord.Embed(title='Вассерман!',
                                                                        description=f'К счёту участника {user.mention}\
                                         было добавлено {points_delta} очков!'))
        else:
            await interaction.response.send_message(embed=discord.Embed(title='Вассерман!',
                                                                        description=f'Со счёта участника {user.mention}\
                                         было вычтено {abs(points_delta)} очков!'))


@tree.command(name='add_emoji',
              description='adds custom emoji')
async def add_emoji(interaction: Interaction, emoji: str, name: str = None):
    try:
        emj_anim, emj_name, emj_id = emoji.strip('<>').split(':')
        print(emj_id)
        emj_format = 'webp' if not emj_anim else 'gif'
        url = f'https://cdn.discordapp.com/emojis/{emj_id}.{emj_format}'
        if name == None:
            name = emj_name
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                emoji = await interaction.guild.create_custom_emoji(name=name, image=await resp.read())
    except (Exception) as e:
        print(f"[ERROR] {e}")
        await interaction.response.send_message("Произошла ошибка!")
    else:
        await interaction.response.send_message("Эмодзи <{}:{}:{}> был успешно добавлен!".format(emj_anim, emj_name, emj_id))


@client.event
async def on_ready():
    tree.clear_commands(guild=TEST_GUILDS[1])
    await tree.sync(guild=TEST_GUILDS[1])
    print('Ready!')


@client.event
async def on_message(ctx):
    datetime_format = "%d-%m-%y %H:%M:%S"
    if ctx.guild.id == 542919556155310101:
        with open('msg_log.txt', 'a', encoding='utf-8') as log:
            log.write(f'[{ctx.created_at.strftime(datetime_format)}] {
                      ctx.author}: {ctx.content}\n')


client.run(cfg.TOKEN)
