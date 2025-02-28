import discord

# ID del canal donde se enviará el mensaje de despedida
CANAL_DESPEDIDA_ID = 1343965698300317716  # Reemplaza con el ID de tu canal de despedida

async def send_farewell_message(member):
    """Envía un mensaje de despedida con un banner gif y la foto de perfil del usuario."""
    guild = member.guild
    canal_despedida = guild.get_channel(CANAL_DESPEDIDA_ID)  # Obtener el canal de despedida

    if canal_despedida:
        # Obtener la URL del avatar del usuario
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url

        # URL del banner gif de despedida (reemplaza esta URL con la de tu gif/banner)
        banner_url = "https://media.discordapp.net/attachments/1344857912752865370/1344859095076700160/tumblr_static_tumblr_static_eudryx3tcu0w88cwcw4cowcgc_640.gif?ex=67c27122&is=67c11fa2&hm=67639df88492f4ddd3c3e3cd00202688ce20c001793b69ab15282dda6c4e0cab&=&width=621&height=350"

        # Crear el embed con un diseño similar al de bienvenida
        embed = discord.Embed(
            title=f"👋 ¡Adiós, {member.name}!",
            description=(
                "Lamentamos verte partir de **Privilegiados**.\n\n"
                "Gracias por haber formado parte de nuestra comunidad. "
                "Recuerda que siempre serás bienvenido si decides volver."
            ),
            color=discord.Color.dark_gray()  # Puedes cambiar el color si lo deseas
        )
        # Establecer el banner gif en la parte superior del embed
        embed.set_image(url=banner_url)
        # Establecer el avatar del usuario como miniatura
        embed.set_thumbnail(url=avatar_url)
        # Agregar un campo extra opcional
        embed.add_field(
            name="¡Hasta pronto!",
            value="Esperamos verte de nuevo en futuras ocasiones.",
            inline=False
        )
        # Pie de página con el nombre del servidor e icono
        embed.set_footer(text=f"Despedida de {guild.name}", icon_url=guild.icon.url if guild.icon else None)

        # Enviar el mensaje con el embed
        await canal_despedida.send(embed=embed)
        print(f'✅ Mensaje de despedida enviado a {member.name}')
    else:
        print(f'⚠️ No encontré el canal de despedida en {guild.name}')
