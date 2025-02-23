import discord

# Configuración del rol y prefijo
ROL_OBJETIVO = "𝒁┊Member"
PREFIJO = "𝒁┊ "

async def update_role_nickname(before: discord.Member, after: discord.Member):
    """Se ejecuta cuando un usuario gana o pierde un rol y actualiza su apodo."""
    guild = after.guild
    role = discord.utils.get(guild.roles, name=ROL_OBJETIVO)

    if not role:
        print(f'⚠️ El rol "{ROL_OBJETIVO}" no existe en el servidor {guild.name}')
        return

    # ✅ Si el usuario GANA el rol, añade el prefijo
    if role not in before.roles and role in after.roles:
        try:
            if not after.nick or not after.nick.startswith(PREFIJO):
                nuevo_nombre = f"{PREFIJO}{after.nick or after.name}"
                await after.edit(nick=nuevo_nombre[:32])
                print(f'✅ Prefijo añadido a {after.name}')
        except discord.Forbidden:
            print(f'❌ No tengo permisos para cambiar el apodo de {after.name}')
        except discord.HTTPException as e:
            print(f'⚠️ Error al cambiar el apodo: {e}')

    # ✅ Si el usuario PIERDE el rol, elimina el prefijo
    if role in before.roles and role not in after.roles:
        try:
            if after.nick and after.nick.startswith(PREFIJO):
                nuevo_nombre = after.nick.replace(PREFIJO, "").strip() or None
                await after.edit(nick=nuevo_nombre)
                print(f'🔄 Se quitó el prefijo de {after.name}')
        except discord.Forbidden:
            print(f'❌ No tengo permisos para cambiar el apodo de {after.name}')
        except discord.HTTPException as e:
            print(f'⚠️ Error al cambiar el apodo: {e}')
