import cfg
import discord
from discord import app_commands
import db

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)

tree = app_commands.CommandTree(client)

@tree.command(name='test',\
    description='test description',\
    guild=discord.Object(id=cfg.guilds['sh']))
async def test(interaction, name: str):
    await interaction.response.send_message(f'Hi, {name}!')

@tree.command(name='vasserman',\
    description='vasserman event')
async def vasserman(interaction: discord.Integration, user: discord.User, points: int):
    try:
        connect = db.DBConnect()
        select = connect.select(f'SELECT * FROM Users WHERE user_id={user.id}').fetchone()
        if select:
            connect.update('Users', f'vsm_points={select[2] + points}', user.id)
        else:
            connect.insert('Users', (user.id, 0, points))
    except ConnectionError:
        print('[ERROR] There was error during db connect!')
        await interaction.response.send_message\
        (f'При выполнении команды произошла ошибка!')
    except ValueError:
        print('[ERROR] Incorrect values!')
        await interaction.response.send_message\
        (f'При выполнении команды произошла ошибка!')
    else:
        if points >= 0:
            await interaction.response.send_message\
            (embed = discord.Embed(title='Вассерман!',\
            description=f'К счёту участника {user} было добавлено {points} очков!'))
        else:
            await interaction.response.send_message\
            (embed = discord.Embed(title='Вассерман!',\
            description=f'Со счёта участника {user.mention} было вычтено {abs(points)} очков!'))


@client.event
async def on_ready():
    await tree.sync()
    print('Ready!')


client.run(cfg.TOKEN)