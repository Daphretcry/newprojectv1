import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from sms import SendSms  # sms.py içindeki sınıf

# === Bot token ===
token = "BOT_TOKEN"  # Buraya bot tokenini yerleştirin.

# === Discord bot ayarları ===
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === Bot açıldığında çalışacak olan event ===
@bot.event
async def on_ready():
    await bot.tree.sync()  # Slash komutları senkronize et
    print(f"✅ Bot {bot.user} olarak giriş yaptı ve slash komutlar senkronize edildi.")

# === SMS Gönderme Slash Komutu ===
@bot.tree.command(name="sms", description="Telefon numarasına SMS gönder.")
async def sms_command(interaction: discord.Interaction, telefon: str, adet: int, saniye: int):
    await interaction.response.send_message(
        f"📨 {telefon} numarasına {adet} SMS gönderimi başlatılıyor. Her {saniye} saniyede bir mesaj gidecek.",
        ephemeral=True  # Yalnızca komutu kullanan kişi görecek
    )

    sms = SendSms(telefon, "")  # sms.py içindeki sınıfı kullanıyoruz

    for attribute in dir(SendSms):
        attribute_value = getattr(sms, attribute)
        if callable(attribute_value) and not attribute.startswith('__'):
            if sms.adet >= adet:
                break
            exec("sms." + attribute + "()")
            await asyncio.sleep(saniye)

    await interaction.followup.send(
        f"✅ Gönderim tamamlandı: {telefon} numarasına {sms.adet} SMS gönderildi.",
        ephemeral=True  # Bu mesaj da gizli
    )

# === Yardım Komutu ===
@bot.tree.command(name="help", description="Kullanım talimatlarını gösterir.")
async def help_command(interaction: discord.Interaction):
    mesaj = (
        "📘 **SMS Gönderme Talimatı**\n"
        "Komut formatı: `/sms <telefon> <adet> <saniye>`\n"
        "Örnek: `/sms 5051234567 20 1`\n\n"
        "Ayrıca `/status` komutu ile botun aktif olup olmadığını kontrol edebilirsin."
    )
    await interaction.response.send_message(mesaj, ephemeral=True)

# === Durum Komutu ===
@bot.tree.command(name="status", description="Botun aktif olup olmadığını gösterir.")
async def status_command(interaction: discord.Interaction):
    await interaction.response.send_message("✅ Bot şu anda aktif ve çalışıyor!", ephemeral=True)

# === DM'den gelen komutları engelleme ===
@bot.event
async def on_message(message):
    # Botun kendisinin yazdığı mesajları yok sayıyoruz
    if message.author == bot.user:
        return

    # Eğer mesaj DM kanalından geldiyse, komutları engelliyoruz
    if isinstance(message.channel, discord.DMChannel):
        await message.delete()  # Yanlış komut mesajını siliyoruz

        try:
            # Kullanıcıya DM olarak hata mesajı gönderiyoruz
            await message.author.send(
                "⚠️ **Burada komutları kullanamazsınız!**\n"
                "Komutları yalnızca **sunucumuzda** kullanabilirsiniz.\n"
                "Lütfen aşağıdaki linke tıklayarak sunucumuza katılın:\n"
                "https://discord.gg/prBpnVQ37B"
            )
        except discord.Forbidden:
            # Eğer kullanıcı DM'yi kapatmışsa, hata mesajını genel kanala gönderiyoruz
            await message.channel.send(
                f"{message.author.mention} ⚠️ **Burada komutları kullanamazsınız!**\n"
                "Komutları yalnızca **sunucumuzda** kullanabilirsiniz.\n"
                "Lütfen aşağıdaki linke tıklayarak sunucumuza katılın:\n"
                "https://discord.gg/prBpnVQ37B"
            )
        return  # Burada komutları işlemiyoruz

    # Slash komutlarını işlemeye devam etsin (sadece sunucularda)
    await bot.process_commands(message)

# === Botu çalıştır ===
bot.run(token)
