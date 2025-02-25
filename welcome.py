import discord

# ID del canal donde se enviará el mensaje de bienvenida
CANAL_BIENVENIDA_ID = 1343776731160641657  # Reemplaza con el ID de tu canal de bienvenida

async def send_welcome_message(member):
    """Envía un mensaje de bienvenida con un banner gif y la foto de perfil del usuario."""
    guild = member.guild
    canal_bienvenida = guild.get_channel(CANAL_BIENVENIDA_ID)  # Obtener el canal de bienvenida

    if canal_bienvenida:
        # Obtener la URL del avatar del usuario
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url

        # URL del banner gif (reemplaza esta URL con la de tu gif/banner)
        banner_url = "https://media.discordapp.net/attachments/1343622087448723556/1343809701996920852/uhMkNyZ.gif?ex=67be9fcf&is=67bd4e4f&hm=88f56addfb39afd81a265f5f48f4a6a30ac3200890e4ece124e357b1d5a81ca5&=&width=625&height=353"

        # Crear el embed con un diseño mejorado
        embed = discord.Embed(
            title=f"🕵️ ¡Bienvenido {member.name}!",
            description=(
                "🎉 ¡Nos alegra tenerte en **Privilegiados**!\n\n"
                "Te invitamos a leer las reglas y explorar todos los canales para que disfrutes al máximo la experiencia."
            ),
            color=discord.Color.blurple()  # Usando el color blurple, propio de Discord
        )
        # Establecer el banner gif en la parte superior del embed
        embed.set_image(url=banner_url)
        # Establecer el avatar del usuario como miniatura
        embed.set_thumbnail(url=avatar_url)
        # Agregar un campo extra con información relevante, haciendo clickeable el canal
        embed.add_field(
            name="¿Por dónde empezar?",
            value=f"Dirígete a <#{1343621926521933998}> para chatear.",
            inline=False
        )
        # Pie de página con el nombre del servidor e icono
        embed.set_footer(text=f"Bienvenido a {guild.name}", icon_url=guild.icon.url if guild.icon else None)

        # Enviar el mensaje con el embed
        await canal_bienvenida.send(embed=embed)
        print(f'✅ Mensaje de bienvenida enviado a {member.name}')
    else:
        print(f'⚠️ No encontré el canal de bienvenida en {guild.name}')
