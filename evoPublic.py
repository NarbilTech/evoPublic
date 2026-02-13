import discord
from discord.ext import commands
import os
import difflib

# ====================
# AYARLAR (HAFIZADAN ALINDI)
# ====================
TOKEN = os.getenv("TOKEN")
BOT_SAHIP_ID = 1103809448016879776 

UYE_ROL_ID = 1469284940863504457       
KAYITSIZ_ROL_ID = 1469385270703947986  

# ====================
# BOT AYARLARI
# ====================
intents = discord.Intents.default()
intents.members = True  # Yeni gelenleri görmek için şart
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

def yetkili_mi(ctx):
    return (ctx.author.id == BOT_SAHIP_ID or 
            ctx.author.id == ctx.guild.owner_id or 
            ctx.author.guild_permissions.administrator)

# ====================
# OTOMATİK ROL (YENİ EKLEDİĞİN ÖZELLİK)
# ====================
@bot.event
async def on_member_join(member):
    """Sunucuya katılanlara otomatik kayıtsız rolü verir."""
    try:
        rol = member.guild.get_role(KAYITSIZ_ROL_ID)
        if rol:
            await member.add_roles(rol)
            print(f"✅ {member.display_name} sunucuya katıldı, kayıtsız rolü verildi.")
    except Exception as e:
        print(f"❌ Otomatik rol verme hatası: {e}")

@bot.event
async def on_ready():
    print(f"🚀 {bot.user} Aktif! Otomatik Rol Sistemi Devrede.")

# ====================
# HATA YÖNETİMİ
# ====================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        komutlar = [cmd.name for cmd in bot.commands]
        yazilan = ctx.message.content.replace("!", "").split()[0]
        olasi = difflib.get_close_matches(yazilan, komutlar, n=1)
        if olasi:
            await ctx.send(f"❓ `{yazilan}` bulunamadı. **!{olasi[0]}** mı demek istedin?", delete_after=5)
    return

# ====================
# MODERN KIRMIZI YÖNETİCİ PANELİ
# ====================
@bot.command()
async def admin(ctx):
    if not yetkili_mi(ctx): return
    
    embed = discord.Embed(
        title="🛑 ÇAKIRBEYLİ YÖNETİM",
        description="Sunucu güvenliği için yetkili araçları aşağıdadır.",
        color=0xFF0000 
    )
    
    embed.add_field(name="👥 KAYIT YÖNETİMİ", value="> `!kayit @üye` / `!unkayit @üye`", inline=True)
    embed.add_field(name="🎭 ROL SİSTEMİ", value="> `!rolver @üye @rol` / `!rolal @üye @rol`", inline=True)
    embed.add_field(name="🛡️ MODERASYON", value="```!ban @üye\n!kick @üye\n!unban [ID]```", inline=False)
    embed.add_field(name="🧹 TEMİZLİK", value="`!sil [miktar]`", inline=True)
    
    embed.set_footer(text=f"{ctx.author.name} | 2026 Evo System", icon_url=ctx.author.display_avatar.url)
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    
    await ctx.send(embed=embed)

# ====================
# KOMUTLAR
# ====================

@bot.command()
async def sil(ctx, miktar: int):
    if not yetkili_mi(ctx): return
    try:
        await ctx.channel.purge(limit=miktar + 1)
        msg = await ctx.send(f"🧹 **{miktar}** mesaj imha edildi.")
        await msg.delete(delay=3)
    except: pass

@bot.command()
async def kayit(ctx, member: discord.Member):
    if not yetkili_mi(ctx): return
    try:
        u, k = ctx.guild.get_role(UYE_ROL_ID), ctx.guild.get_role(KAYITSIZ_ROL_ID)
        if k: await member.remove_roles(k)
        if u: await member.add_roles(u)
        await ctx.send(f"✅ {member.mention} kaydedildi.", delete_after=5)
    except: pass

@bot.command()
async def unkayit(ctx, member: discord.Member):
    if not yetkili_mi(ctx): return
    try:
        u, k = ctx.guild.get_role(UYE_ROL_ID), ctx.guild.get_role(KAYITSIZ_ROL_ID)
        if u: await member.remove_roles(u)
        if k: await member.add_roles(k)
        await ctx.send(f"🔄 {member.mention} kayıtsıza çekildi.", delete_after=5)
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
        await ctx.send(f"✅ {user.name} yasağı kaldırıldı.")
    except: pass

bot.run(TOKEN)
