import os
import discord
import asyncio
from discord.ext import commands
from updaterol import handle_member_update, handle_member_join  # Importar funciones

# Obtener el token desde las variables de entorno
TOKEN = os.environ['TOKEN']

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True  # Agregamos este intent para las reacciones

# Inicializar el bot
bot = commands.Bot(command_prefix="..", intents=intents)


@bot.event
async def on_ready():
    print(f'✅ Bot iniciado como {bot.user}')
    print(
        f'Comandos registrados: {[command.name for command in bot.commands]}')


@bot.event
async def on_message(message):
    """Reenvía el mensaje con emojis y el nombre del usuario sin errores."""
    if message.author == bot.user or message.webhook_id:
        return

    emojis = {
        emoji.name:
        f"<{'a' if emoji.animated else ''}:{emoji.name}:{emoji.id}>"
        for emoji in message.guild.emojis
    }

    new_message = message.content
    for emoji_name, emoji_str in emojis.items():
        new_message = new_message.replace(f":{emoji_name}:", emoji_str)

    if new_message == message.content:
        await bot.process_commands(message)
        return

    channel = message.channel
    await asyncio.sleep(0.3)

    try:
        await message.delete()
    except discord.Forbidden:
        print(f"No tengo permisos para borrar mensajes en {channel.name}")

    webhooks = await channel.webhooks()
    webhook = next((wh for wh in webhooks if wh.user == bot.user), None)

    if webhook is None:
        webhook = await channel.create_webhook(name="EmojiBot")

    try:
        await webhook.send(
            content=new_message,
            username=message.author.display_name,
            avatar_url=message.author.avatar.url
            if message.author.avatar else message.author.default_avatar.url)
    except discord.HTTPException as e:
        print(f"Error al enviar el mensaje: {e}")

    await bot.process_commands(message)


@bot.event
async def on_member_join(member: discord.Member):
    await handle_member_join(member)


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    await handle_member_update(before, after)


# Cargar comandos y el sistema de auto-roles
async def load_extensions():
    await bot.load_extension("commands")  # Tus otros comandos
    await bot.load_extension("autorol")  # Auto-roles con reacciones


async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)


# Ejecutar el bot
asyncio.run(main())
