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

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

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
    # Komut bulunamadığında öneri yapar, yetkisiz kullanımda susar
    if isinstance(error, commands.CommandNotFound):
        komutlar = [cmd.name for cmd in bot.commands]
        yazilan = ctx.message.content.replace("!", "").split()[0]
        olasi = difflib.get_close_matches(yazilan, komutlar, n=1)
        if olasi:
            await ctx.send(f"❌ `{yazilan}` diye bir komut yok. `{olasi[0]}` mı demek istedin?", delete_after=5)

# ====================
# ADMIN YARDIM PANELİ
# ====================
@bot.command()
async def admin(ctx):
    if not yetkili_mi(ctx): return
    
    embed = discord.Embed(
        title="🛠️ Yetkili Komut Paneli",
        description="Sadece yöneticilerin kullanabileceği komutlar aşağıdadır:",
        color=discord.Color.blue()
    )
    embed.add_field(name="👤 Kayıt Sistemleri", value="`!kayit @üye` - Üye rolü verir, kayıtsızı alır.\n`!unkayit @üye` - Kayıtsız rolü verir, üyeyi alır.", inline=False)
    embed.add_field(name="🎭 Rol Yönetimi", value="`!rolver @üye @rol` - Belirtilen rolü verir.\n`!rolal @üye @rol` - Belirtilen rolü geri alır.", inline=False)
    embed.add_field(name="🛡️ Moderasyon", value="`!ban @üye` - Kullanıcıyı yasaklar.\n`!kick @üye` - Kullanıcıyı sunucudan atar.\n`!unban ID` - Yasak kaldırır.\n`!sil [sayı]` - Mesajları temizler.", inline=False)
    embed.set_footer(text=f"Komutu kullanan: {ctx.author.name}")
    
    await ctx.send(embed=embed)

# ====================
# KAYIT SİSTEMİ
# ====================
@bot.command()
async def kayit(ctx, member: discord.Member):
    if not yetkili_mi(ctx): return
    uye_rol = ctx.guild.get_role(UYE_ROL_ID)
    kayitsiz_rol = ctx.guild.get_role(KAYITSIZ_ROL_ID)
    try:
        if kayitsiz_rol: await member.remove_roles(kayitsiz_rol)
        if uye_rol: await member.add_roles(uye_rol)
        await ctx.send(f"✅ {member.mention} başarıyla kayıt edildi.", delete_after=5)
    except: pass

@bot.command()
async def unkayit(ctx, member: discord.Member):
    if not yetkili_mi(ctx): return
    uye_rol = ctx.guild.get_role(UYE_ROL_ID)
    kayitsiz_rol = ctx.guild.get_role(KAYITSIZ_ROL_ID)
    try:
        if uye_rol: await member.remove_roles(uye_rol)
        if kayitsiz_rol: await member.add_roles(kayitsiz_rol)
        await ctx.send(f"🔄 {member.mention} kayıtsıza atıldı.", delete_after=5)
    except: pass

# ====================
# ROL YÖNETİMİ
# ====================
@bot.command()
async def rolver(ctx, member: discord.Member, rol: discord.Role):
    if not yetkili_mi(ctx): return
    try:
        await member.add_roles(rol)
        await ctx.send(f"✅ {member.mention} -> **{rol.name}** verildi.", delete_after=5)
    except: pass

@bot.command()
async def rolal(ctx, member: discord.Member, rol: discord.Role):
    if not yetkili_mi(ctx): return
    try:
        await member.remove_roles(rol)
        await ctx.send(f"✅ {member.mention} -> **{rol.name}** alındı.", delete_after=5)
    except: pass

# ====================
# MODERASYON
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
async def ban(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    if not yetkili_mi(ctx): return
    try:
        await member.ban(reason=sebep)
        await ctx.send(f"🔨 **{member.name}** banlandı.")
    except: pass

@bot.command()
async def unban(ctx, user_id: int):
    if not yetkili_mi(ctx): return
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ **{user.name}** yasağı kaldırıldı.")
    except: pass

@bot.command()
async def kick(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    if not yetkili_mi(ctx): return
    try:
        await member.kick(reason=sebep)
        await ctx.send(f"👢 **{member.name}** atıldı.")
    except: pass

bot.run(TOKEN)
