import discord
from discord.ext import commands
import json
import os
import difflib

# ====================
# AYARLAR
# ====================
TOKEN = os.getenv("TOKEN")
BOT_SAHIP_ID = 1103809448016879776  

CONFIG_DOSYA = "config.json"

# ====================
# CONFIG (KALICI HAFIZA)
# ====================
if os.path.exists(CONFIG_DOSYA):
    with open(CONFIG_DOSYA, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
else:
    CONFIG = {"ROLLER": {}}
    with open(CONFIG_DOSYA, "w", encoding="utf-8") as f:
        json.dump(CONFIG, f, indent=4)

def config_kaydet():
    with open(CONFIG_DOSYA, "w", encoding="utf-8") as f:
        json.dump(CONFIG, f, indent=4)

# Guild ID'leri int'e çevir
CONFIG["ROLLER"] = {int(k): v for k, v in CONFIG.get("ROLLER", {}).items()}

# ====================
# BOT AYARLARI
# ====================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ====================
# YARDIMCI FONKSİYONLAR
# ====================
def bot_sahibi_mi(ctx):
    return ctx.author.id == BOT_SAHIP_ID

def yetkili_kurucu_mu(ctx):
    return ctx.author.id == ctx.guild.owner_id or bot_sahibi_mi(ctx)

def get_roller(guild_id):
    return CONFIG["ROLLER"].get(guild_id)

def yetkili_mi(member):
    r = get_roller(member.guild.id)
    if not r or "yetkili" not in r:
        return False
    rol = member.guild.get_role(r["yetkili"])
    return rol in member.roles if rol else False

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
        else:
            await ctx.send("❌ Komut bulunamadı.")

# ====================
# KURULUM VE AYARLAR
# ====================
@bot.command()
async def kurulum(ctx):
    if not yetkili_kurucu_mu(ctx):
        await ctx.send("❌ Bu komutu sadece **sunucu sahibi** kullanabilir.")
        return

    CONFIG["ROLLER"][ctx.guild.id] = {
        "kayitsiz": None,
        "uye": None,
        "yetkili": None
    }
    config_kaydet()
    await ctx.send("✅ Sistem hazır. Şimdi `!rolver` komutu ile rolleri tanımlayın.")

@bot.command()
async def rolver(ctx, tur: str, rol: discord.Role, member: discord.Member = None):
    """Örn: !rolver yetkili @Rol @Kullanıcı"""
    if not yetkili_kurucu_mu(ctx):
        await ctx.send("❌ Yetkin yetersiz.")
        return

    tur = tur.lower()
    if tur not in ["kayitsiz", "uye", "yetkili"]:
        await ctx.send("❌ Geçersiz tür! Kullanabileceklerin: `kayitsiz`, `uye`, `yetkili`")
        return

    if ctx.guild.id not in CONFIG["ROLLER"]:
        await ctx.send("❌ Lütfen önce `!kurulum` yapın.")
        return

    CONFIG["ROLLER"][ctx.guild.id][tur] = rol.id
    config_kaydet()

    mesaj = f"✅ `{tur}` rolü **{rol.name}** olarak kaydedildi."

    if member:
        try:
            await member.add_roles(rol)
            mesaj += f"\n👤 {member.mention} kullanıcısına rol verildi."
        except discord.Forbidden:
            mesaj += "\n❌ Yetkim yetmediği için rolü kullanıcıya veremedim."

    await ctx.send(mesaj)

@bot.command()
async def rolal(ctx, member: discord.Member, rol: discord.Role):
    """Örn: !rolal @Kullanıcı @Rol"""
    if not yetkili_mi(ctx.author):
        await ctx.send("❌ Bu işlem için yetkili rolüne sahip olmalısın.")
        return

    try:
        await member.remove_roles(rol)
        await ctx.send(f"✅ {member.mention} üzerinden **{rol.name}** rolü alındı.")
    except discord.Forbidden:
        await ctx.send("❌ Rolü almaya yetkim yetmiyor.")

# ====================
# KAYIT SİSTEMİ
# ====================
@bot.command()
async def kayit(ctx, member: discord.Member):
    if not yetkili_mi(ctx.author):
        await ctx.send("❌ Yetkin yok.")
        return

    r = get_roller(ctx.guild.id)
    if not r: return

    kayitsiz = ctx.guild.get_role(r["kayitsiz"])
    uye = ctx.guild.get_role(r["uye"])

    if kayitsiz: await member.remove_roles(kayitsiz)
    if uye: await member.add_roles(uye)

    await ctx.send(f"✅ {member.mention} başarıyla kayıt edildi.")

@bot.command()
async def unkayit(ctx, member: discord.Member):
    if not yetkili_mi(ctx.author):
        await ctx.send("❌ Yetkin yok.")
        return

    r = get_roller(ctx.guild.id)
    if not r: return

    kayitsiz = ctx.guild.get_role(r["kayitsiz"])
    uye = ctx.guild.get_role(r["uye"])

    if uye: await member.remove_roles(uye)
    if kayitsiz: await member.add_roles(kayitsiz)

    await ctx.send(f"🔄 {member.mention} tekrar kayıtsıza atıldı.")

@bot.event
async def on_member_join(member):
    r = get_roller(member.guild.id)
    if r and r.get("kayitsiz"):
        rol = member.guild.get_role(r["kayitsiz"])
        if rol:
            try: await member.add_roles(rol)
            except: pass

# ====================
# MODERASYON
# ====================
@bot.command()
async def sil(ctx, miktar: int):
    if not yetkili_mi(ctx.author):
        await ctx.send("❌ Yetkin yok.")
        return
    await ctx.channel.purge(limit=miktar + 1)
    msg = await ctx.send(f"🧹 {miktar} mesaj temizlendi.")
    await msg.delete(delay=3)

@bot.command()
async def ban(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    if not yetkili_mi(ctx.author): return
    await member.ban(reason=sebep)
    await ctx.send(f"🔨 {member.name} banlandı. Sebep: {sebep}")

@bot.command()
async def kick(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    if not yetkili_mi(ctx.author): return
    await member.kick(reason=sebep)
    await ctx.send(f"👢 {member.name} atıldı. Sebep: {sebep}")

@bot.command()
async def unban(ctx, user_id: int):
    if not yetkili_mi(ctx.author): return
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ {user.name} yasağı kaldırıldı.")

# ====================
# BAŞLAT
# ====================
bot.run(TOKEN)