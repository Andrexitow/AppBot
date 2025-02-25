import discord
import asyncio
from discord.ext import commands

class BotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        """Elimina una cantidad específica de mensajes en el canal."""
        if amount <= 0:
            await ctx.send("❌ La cantidad debe ser mayor que 0.", delete_after=5)
            return

        try:
            deleted = await ctx.channel.purge(limit=amount + 1)
            await ctx.send(f'🗑️ Se eliminaron {len(deleted) - 1} mensajes.', delete_after=3)
        except Exception as e:
            await ctx.send(f"❌ Error al eliminar mensajes: {e}", delete_after=5)

    @commands.command()
    async def info(self, ctx, member: discord.Member):
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

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, *, reason="No especificada"):
        """Banea a un usuario del servidor."""
        if not member:
            await ctx.send("❌ Debes mencionar a un usuario para banear.", delete_after=10)
            return

        try:
            await member.ban(reason=reason)
            embed = discord.Embed(title="✅ Usuario baneado", description=f"{member.mention} ha sido baneado.", color=discord.Color.green())
            embed.add_field(name="Razón", value=reason, inline=False)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos para banear a este usuario.", delete_after=10)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member = None, tiempo: str = None, *, reason="No especificada"):
        """Mutea a un usuario en el servidor por un tiempo específico."""
        if not member:
            await ctx.send("❌ Debes mencionar a un usuario para mutear.", delete_after=10)
            return

        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted", reason="Rol de mute creado automáticamente.")
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, speak=False)

        await member.add_roles(mute_role, reason=reason)
        embed = discord.Embed(title="✅ Usuario muteado", description=f"{member.mention} ha sido muteado.", color=discord.Color.green())
        embed.add_field(name="Razón", value=reason, inline=False)
        await ctx.send(embed=embed)

        if tiempo:
            try:
                tiempo_segundos = sum(int(t[:-1]) * {'d': 86400, 'h': 3600, 'm': 60, 's': 1}[t[-1]] for t in tiempo.split() if t[-1] in "dhms")
                embed.add_field(name="Duración", value=tiempo, inline=False)
                await asyncio.sleep(tiempo_segundos)
                await member.remove_roles(mute_role, reason="Tiempo de muteo terminado.")
                await ctx.send(f"✅ {member.mention} ha sido desmuteado automáticamente.")
            except ValueError:
                await ctx.send("❌ Formato de tiempo inválido. Usa `1d2h3m4s`.", delete_after=10)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member = None):
        """Desmutea a un usuario en el servidor."""
        if not member:
            await ctx.send("❌ Debes mencionar a un usuario para desmutear.", delete_after=10)
            return

        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role in member.roles:
            await member.remove_roles(mute_role, reason="Desmuteo manual")
            await ctx.send(f"✅ {member.mention} ha sido desmuteado.")
        else:
            await ctx.send("❌ Este usuario no está muteado.", delete_after=10)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def anuncio(self, ctx, channel: discord.TextChannel = None, *, message=None):
        """Envía un anuncio a un canal específico con soporte para emojis personalizados."""
        if not channel or not message:
            embed = discord.Embed(
                title="❌ Error",
                description="Uso correcto: `..anuncio #canal Mensaje del anuncio`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=10)
            return

        # Obtener todos los emojis del servidor y reemplazar en el mensaje
        emojis = {emoji.name: str(emoji) for emoji in ctx.guild.emojis}
        for emoji_name, emoji_str in emojis.items():
            message = message.replace(f":{emoji_name}:", emoji_str)

        try:
            embed = discord.Embed(
                title="📢 Anuncio Importante",
                description=message,  # Mensaje con emojis bien formateados
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Anuncio realizado por {ctx.author.name}", icon_url=ctx.author.avatar.url)

            await channel.send("@here", embed=embed)

            confirm_embed = discord.Embed(
                title="✅ Anuncio enviado",
                description=f"El anuncio se ha enviado correctamente a {channel.mention}.",
                color=discord.Color.green()
            )
            await ctx.send(embed=confirm_embed, delete_after=10)

        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(
                title="❌ Error",
                description="No tengo permisos para enviar mensajes en ese canal.",
                color=discord.Color.red()
            ), delete_after=10)

        except Exception as e:
            await ctx.send(embed=discord.Embed(
                title="❌ Error",
                description=f"Ocurrió un error al enviar el anuncio: {e}",
                color=discord.Color.red()
            ), delete_after=10)

# Agregar la clase como un `Cog` al bot
async def setup(bot):
    await bot.add_cog(BotCommands(bot))
