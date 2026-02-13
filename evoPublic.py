import discord
from discord.ext import commands
import os
import difflib
from typing import Union

# ====================
# AYARLAR (ID'LER SABİTLENDİ)
# ====================
TOKEN = os.getenv("TOKEN")
BOT_SAHIP_ID = 1103809448016879776 

UYE_ROL_ID = 1469284940863504457       
KAYITSIZ_ROL_ID = 1469385270703947986  

# ====================
# BOT AYARLARI
# ====================
intents = discord.Intents.default()
intents.members = True  
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

def yetkili_mi(ctx):
    return (ctx.author.id == BOT_SAHIP_ID or 
            ctx.author.id == ctx.guild.owner_id or 
            ctx.author.guild_permissions.administrator)

# ====================
# OTOMATİK ROL VERME
# ====================
@bot.event
async def on_member_join(member):
    """Yeni girenlere otomatik kayıtsız rolü verir."""
    try:
        rol = member.guild.get_role(KAYITSIZ_ROL_ID)
        if rol: await member.add_roles(rol)
    except: pass

@bot.event
async def on_ready():
    print(f"🚀 {bot.user} Aktif!")

# ====================
# HATA YÖNETİMİ (ÖNERİ SİSTEMİ)
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
# KIRMIZI YÖNETİCİ PANELİ (BOZULMADI)
# ====================
@bot.command()
async def admin(ctx):
    if not yetkili_mi(ctx): return
    
    embed = discord.Embed(
        title="🛑 ÇAKIRBEYLİ",
        description="Sunucu güvenliği ve düzeni için aşağıdaki yetkili araçlarını kullanın.",
        color=0xFF0000 
    )
    
    embed.add_field(name="👥 KAYIT YÖNETİMİ", value="> `!kayit @üye/ID`\n> `!unkayit @üye/ID`", inline=True)
    embed.add_field(name="🎭 ROL SİSTEMİ", value="> `!rolver @üye/ID @rol`\n> `!rolal @üye/ID @rol`", inline=True)
    embed.add_field(name="🛡️ MODERASYON", value="```!ban @üye/ID\n!kick @üye/ID\n!unban [ID]```", inline=False)
    embed.add_field(name="🧹 KANAL TEMİZLİĞİ", value="`!sil [miktar]`", inline=True)
    
    embed.set_footer(text=f"{ctx.author.name} | 2026 Evo System", icon_url=ctx.author.display_avatar.url)
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    
    await ctx.send(embed=embed)

# ====================
# KOMUTLAR (ID + ETİKET DESTEKLİ)
# ====================

@bot.command()
async def kayit(ctx, user: Union[discord.Member, discord.User]):
    if not yetkili_mi(ctx): return
    try:
        member = ctx.guild.get_member(user.id)
        if not member: return await ctx.send("❌ Kullanıcı bulunamadı.")
        u, k = ctx.guild.get_role(UYE_ROL_ID), ctx.guild.get_role(KAYITSIZ_ROL_ID)
        if k: await member.remove_roles(k)
        if u: await member.add_roles(u)
        await ctx.send(f"✅ {member.mention} başarıyla kayıt edildi.", delete_after=5)
    except: pass

@bot.command()
async def unkayit(ctx, user: Union[discord.Member, discord.User]):
    if not yetkili_mi(ctx): return
    try:
        member = ctx.guild.get_member(user.id)
        if not member: return
        u, k = ctx.guild.get_role(UYE_ROL_ID), ctx.guild.get_role(KAYITSIZ_ROL_ID)
        if u: await member.remove_roles(u)
        if k: await member.add_roles(k)
        await ctx.send(f"🔄 {member.mention} kayıtsıza çekildi.", delete_after=5)
    except: pass

@bot.command()
async def sil(ctx, miktar: int):
    if not yetkili_mi(ctx): return
    try:
        await ctx.channel.purge(limit=miktar + 1)
        msg = await ctx.send(f"🧹 **{miktar}** mesaj imha edildi.")
        await msg.delete(delay=3)
    except: pass

@bot.command()
async def rolver(ctx, user: Union[discord.Member, discord.User], rol: discord.Role):
    if not yetkili_mi(ctx): return
    try:
        member = ctx.guild.get_member(user.id)
        await member.add_roles(rol)
        await ctx.send(f"✅ **{rol.name}** rolü tanımlandı.", delete_after=5)
    except: pass

@bot.command()
async def rolal(ctx, user: Union[discord.Member, discord.User], rol: discord.Role):
    if not yetkili_mi(ctx): return
    try:
        member = ctx.guild.get_member(user.id)
        await member.remove_roles(rol)
        await ctx.send(f"✅ **{rol.name}** rolü geri alındı.", delete_after=5)
    except: pass

@bot.command()
async def ban(ctx, user: Union[discord.Member, discord.User], *, sebep="Belirtilmedi"):
    if not yetkili_mi(ctx): return
    try:
        await ctx.guild.ban(user, reason=sebep)
        await ctx.send(f"🔨 {user.name} sunucudan yasaklandı.")
    except: pass

@bot.command()
async def kick(ctx, user: Union[discord.Member, discord.User], *, sebep="Belirtilmedi"):
    if not yetkili_mi(ctx): return
    try:
        await ctx.guild.kick(user, reason=sebep)
        await ctx.send(f"👢 {user.name} sunucudan atıldı.")
    except: pass

@bot.command()
async def unban(ctx, user_id: int):
    if not yetkili_mi(ctx): return
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ {user.name} kullanıcısının yasağı kaldırıldı.")
    except: pass

bot.run(TOKEN)
