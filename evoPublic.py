import discord
from discord.ext import commands
import os
import difflib

# ====================
# AYARLAR (ID'LERİ GİR)
# ====================
TOKEN = os.getenv("TOKEN")
BOT_SAHIP_ID = 1103809448016879776 

UYE_ROL_ID = 123456789012345678       # Buraya Üye rol ID'sini gir
KAYITSIZ_ROL_ID = 123456789012345678  # Buraya Kayıtsız rol ID'sini gir

# ====================
# BOT AYARLARI
# ====================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ====================
# YETKİ KONTROLÜ
# ====================
def yetkili_mi(ctx):
    return (ctx.author.id == BOT_SAHIP_ID or 
            ctx.author.id == ctx.guild.owner_id or 
            ctx.author.guild_permissions.administrator)

# ====================
# ÖZEL HATA YAKALAYICI (Bunu mu demek istedin?)
# ====================
@bot.event
async def on_command_error(ctx, error):
    # Sadece komut yanlış yazıldığında öneri yapar
    if isinstance(error, commands.CommandNotFound):
        komutlar = [cmd.name for cmd in bot.commands]
        yazilan = ctx.message.content.replace("!", "").split()[0]
        olasi = difflib.get_close_matches(yazilan, komutlar, n=1)
        if olasi:
            await ctx.send(f"❓ `{yazilan}` diye bir komut bulamadım. **!{olasi[0]}** mı demek istedin?", delete_after=5)
    # Yetki hataları veya diğer hatalar gelirse bot tamamen sessiz kalır
    pass

# ====================
# ADMIN YARDIM PANELİ
# ====================
@bot.command()
async def admin(ctx):
    if not yetkili_mi(ctx): return
    
    embed = discord.Embed(
        title="🛠️ Yönetici Paneli",
        description="Aşağıdaki komutlar sadece yetkililer içindir:",
        color=discord.Color.blue()
    )
    embed.add_field(name="Kayıt İşlemleri", value="`!kayit @üye` / `!unkayit @üye`", inline=False)
    embed.add_field(name="Rol İşlemleri", value="`!rolver @üye @rol` / `!rolal @üye @rol`", inline=False)
    embed.add_field(name="Moderasyon", value="`!ban` / `!kick` / `!unban ID` / `!sil [sayı]`", inline=False)
    
    await ctx.send(embed=embed)

# ====================
# KOMUTLAR
# ====================

@bot.command()
async def kayit(ctx, member: discord.Member):
    if not yetkili_mi(ctx): return
    try:
        u, k = ctx.guild.get_role(UYE_ROL_ID), ctx.guild.get_role(KAYITSIZ_ROL_ID)
        if k: await member.remove_roles(k)
        if u: await member.add_roles(u)
        await ctx.send(f"✅ {member.display_name} başarıyla kaydedildi.", delete_after=5)
    except: pass

@bot.command()
async def unkayit(ctx, member: discord.Member):
    if not yetkili_mi(ctx): return
    try:
        u, k = ctx.guild.get_role(UYE_ROL_ID), ctx.guild.get_role(KAYITSIZ_ROL_ID)
        if u: await member.remove_roles(u)
        if k: await member.add_roles(k)
        await ctx.send(f"🔄 {member.display_name} kayıtsıza çekildi.", delete_after=5)
    except: pass

@bot.command()
async def rolver(ctx, member: discord.Member, rol: discord.Role):
    if not yetkili_mi(ctx): return
    try:
        await member.add_roles(rol)
        await ctx.send(f"✅ **{rol.name}** rolü verildi.", delete_after=5)
    except: pass

@bot.command()
async def rolal(ctx, member: discord.Member, rol: discord.Role):
    if not yetkili_mi(ctx): return
    try:
        await member.remove_roles(rol)
        await ctx.send(f"✅ **{rol.name}** rolü geri alındı.", delete_after=5)
    except: pass

@bot.command()
async def sil(ctx, miktar: int):
    if not yetkili_mi(ctx): return
    try:
        await ctx.channel.purge(limit=miktar + 1)
        m = await ctx.send(f"🧹 {miktar} adet mesaj temizlendi.")
        await m.delete(delay=3)
    except: pass

@bot.command()
async def ban(ctx, member: discord.Member):
    if not yetkili_mi(ctx): return
    try: await member.ban(); await ctx.send(f"🔨 {member.name} banlandı.")
    except: pass

@bot.command()
async def kick(ctx, member: discord.Member):
    if not yetkili_mi(ctx): return
    try: await member.kick(); await ctx.send(f"👢 {member.name} atıldı.")
    except: pass

@bot.command()
async def unban(ctx, user_id: int):
    if not yetkili_mi(ctx): return
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ Yasak kaldırıldı: {user.name}")
    except: pass

bot.run(TOKEN)
