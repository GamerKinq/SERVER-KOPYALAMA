import discord
import asyncio
from colorama import Fore, Style

def log(durum, mesaj):
    renkler = {"+": Fore.GREEN, "-": Fore.RED, "!": Fore.YELLOW, "*": Fore.CYAN}
    print(f"{Style.BRIGHT}{renkler.get(durum, Fore.WHITE)}[{durum}]{Style.RESET_ALL} {mesaj}")

class KlonMotoru:
    @staticmethod
    async def ayarlar(yeni_s, eski_s):
        log("*", "Sunucu ismi ve görselleri aktarılıyor...")
        try:
            icon_data = await eski_s.icon_url.read() if eski_s.icon else None
            await yeni_s.edit(name=eski_s.name, icon=icon_data)
            log("+", "Sunucu ismi ve simgesi güncellendi.")
        except: log("!", "Sunucu ayarları kopyalanamadı.")

    @staticmethod
    async def roller(yeni_s, eski_s):
        log("*", "Roller senkronize ediliyor...")
        rol_haritasi = {}
        for rol in sorted(eski_s.roles, key=lambda x: x.position):
            if rol.is_default() or rol.managed: continue
            try:
                yeni_rol = await yeni_s.create_role(
                    name=rol.name, permissions=rol.permissions, colour=rol.colour,
                    hoist=rol.hoist, mentionable=rol.mentionable
                )
                rol_haritasi[rol.id] = yeni_rol
                log("+", f"Rol: {rol.name}")
            except: continue
        return rol_haritasi

    @staticmethod
    async def kanallar(yeni_s, eski_s, rol_haritasi):
        log("*", "Kanallar ve mesajlar taşınıyor...")
        for kategori in sorted(eski_s.categories, key=lambda x: x.position):
            try:
                izinler = {rol_haritasi[h.id]: ow for h, ow in kategori.overwrites.items() if isinstance(h, discord.Role) and h.id in rol_haritasi}
                yeni_kat = await yeni_s.create_category(name=kategori.name, overwrites=izinler)
                
                for kanal in kategori.channels:
                    k_izin = {rol_haritasi[h.id]: ow for h, ow in kanal.overwrites.items() if isinstance(h, discord.Role) and h.id in rol_haritasi}
                    if isinstance(kanal, discord.TextChannel):
                        yeni_k = await yeni_kat.create_text_channel(name=kanal.name, overwrites=k_izin, topic=kanal.topic)
                        # Mesaj Geçmişini Kopyala
                        async for m in kanal.history(limit=25):
                            if m.content: await yeni_k.send(f"**{m.author.name}**: {m.content}")
                    elif isinstance(kanal, discord.VoiceChannel):
                        await yeni_kat.create_voice_channel(name=kanal.name, overwrites=k_izin)
                    log("+", f"Kanal: {kanal.name}")
                    await asyncio.sleep(0.6)
            except: continue