import discord

# Configuración del rol y prefijo
ROL_OBJETIVO = "𝒁┊Member"  # Rol que activa el prefijo en el apodoO
ROL_USUARIO = "User"  # Rol que se asigna automáticamente a los nuevos miembros
PREFIJO = "𝒁┊ "

# Diccionario para almacenar los nombres originales de los usuarios
nombres_originales = {}

async def handle_member_join(member: discord.Member):
    """Asigna el rol 'User' a los nuevos miembros."""
    guild = member.guild
    rol_user = discord.utils.get(guild.roles, name=ROL_USUARIO)

    if not rol_user:
        print(f'⚠️ El rol "{ROL_USUARIO}" no existe en el servidor {guild.name}')
        return

    try:
        await member.add_roles(rol_user)
        print(f'✅ Rol "{ROL_USUARIO}" asignado a {member.name}')
    except discord.Forbidden:
        print(f'❌ No tengo permisos para asignar roles a {member.name}')
    except Exception as e:
        print(f'⚠️ Error al asignar el rol: {e}')

async def handle_member_update(before: discord.Member, after: discord.Member):
    """Añade o quita el prefijo en el apodo de los miembros según el rol."""
    guild = after.guild
    role = discord.utils.get(guild.roles, name=ROL_OBJETIVO)

    if not role:
        print(f'⚠️ El rol "{ROL_OBJETIVO}" no existe en el servidor {guild.name}')
        return

    # ✅ Si el usuario GANA el rol, añade el prefijo
    if role not in before.roles and role in after.roles:
        try:
            if after.id not in nombres_originales:
                nombres_originales[after.id] = after.nick or after.name

            nuevo_nombre = f"{PREFIJO}{nombres_originales[after.id]}"[:32]
            await after.edit(nick=nuevo_nombre)
            print(f'✅ Prefijo añadido a {after.name} (Apodo: {nuevo_nombre})')
        except discord.Forbidden:
            print(f'❌ No tengo permisos para cambiar el apodo de {after.name}')
        except discord.HTTPException as e:
            print(f'⚠️ Error al cambiar el apodo: {e}')

    # ✅ Si el usuario PIERDE el rol, elimina el prefijo
    if role in before.roles and role not in after.roles:
        try:
            if after.id in nombres_originales:
                nuevo_nombre = nombres_originales[after.id]
                await after.edit(nick=nuevo_nombre)
                del nombres_originales[after.id]
                print(f'🔄 Prefijo eliminado de {after.name} (Apodo restaurado: {nuevo_nombre})')
        except discord.Forbidden:
            print(f'❌ No tengo permisos para cambiar el apodo de {after.name}')
        except discord.HTTPException as e:
            print(f'⚠️ Error al cambiar el apodo: {e}')
