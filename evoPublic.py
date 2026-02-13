import discord
from discord.ext import commands
import os

# ====================
# AYARLAR (ID'LER SABİTLENDİ)
# ====================
TOKEN = os.getenv("TOKEN")
BOT_SAHIP_ID = 1103809448016879776 

# Kaydedilen Rol ID'lerin
UYE_ROL_ID = 1469284940863504457       
KAYITSIZ_ROL_ID = 1469385270703947986  

# ====================
# BOT YAPILANDIRMASI
# ====================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Hataları tamamen susturur (Yetkin yok mesajını engeller)
@bot.event
async def on_command_error(ctx, error):
    return

def yetkili_mi(ctx):
    return (ctx.author.id == BOT_SAHIP_ID or 
            ctx.author.id == ctx.guild.owner_id or 
            ctx.author.guild_permissions.administrator)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} Tüm özelliklerle aktif!")

# ====================
# MAVİ YÖNETİCİ PANELİ
# ====================
@bot.command()
async def admin(ctx):
    if not yetkili_mi(ctx): return
    embed = discord.Embed(
        title="🛠️ Yönetici Paneli",
        description="Aşağıdaki komutlar sadece yetkililer içindir:",
        color=0x3498db # Mavi Panel
    )
    embed.add_field(name="👤 Kayıt", value="`!kayit @üye` / `!unkayit @üye`", inline=False)
    embed.add_field(name="🎭 Roller", value="`!rolver @üye @rol` / `!rolal @üye @rol`", inline=False)
    embed.add_field(name="🛡️ Moderasyon", value="`!ban @üye` / `!kick @üye` / `!unban ID` / `!sil [sayı]`", inline=False)
    await ctx.send(embed=embed)

# ====================
# TÜM KOMUTLAR (EKSİKSİZ)
# ====================

@bot.command()
async def sil(ctx, miktar: int):
    if not yetkili_mi(ctx): return
    try:
        await ctx.channel.purge(limit=miktar + 1)
        msg = await ctx.send(f"🧹 {miktar} mesaj temizlendi.")
        await msg.delete(delay=3)
    except: pass

@bot.command()
async def kayit(ctx, member: discord.Member):
    if not yetkili_mi(ctx): return
    try:
        u, k = ctx.guild.get_role(UYE_ROL_ID), ctx.guild.get_role(KAYITSIZ_ROL_ID)
        if k: await member.remove_roles(k)
        if u: await member.add_roles(u)
        await ctx.send(f"✅ {member.display_name} kaydedildi.", delete_after=5)
    except: pass

@bot.command()
async def unkayit(ctx, member: discord.Member):
    if not yetkili_mi(ctx): return
    try:
        u, k = ctx.guild.get_role(UYE_ROL_ID), ctx.guild.get_role(KAYITSIZ_ROL_ID)
        if u: await member.remove_roles(u)
        if k: await member.add_roles(k)
        await ctx.send(f"🔄 {member.display_name} unkayit edildi.", delete_after=5)
    except: pass

@bot.command()
async def rolver(ctx, member: discord.Member, rol: discord.Role):
    if not yetkili_mi(ctx): return
    try:
        await member.add_roles(rol)
        await ctx.send(f"✅ **{rol.name}** verildi.", delete_after=5)
    except: pass

@bot.command()
async def rolal(ctx, member: discord.Member, rol: discord.Role):
    if not yetkili_mi(ctx): return
    try:
        await member.remove_roles(rol)
        await ctx.send(f"✅ **{rol.name}** alındı.", delete_after=5)
    except: pass

@bot.command()
async def ban(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    if not yetkili_mi(ctx): return
    try:
        await member.ban(reason=sebep)
        await ctx.send(f"🔨 {member.name} banlandı.")
    except: pass

@bot.command()
async def kick(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    if not yetkili_mi(ctx): return
    try:
        await member.kick(reason=sebep)
        await ctx.send(f"👢 {member.name} atıldı.")
    except: pass

@bot.command()
async def unban(ctx, user_id: int):
    if not yetkili_mi(ctx): return
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ {user.name} yasak kaldırıldı.")
    except: pass

bot.run(TOKEN)
