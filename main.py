import os
import discord
import asyncio
from discord.ext import commands
from welcome import send_welcome_message  # Importar la función de welcome.py
from back import send_farewell_message  # Función de despedida
from updaterol import handle_member_update, handle_member_join  # Importar funcioness
from aiohttp import web  # Importar AIOHTTP

# Obtener el token desde las variables de entorno
TOKEN = os.environ['TOKEN']

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True  # Agregamos este intent para las reacciones

# Inicializar el bot
bot = commands.Bot(command_prefix="..", intents=intents)

# Servidor web mínimo para Railway
async def handle(request):
    return web.Response(text="Bot activo.")

@bot.event
async def on_ready():
    print(f'✅ Bot iniciado como {bot.user}')
    print(f'Comandos registrados: {[command.name for command in bot.commands]}')

    @bot.event
    async def on_message(message):
        # Evitar que el bot responda a sus propios mensajes o mensajes de webhooks
        if message.author == bot.user or message.webhook_id:
            return

        # Si el mensaje es "hola", el bot saluda al usuario
        if message.content.lower().strip() == "hola":
            await message.channel.send(f"¡Hola, {message.author.mention}! ¿Cómo estás?")
            await bot.process_commands(message)
            return

        # Verificar si el usuario tiene Nitro; si lo tiene, no se realiza el reemplazo
        if message.author.premium_since is not None:
            await bot.process_commands(message)
            return

        # Construir un diccionario solo con emojis animados del servidor
        animated_emojis = {
            emoji.name: f"<a:{emoji.name}:{emoji.id}>"
            for emoji in message.guild.emojis if emoji.animated
        }

        new_message = message.content
        # Reemplazar solo los emojis animados encontrados en el mensaje
        for emoji_name, emoji_str in animated_emojis.items():
            new_message = new_message.replace(f":{emoji_name}:", emoji_str)

        # Si no se realizó ningún cambio, continuar normalmente
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
                avatar_url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url
            )
        except discord.HTTPException as e:
            print(f"Error al enviar el mensaje: {e}")

        await bot.process_commands(message)

@bot.event
async def on_member_join(member: discord.Member):
    await send_welcome_message(member)
    await handle_member_join(member)

@bot.event
async def on_member_remove(member: discord.Member):
    await send_farewell_message(member)

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    await handle_member_update(before, after)

# Comandos de administración
@bot.command()
@commands.has_permissions(administrator=True)
async def admin_only(ctx):
    await ctx.send("✅ Este comando solo puede ser usado por administradores.")

@bot.command()
async def admin_check(ctx):
    if ctx.author.guild_permissions.administrator:
        await ctx.send("✅ Eres administrador y puedes usar este comando.")
    else:
        await ctx.send("❌ No tienes permisos para usar este comando.")

# Manejo global de errores
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ No tienes permiso para usar este comando.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Ese comando no existe.")
    else:
        print(f"Error no manejado: {error}")

# Cargar extensiones (comandos y autoroles)
async def load_extensions():
    await bot.load_extension("commands")  # Tus otros comandos
    await bot.load_extension("autorol")  # Auto-roles con reacciones

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

# Ejecutar el bot
asyncio.run(main())
