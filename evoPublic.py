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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DOSYA = os.path.join(BASE_DIR, "config.json")

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
def yetkili_mi(ctx):
    # Komutu kullanan kişi sunucu sahibi, bot sahibi veya Yönetici yetkisine sahipse True döner
    return ctx.author.guild_permissions.administrator or ctx.author.id == BOT_SAHIP_ID or ctx.author.id == ctx.guild.owner_id

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
# ROL İŞLEMLERİ
# ====================

@bot.command()
async def rolver(ctx, member: discord.Member, rol: discord.Role):
    """Örn: !rolver @Kullanıcı @Rol"""
    if not yetkili_mi(ctx):
        await ctx.send("❌ Bu komutu kullanmak için **Yönetici** yetkisine sahip olmalısın.")
        return

    try:
        await member.add_roles(rol)
        await ctx.send(f"✅ {member.mention} kullanıcısına **{rol.name}** rolü verildi.")
    except discord.Forbidden:
        await ctx.send("❌ Bu rolü vermeye yetkim yetmiyor. Bot rolünü yukarı taşımayı deneyin.")
    except Exception as e:
        await ctx.send(f"❌ Bir hata oluştu: {e}")

@bot.command()
async def rolal(ctx, member: discord.Member, rol: discord.Role):
    """Örn: !rolal @Kullanıcı @Rol"""
    if not yetkili_mi(ctx):
        await ctx.send("❌ Bu komutu kullanmak için **Yönetici** yetkisine sahip olmalısın.")
        return

    try:
        await member.remove_roles(rol)
        await ctx.send(f"✅ {member.mention} üzerinden **{rol.name}** rolü alındı.")
    except discord.Forbidden:
        await ctx.send("❌ Bu rolü almaya yetkim yetmiyor. Bot rolünü yukarı taşımayı deneyin.")
    except Exception as e:
        await ctx.send(f"❌ Bir hata oluştu: {e}")

# ====================
# BAŞLAT
# ====================
bot.run(TOKEN)
