import os
import discord
from discord.ext import commands
from updaterol import handle_member_update, handle_member_join  # Importar funciones actualizadas

# Obtener el token desde las variables de entorno
my_secret = os.environ['TOKEN']

# Habilitar intents avanzados
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Necesario para detectar cambios en los miembros

bot = commands.Bot(command_prefix="z.", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot iniciado como {bot.user}')
    print(f'Comandos registrados: {[command.name for command in bot.commands]}')

@bot.event
async def on_member_join(member: discord.Member):
    """Evento que se ejecuta cuando un nuevo miembro se une al servidor."""
    await handle_member_join(member)  # Llamar a la función de asignación de rol

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    """Evento que se ejecuta cuando un miembro actualiza su información."""
    await handle_member_update(before, after)  # Llamar a la función de actualización de apodo

@bot.event
async def on_message(message):
    """Responde a los usuarios cuando dicen 'hola'."""
    if message.author == bot.user:
        return

    if message.content.lower() == "hola":
        await message.channel.send(f"¡Hola, {message.author.mention}! 😊")

    await bot.process_commands(message)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """Elimina una cantidad específica de mensajes en el canal."""
    if amount <= 0:
        await ctx.send("❌ La cantidad debe ser mayor que 0.", delete_after=5)
        return

    try:
        # Eliminar los mensajes (incluyendo el comando)
        deleted = await ctx.channel.purge(limit=amount + 1)
        # Enviar un mensaje de confirmación que se autodestruirá después de 3 segundos
        await ctx.send(f'🗑️ Se eliminaron {len(deleted) - 1} mensajes.', delete_after=3)
    except Exception as e:
        await ctx.send(f"❌ Ocurrió un error al intentar eliminar los mensajes: {e}", delete_after=5)

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
    embed.add_field(
        name='🔹 Roles',
        value=', '.join([role.name for role in member.roles if role.name != "@everyone"]) or 'Sin roles',
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None, *, reason="No especificada"):
    """Banea a un usuario del servidor."""
    if member is None:
        embed = discord.Embed(
            title="❌ Error",
            description="Debes mencionar a un usuario para banear.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=10)
        return

    # Verificar si el bot tiene permisos para banear
    if not ctx.guild.me.guild_permissions.ban_members:
        embed = discord.Embed(
            title="❌ Error",
            description="No tengo permisos para banear usuarios.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=10)
        return

    # Verificar si el usuario a banear tiene un rol más alto que el bot
    if ctx.guild.me.top_role <= member.top_role:
        embed = discord.Embed(
            title="❌ Error",
            description="No puedo banear a este usuario porque tiene un rol igual o superior al mío.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=10)
        return

    try:
        # Banear al usuario
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="✅ Usuario baneado",
            description=f"{member.mention} ha sido baneado.",
            color=discord.Color.green()
        )
        embed.add_field(name="Razón", value=reason, inline=False)
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ Error",
            description="No tengo permisos para banear a este usuario.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=10)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Ocurrió un error al banear: {e}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=10)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def anuncio(ctx, channel: discord.TextChannel = None, *, message=None):
    """Envía un anuncio importante a un canal específico y menciona a todos los miembros."""
    if channel is None or message is None:
        embed = discord.Embed(
            title="❌ Error",
            description="Uso correcto: `z.anuncio #canal Mensaje del anuncio`",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=10)
        return

    try:
        embed = discord.Embed(
            title="📢 Anuncio Importante",
            description=message,
            color=discord.Color.blue()
        )
        embed.set_footer(
            text=f"Anuncio realizado por {ctx.author.name}",
            icon_url=ctx.author.avatar.url
        )
        await channel.send("@here", embed=embed)
        confirm_embed = discord.Embed(
            title="✅ Anuncio enviado",
            description=f"El anuncio se ha enviado correctamente a {channel.mention}.",
            color=discord.Color.green()
        )
        await ctx.send(embed=confirm_embed, delete_after=10)
    except discord.Forbidden:
        await ctx.send(embed=discord.Embed(title="❌ Error", description="No tengo permisos para enviar mensajes en ese canal.", color=discord.Color.red()), delete_after=10)
    except Exception as e:
        await ctx.send(embed=discord.Embed(title="❌ Error", description=f"Ocurrió un error al enviar el anuncio: {e}", color=discord.Color.red()), delete_after=10)

bot.run(my_secret)
