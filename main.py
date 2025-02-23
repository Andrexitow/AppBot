import os
import discord
from discord.ext import commands

# Obtener el token desde las variables de entorno
my_secret = os.environ['TOKEN']

# Habilitar intents avanzados
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="#", intents=intents)

# Configuración de yt-dlp para descargar audio
YDL_OPTIONS = {
    'format': 'bestaudio/best',  # Fuerza la mejor calidad de audio disponible
    'noplaylist': 'True',
    'quiet': True,  # Oculta logs innecesarios
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': 'downloads/%(title)s.%(ext)s',  # Guarda el archivo en la carpeta "downloads"
    'postprocessors': [{  # Añade un postprocesador para asegurar que el audio sea compatible
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

FFMPEG_OPTIONS = {
    'before_options': '-nostdin',
    'options': '-vn'
}


@bot.event
async def on_ready():
    print(f'✅ Bot iniciado como {bot.user}')
    print(f'Comandos registrados: {[command.name for command in bot.commands]}')


@bot.command()
async def join(ctx):
    """El bot se une al canal de voz"""
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send(f"🔊 Conectado a **{ctx.author.voice.channel}**")
    else:
        await ctx.send("❌ Debes estar en un canal de voz.")


@bot.command()
async def leave(ctx):
    """El bot sale del canal de voz"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("🔇 Desconectado.")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """Elimina mensajes anteriores"""
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'🗑️ Se eliminaron {amount} mensajes.', delete_after=3)


@bot.command()
async def info(ctx, member: discord.Member):
    """Muestra información sobre un usuario"""
    embed = discord.Embed(title=f'Información de {member.name}', color=discord.Color.blue())
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name='🔹 ID', value=member.id, inline=False)
    embed.add_field(name='🔹 Nombre', value=member.name, inline=False)
    embed.add_field(name='🔹 Apodo', value=member.nick if member.nick else 'Ninguno', inline=False)
    embed.add_field(name='🔹 Cuenta creada', value=member.created_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name='🔹 Se unió el', value=member.joined_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name='🔹 Roles', value=', '.join([role.name for role in member.roles if role.name != "@everyone"]) or 'Sin roles', inline=False)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None, *, reason="No especificada"):
    if member is None:
        await ctx.send("❌ Debes mencionar a un usuario para banear.")
        return

    try:
        await member.ban(reason=reason)
        await ctx.send(f"✅ {member.mention} ha sido baneado. Razón: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ No tengo permisos para banear a este usuario.")
    except Exception as e:
        await ctx.send(f"❌ Error al banear: {e}")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def announce(ctx, channel: discord.TextChannel = None, *, message=None):
    if channel is None or message is None:
        await ctx.send("❌ Uso correcto: `#announce #canal Mensaje del anuncio`")
        return

    embed = discord.Embed(title="📢 Anuncio Importante", description=message, color=discord.Color.blue())
    embed.set_footer(text=f"Anuncio realizado por {ctx.author.name}", icon_url=ctx.author.avatar.url)

    await channel.send(embed=embed)
    await ctx.send(f"✅ Anuncio enviado en {channel.mention}")


# Crear la carpeta "downloads" si no existe
if not os.path.exists("downloads"):
    os.makedirs("downloads")

bot.run(my_secret)
