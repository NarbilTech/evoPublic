import discord
from discord.ext import commands
import os
import difflib

# ====================
# AYARLAR (BURALARI DOLDUR)
# ====================
TOKEN = os.getenv("TOKEN")
BOT_SAHIP_ID = 1103809448016879776  # Senin ID'n

# KAYIT SİSTEMİ İÇİN SABİT ROL ID'LERİ
UYE_ROL_ID = 123456789012345678       # Üye rolü ID'sini buraya yapıştır
KAYITSIZ_ROL_ID = 123456789012345678  # Kayıtsız rolü ID'sini buraya yapıştır

# ====================
# BOT AYARLARI
# ====================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ====================
# YETKİ KONTROLÜ
# ====================
def yetkili_mi(ctx):
    # Bot sahibi, Sunucu sahibi veya Yönetici yetkisi olanlar kullanabilir
    return (ctx.author.id == BOT_SAHIP_ID or 
            ctx.author.id == ctx.guild.owner_id or 
            ctx.author.guild_permissions.administrator)

# ====================
# EVENTS
# ====================
@bot.event
async def on_ready():
    print(f"{bot.user} aktif ve görev başında!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        komutlar = [cmd.name for cmd in bot.commands]
        yazilan = ctx.message.content.replace("!", "").split()[0]
        olasi = difflib.get_close_matches(yazilan, komutlar, n=1)
        if olasi:
            await ctx.send(f"❌ `{yazilan}` diye bir komut yok. `{olasi[0]}` mı demek istedin?")

# ====================
# KAYIT SİSTEMİ (OTOMATİK ID)
# ====================

@bot.command()
async def kayit(ctx, member: discord.Member):
    if not yetkili_mi(ctx): return
    uye_rol = ctx.guild.get_role(UYE_ROL_ID)
    kayitsiz_rol = ctx.guild.get_role(KAYITSIZ_ROL_ID)
    try:
        if kayitsiz_rol: await member.remove_roles(kayitsiz_rol)
        if uye_rol: await member.add_roles(uye_rol)
        await ctx.send(f"✅ {member.mention} başarıyla kayıt edildi.")
    except:
        await ctx.send("❌ Yetki hatası! Botun rolü en üstte olmalı.")

@bot.command()
async def unkayit(ctx, member: discord.Member):
    if not yetkili_mi(ctx): return
    uye_rol = ctx.guild.get_role(UYE_ROL_ID)
    kayitsiz_rol = ctx.guild.get_role(KAYITSIZ_ROL_ID)
    try:
        if uye_rol: await member.remove_roles(uye_rol)
        if kayitsiz_rol: await member.add_roles(kayitsiz_rol)
        await ctx.send(f"🔄 {member.mention} kayıtsıza atıldı.")
    except:
        await ctx.send("❌ Yetki hatası!")

# ====================
# ROL YÖNETİMİ (ETİKETLEME)
# ====================

@bot.command()
async def rolver(ctx, member: discord.Member, rol: discord.Role):
    if not yetkili_mi(ctx): return
    try:
        await member.add_roles(rol)
        await ctx.send(f"✅ {member.mention} kullanıcısına **{rol.name}** rolü verildi.")
    except:
        await ctx.send("❌ Bu rolü vermeye yetkim yetmiyor.")

@bot.command()
async def rolal(ctx, member: discord.Member, rol: discord.Role):
    if not yetkili_mi(ctx): return
    try:
        await member.remove_roles(rol)
        await ctx.send(f"✅ {member.mention} üzerinden **{rol.name}** rolü alındı.")
    except:
        await ctx.send("❌ Bu rolü almaya yetkim yetmiyor.")

# ====================
# MODERASYON (BAN, KICK, UNBAN, SIL)
# ====================

@bot.command()
async def ban(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    if not yetkili_mi(ctx): return
    await member.ban(reason=sebep)
    await ctx.send(f"🔨 **{member.name}** banlandı. Sebep: {sebep}")

@bot.command()
async def unban(ctx, user_id: int):
    if not yetkili_mi(ctx): return
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ **{user.name}** yasağı kaldırıldı.")

@bot.command()
async def kick(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    if not yetkili_mi(ctx): return
    await member.kick(reason=sebep)
    await ctx.send(f"👢 **{member.name}** atıldı. Sebep: {sebep}")

@bot.command()
async def sil(ctx, miktar: int):
    if not yetkili_mi(ctx): return
    await ctx.channel.purge(limit=miktar + 1)
    msg = await ctx.send(f"🧹 {miktar} mesaj temizlendi.")
    await msg.delete(delay=3)

bot.run(TOKEN)
