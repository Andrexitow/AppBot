import discord

# ID del canal donde se enviará el mensaje de bienvenida
CANAL_BIENVENIDA_ID = 1342951417928880362  # Reemplaza con el ID de tu canal de bienvenida

async def send_welcome_message(member):
    """Envia un mensaje de bienvenida con la foto de perfil del usuario."""
    guild = member.guild
    canal_bienvenida = guild.get_channel(CANAL_BIENVENIDA_ID)  # Obtener el canal de bienvenida

    if canal_bienvenida:
        # Obtener la URL del avatar del usuario
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url

        # Crear el embed con la imagen del usuario
        embed = discord.Embed(
            title=f"🕵️ ¡Bienvenido {member.name}!",
            description="🎉 Disfruta nuestro clan llamado **LosZetas BloodStrike**.",
            color=discord.Color.blue()  # Color del embed
        )
        embed.set_thumbnail(url=avatar_url)  # Foto de perfil del usuario
        embed.set_footer(text=f"Bienvenido a {guild.name}", icon_url=guild.icon.url if guild.icon else None)

        # Enviar el mensaje con el embed
        await canal_bienvenida.send(embed=embed)
        print(f'✅ Mensaje de bienvenida enviado a {member.name}')
    else:
        print(f'⚠️ No encontré el canal de bienvenida en {guild.name}')
