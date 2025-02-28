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
        banner_url = "https://media.discordapp.net/attachments/1344857912752865370/1344859094716256276/Gif-Animated-Wallpaper-Background-Full-HD-Free-Download-for-PC-Macbook-261121-Wallpaperxyz.com-13.gif?ex=67c27122&is=67c11fa2&hm=5d35eb31f9c5a540a5cd688707bb0f2c25d3b2d1ac20394367744fcb89cf4759&=&width=1423&height=800"

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
