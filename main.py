import discord
import asyncio
import os
from colorama import init, Fore, Style

init(autoreset=True)

LOGO = r"""
  ________                                ____  __.__                
 /  _____/_____    _____   ___________|    |/ _|__| ____   ______
/   \  ___\__  \  /     \_/ __ \_  __ \    |  < |  |/    \ / ____/
\    \_\  \/ __ \|  Y Y  \  ___/|  | \/    |  \|  |   |  < <_|  | 
 \______  (____  /__|_|  /\___  >__|  |____|__ \__|___|  /\__   |
        \/     \/      \/      \/              \/       \/    |__|
            GAMEKING PROFESYONEL TEK PARÇA AKTARICI v5.1
"""

class GameKingFullCloner(discord.Client):
    def __init__(self, kopyalanacak_id, yeni_id):
        super().__init__()
        self.k_id = kopyalanacak_id
        self.y_id = yeni_id

    async def on_ready(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + LOGO)
        print(f"{Fore.GREEN}[*] Giriş Yapıldı: {self.user}")

        eski_s = self.get_guild(self.k_id)
        yeni_s = self.get_guild(self.y_id)

        if not eski_s or not yeni_s:
            print(f"{Fore.RED}[!] HATA: Sunucular bulunamadı! ID'leri kontrol edin.")
            return await self.close()

        print(f"{Fore.YELLOW}[i] Aktarım Başlıyor: {eski_s.name} -> {yeni_s.name}")
        print("-" * 50)

        # 1. SUNUCU AYARLARI
        try:
            icon = await eski_s.icon_url.read() if hasattr(eski_s, 'icon_url') and eski_s.icon else None
            await yeni_s.edit(name=eski_s.name, icon=icon)
            print(f"{Fore.BLUE}[+] Sunucu ismi ve simgesi güncellendi.")
        except: pass

        # 2. ROLLERİ KOPYALA
        rol_map = {}
        print(f"{Fore.YELLOW}[*] Roller kopyalanıyor...")
        for rol in sorted(eski_s.roles, key=lambda x: x.position):
            if rol.is_default() or rol.managed: continue
            try:
                yeni_rol = await yeni_s.create_role(
                    name=rol.name, permissions=rol.permissions, 
                    colour=rol.colour, hoist=rol.hoist, mentionable=rol.mentionable
                )
                rol_map[rol.id] = yeni_rol
                print(f"{Fore.BLUE}  ﹂ Rol: {rol.name}")
            except: continue

        # 3. KANALLARI TEMİZLE VE KOPYALA
        print(f"{Fore.YELLOW}[*] Kanallar ve mesajlar aktarılıyor...")
        for ch in yeni_s.channels:
            try: await ch.delete()
            except: pass

        for kat in sorted(eski_s.categories, key=lambda x: x.position):
            try:
                # İzinleri eşleştir
                izinler = {rol_map[r.id]: ow for r, ow in kat.overwrites.items() if isinstance(r, discord.Role) and r.id in rol_map}
                yeni_kat = await yeni_s.create_category(name=kat.name, overwrites=izinler)
                print(f"{Fore.MAGENTA}[+] Kategori: {kat.name}")

                for ch in kat.channels:
                    c_izin = {rol_map[r.id]: ow for r, ow in ch.overwrites.items() if isinstance(r, discord.Role) and r.id in rol_map}
                    if isinstance(ch, discord.TextChannel):
                        yeni_ch = await yeni_kat.create_text_channel(name=ch.name, overwrites=c_izin, topic=ch.topic)
                        # Mesaj Geçmişi (Son 10 mesaj)
                        try:
                            async for m in ch.history(limit=10, oldest_first=True):
                                if m.content: await yeni_ch.send(f"**{m.author.name}**: {m.content}")
                        except: pass
                    elif isinstance(ch, discord.VoiceChannel):
                        await yeni_kat.create_voice_channel(name=ch.name, overwrites=c_izin)
                    
                    print(f"{Fore.MAGENTA}  ﹂ Kanal: {ch.name}")
                    await asyncio.sleep(0.8)
            except discord.errors.Forbidden:
                print(f"{Fore.RED}[!] YETKİ HATASI: Yeni sunucuda yönetici yetkiniz olduğundan emin olun!")
            except Exception: # Hata buradaydı, : eklendi.
                continue

        print("-" * 50)
        print(f"{Fore.GREEN}[!!!] TÜM İŞLEMLER TAMAMLANDI!")
        await self.close()

if __name__ == "__main__":
    tkn = input("Hesap Tokeninizi Girin: ")
    try:
        k_id = int(input("Kopyalanacak Sunucu ID: "))
        y_id = int(input("Yeni Sunucu ID: "))
        
        bot = GameKingFullCloner(k_id, y_id)
        bot.run(tkn, bot=False)
    except Exception as ex:
        print(f"Hata: {ex}")