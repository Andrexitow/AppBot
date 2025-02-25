import discord
from discord.ext import commands
import re


class AutoRolesURL(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # Guardamos el mensaje de autoroles para gestionar las reacciones
        self.role_messages = {}

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def autorolcreate_url(self, ctx, channel: discord.TextChannel,
                                description: str, thumbnail_url: str, *,
                                roles_text: str):
        """
        Crea un embed de autoroles con un thumbnail opcional que se pasa mediante URL.

        Uso:
          ..autorolcreate_url #canal "Descripción" [thumbnail_url | none] "emoji = @Rol | emoji = @Rol | ..."
        """
        # Validamos el thumbnail
        final_thumbnail_url = None
        if thumbnail_url.lower() not in ("none", "no"):
            final_thumbnail_url = thumbnail_url  # Se asume que es una URL válida

        # Procesamos la lista de pares "emoji = rol"
        roles_dict = {}  # Estructura: {emoji_obj: role}
        # Este patrón detecta IDs de emojis o emojis estándar
        emoji_pattern = re.compile(r"(\d+|[^|= ]+)")
        pairs = roles_text.split("|")
        for pair in pairs:
            try:
                emoji_str, role_mention = map(str.strip, pair.split("="))
                # Extraer el ID del rol usando una expresión regular (más robusto)
                role_id_match = re.search(r"\d+", role_mention)
                if not role_id_match:
                    await ctx.send(
                        f"❌ No se pudo extraer el ID del rol en: `{role_mention}`"
                    )
                    return
                role_id = int(role_id_match.group())
                role = ctx.guild.get_role(role_id)
                if role is None:
                    await ctx.send(f"❌ No encontré el rol {role_mention}.")
                    return

                match = emoji_pattern.match(emoji_str)
                if not match:
                    await ctx.send(
                        "❌ Formato incorrecto en los emojis. Usa: `emoji = @Rol`"
                    )
                    return

                emoji_input = match.group(1)
                # Si es un número, buscamos el emoji personalizado
                if emoji_input.isdigit():
                    emoji_obj = discord.utils.get(ctx.guild.emojis,
                                                  id=int(emoji_input))
                    if emoji_obj is None:
                        await ctx.send(
                            f"❌ No se encontró el emoji con ID {emoji_input} en este servidor."
                        )
                        return
                else:
                    # Se asume que es un emoji estándar
                    emoji_obj = emoji_input

                roles_dict[emoji_obj] = role

            except Exception as e:
                await ctx.send(
                    f"❌ Error en la sintaxis. Usa: `..autorolcreate_url #canal \"Descripción\" [thumbnail_url|none] \"emoji = @Rol\"`. Error: {e}"
                )
                return

        # Crear el embed
        embed = discord.Embed(
            title=
            "<a:aCORONA_:882352292140036097> 𝐀𝐮𝐭𝐨𝐫𝐨𝐥𝐞𝐬 <a:aCORONA_:882352292140036097>",
            description="<a:cruz:882351660339437579> " + description,
            color=discord.Color.blue())

        if final_thumbnail_url:
            embed.set_thumbnail(url=final_thumbnail_url)

        # Agregar la lista de roles a la descripción
        role_lines = []
        for emoji, role in roles_dict.items():
            role_lines.append(f"{emoji} | {role.mention}")
        embed.description += "\n\n" + "\n".join(role_lines)

        # Enviar el mensaje con el embed
        try:
            autorole_message = await channel.send(
                embed=embed,
                allowed_mentions=discord.AllowedMentions(roles=True))
        except Exception as e:
            await ctx.send(f"❌ Error al enviar el mensaje: {e}")
            return

        # Agregar las reacciones a dicho mensaje
        for emoji in roles_dict.keys():
            try:
                await autorole_message.add_reaction(emoji)
            except Exception as e:
                await ctx.send(f"❌ No pude agregar la reacción {emoji}: {e}")

        # Guardamos el mensaje para gestionar las reacciones posteriormente
        self.role_messages[autorole_message.id] = roles_dict

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Asigna el rol correspondiente al reaccionar y remueve otros para que solo tenga uno."""
        if payload.message_id not in self.role_messages:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None or member.bot:
            return

        roles_dict = self.role_messages[payload.message_id]
        channel = guild.get_channel(payload.channel_id)
        if not channel:
            return

        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception as e:
            print(f"Error al obtener el mensaje: {e}")
            return

        new_role = None
        for key, role in roles_dict.items():
            # Compara para emojis personalizados y estándar
            if isinstance(key, discord.Emoji):
                if payload.emoji.id == key.id:
                    new_role = role
                    break
            else:
                if str(payload.emoji) == key:
                    new_role = role
                    break

        if new_role is None:
            return

        # Remover otros roles de la lista para que el usuario solo tenga uno
        for key, role in roles_dict.items():
            if role in member.roles and role != new_role:
                try:
                    await member.remove_roles(role)
                except Exception as e:
                    print(f"Error removiendo rol: {e}")

                # Remover la reacción previa del usuario
                for reaction in message.reactions:
                    if isinstance(key, discord.Emoji):
                        if isinstance(
                                reaction.emoji,
                                discord.Emoji) and reaction.emoji.id == key.id:
                            async for user in reaction.users():
                                if user.id == member.id:
                                    try:
                                        await message.remove_reaction(
                                            reaction.emoji, member)
                                    except Exception as e:
                                        print(
                                            f"Error removiendo reacción: {e}")
                    else:
                        if str(reaction.emoji) == key:
                            async for user in reaction.users():
                                if user.id == member.id:
                                    try:
                                        await message.remove_reaction(
                                            reaction.emoji, member)
                                    except Exception as e:
                                        print(
                                            f"Error removiendo reacción: {e}")

        try:
            await member.add_roles(new_role)
        except Exception as e:
            print(f"Error asignando rol: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Quita el rol si se elimina la reacción."""
        if payload.message_id not in self.role_messages:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None or member.bot:
            return

        roles_dict = self.role_messages[payload.message_id]
        for key, role in roles_dict.items():
            if isinstance(key, discord.Emoji):
                if payload.emoji.id == key.id:
                    try:
                        await member.remove_roles(role)
                    except Exception as e:
                        print(
                            f"Error removiendo rol al quitar la reacción: {e}")
                    break
            else:
                if str(payload.emoji) == key:
                    try:
                        await member.remove_roles(role)
                    except Exception as e:
                        print(
                            f"Error removiendo rol al quitar la reacción: {e}")
                    break


async def setup(bot):
    await bot.add_cog(AutoRolesURL(bot))
