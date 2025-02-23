import os
import discord
from welcome import send_welcome_message
from webserver import keep_alive  # Importa el servidor Flask

# Obtener el token desde las variables de entorno
my_secret = os.environ['TOKEN']

# Habilitar intents avanzados para manejar miembros y roles
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Necesario para detectar cambios en los roles

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Bot iniciado como {client.user}')
    for guild in client.guilds:
        bot_member = guild.me
        if bot_member.guild_permissions.manage_nicknames:
            print(f'✅ Puedo cambiar apodos en {guild.name}')
        else:
            print(f'❌ No tengo permisos para cambiar apodos en {guild.name}')

@client.event
async def on_member_join(member):
    await send_welcome_message(member)  # ✅ Llama a la función de bienvenida desde welcome.py

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        await message.channel.send('👋 ¡Hola!')

    if message.content.startswith('!testwelcome'):
        """Comando para probar el mensaje de bienvenida manualmente"""
        fake_member = message.author  # Usa al que ejecuta el comando como miembro ficticio
        await send_welcome_message(fake_member)
        await message.channel.send(f"✅ Se ha enviado un mensaje de bienvenida para {fake_member.mention}.")

# Nombre del rol que activará el prefijo
ROL_OBJETIVO = "𝒁┊Member"
PREFIJO = "𝒁┊ "

@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
    """Se ejecuta cuando un usuario gana o pierde un rol."""
    guild = after.guild
    role = discord.utils.get(guild.roles, name=ROL_OBJETIVO)  # Busca el rol por nombre

    if not role:
        print(f'⚠️ El rol "{ROL_OBJETIVO}" no existe en el servidor {guild.name}')
        return

    # ✅ Si el usuario GANA el rol, añade el prefijo
    if role not in before.roles and role in after.roles:
        try:
            if not after.nick or not after.nick.startswith(PREFIJO):  # Evita duplicar el prefijo
                nuevo_nombre = f"{PREFIJO}{after.nick or after.name}"
                await after.edit(nick=nuevo_nombre[:32])  # Límite de Discord: 32 caracteres
                print(f'✅ Prefijo añadido a {after.name}')
        except discord.Forbidden:
            print(f'❌ No tengo permisos para cambiar el apodo de {after.name}')
        except discord.HTTPException as e:
            print(f'⚠️ Error al cambiar el apodo: {e}')

    # ✅ Si el usuario PIERDE el rol, elimina el prefijo
    if role in before.roles and role not in after.roles:
        try:
            if after.nick and after.nick.startswith(PREFIJO):  # Evita errores
                nuevo_nombre = after.nick.replace(PREFIJO, "").strip() or None
                await after.edit(nick=nuevo_nombre)
                print(f'🔄 Se quitó el prefijo de {after.name}')
        except discord.Forbidden:
            print(f'❌ No tengo permisos para cambiar el apodo de {after.name}')
        except discord.HTTPException as e:
            print(f'⚠️ Error al cambiar el apodo: {e}')

# Mantener activo el bot
keep_alive()
client.run(my_secret)
