#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import json
import os
import time
from datetime import datetime

# ============ KONFIGURASI ============
API_ID = 123456  # Ganti dengan API ID lo
API_HASH = "your_api_hash"  # Ganti dengan API Hash lo
BOT_TOKEN = None  # Biarin kosong kalo pake userbot
SESSION_NAME = "userbot"

BLACKLIST_FILE = "blacklist.json"
SETTINGS_FILE = "settings.json"
LOG_FILE = "logs.txt"

# ============ LOAD DATA ============
def load_json(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

blacklist = load_json(BLACKLIST_FILE)
settings = load_json(SETTINGS_FILE)

# ============ INISIALISASI CLIENT ============
app = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    workers=8
)

# ============ FUNGSI BANTUAN ============
def log_activity(text):
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{datetime.now()}] {text}\n")

async def is_blacklisted(chat_id):
    return str(chat_id) in blacklist.get('chats', [])

def get_prefix():
    return settings.get('prefix', '.')

# ============ HANDLER COMMAND ============
@app.on_message(filters.command("help", prefixes=get_prefix()))
async def help_command(client, message: Message):
    prefix = get_prefix()
    text = f"""
**🤖 USERBOT TELEGRAM v2.0**

**📌 COMMAND LIST:**

**⚡ BASIC:**
`{prefix}help` - Tampilkan menu ini
`{prefix}ping` - Cek status bot
`{prefix}id` - Lihat ID chat/group
`{prefix}me` - Info akun sendiri

**📋 BLACKLIST GROUP:**
`{prefix}addbl` - Tambah group ke blacklist (reply ke pesan group)
`{prefix}listbl` - Lihat daftar blacklist
`{prefix}delbl` - Hapus dari blacklist

**📤 FORWARD SYSTEM:**
`{prefix}cfd` - Forward pesan yang di-reply ke semua group (kecuali blacklist)
`{prefix}cfdall` - Forward ke semua group (termasuk blacklist)

**📢 BROADCAST:**
`{prefix}bc` - Broadcast pesan ke semua group (reply ke pesan)
`{prefix}bcf` - Broadcast dengan format pesan

**🗑️ CLEANER:**
`{prefix}del` - Hapus pesan bot di group (reply ke pesan bot)
`{prefix}purge` - Hapus banyak pesan (reply ke pesan terakhir)

**🔧 SETTINGS:**
`{prefix}setprefix` - Ganti prefix command
`{prefix}setdelay` - Set delay forward (detik)

**📊 STATS:**
`{prefix}stats` - Lihat statistik bot
`{prefix}log` - Lihat log aktivitas

**🔄 MISC:**
`{prefix}restart` - Restart userbot
`{prefix}clone` - Clone pesan ke group tertentu
"""

    await message.reply(text, parse_mode=enums.ParseMode.MARKDOWN)

@app.on_message(filters.command("ping", prefixes=get_prefix()))
async def ping_command(client, message: Message):
    start = time.time()
    msg = await message.reply("🏓 **Pinging...**")
    end = time.time()
    await msg.edit(f"🏓 **Pong!**\n⚡ Latency: `{round((end - start) * 1000)}ms`")

@app.on_message(filters.command("id", prefixes=get_prefix()))
async def id_command(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = f"""
**📌 CHAT INFO:**
Chat ID: `{chat_id}`
Type: `{message.chat.type}`

**👤 USER INFO:**
User ID: `{user_id}`
Username: @{message.from_user.username or 'None'}
First Name: {message.from_user.first_name}
"""
    await message.reply(text)

@app.on_message(filters.command("me", prefixes=get_prefix()))
async def me_command(client, message: Message):
    user = await client.get_me()
    text = f"""
**👤 AKUN SAYA:**
ID: `{user.id}`
Username: @{user.username}
First Name: {user.first_name}
Last Name: {user.last_name or 'None'}
Is Premium: {user.is_premium}
DC: {user.dc_id}
"""
    await message.reply(text)

# ============ BLACKLIST ============
@app.on_message(filters.command("addbl", prefixes=get_prefix()))
async def add_blacklist(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("❌ **Reply ke pesan di group yang mau di-blacklist!**")

    chat_id = message.reply_to_message.chat.id
    chat_title = message.reply_to_message.chat.title or "Private"

    if 'chats' not in blacklist:
        blacklist['chats'] = {}

    if str(chat_id) in blacklist['chats']:
        return await message.reply(f"⚠️ **Group `{chat_title}` sudah ada di blacklist!**")

    blacklist['chats'][str(chat_id)] = {
        'title': chat_title,
        'added_by': message.from_user.id,
        'added_at': datetime.now().isoformat()
    }
    save_json(BLACKLIST_FILE, blacklist)

    await message.reply(f"""
✅ **Berhasil menambahkan blacklist!**
📌 Group: `{chat_title}`
🆔 ID: `{chat_id}`
👤 Added by: {message.from_user.first_name}
""")

@app.on_message(filters.command("listbl", prefixes=get_prefix()))
async def list_blacklist(client, message: Message):
    if 'chats' not in blacklist or not blacklist['chats']:
        return await message.reply("📭 **Belum ada group di blacklist.**")

    text = "**📋 DAFTAR BLACKLIST GROUP:**\n\n"
    for idx, (chat_id, data) in enumerate(blacklist['chats'].items(), 1):
        text += f"{idx}. **{data['title']}**\n"
        text += f"   🆔 `{chat_id}`\n"
        text += f"   👤 Added by: `{data['added_by']}`\n\n"

    await message.reply(text)

@app.on_message(filters.command("delbl", prefixes=get_prefix()))
async def del_blacklist(client, message: Message):
    if 'chats' not in blacklist or not blacklist['chats']:
        return await message.reply("📭 **Belum ada group di blacklist.**")

    if not message.reply_to_message:
        return await message.reply("❌ **Reply ke pesan di group yang mau dihapus dari blacklist!**")

    chat_id = str(message.reply_to_message.chat.id)
    if chat_id not in blacklist['chats']:
        return await message.reply("❌ **Group ini tidak ada di blacklist!**")

    del blacklist['chats'][chat_id]
    save_json(BLACKLIST_FILE, blacklist)
    await message.reply(f"✅ **Berhasil menghapus group dari blacklist!**")

# ============ FORWARD SYSTEM ============
@app.on_message(filters.command("cfd", prefixes=get_prefix()))
async def forward_to_all(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("❌ **Reply ke pesan yang mau di-forward!**")

    msg = await message.reply("⏳ **Sedang memproses forward...**")
    
    target_msg = message.reply_to_message
    total_chats = 0
    success = 0
    failed = 0
    blacklisted = 0

    async for dialog in client.get_dialogs():
        if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            total_chats += 1
            
            # Cek blacklist
            if str(dialog.chat.id) in blacklist.get('chats', {}):
                blacklisted += 1
                continue

            try:
                await client.forward_messages(
                    dialog.chat.id,
                    target_msg.chat.id,
                    target_msg.id
                )
                success += 1
            except Exception as e:
                failed += 1
                log_activity(f"Failed forward to {dialog.chat.id}: {e}")
            
            await asyncio.sleep(settings.get('delay', 1))

    await msg.edit(f"""
✅ **FORWARD COMPLETE!**

📊 **STATISTIK:**
✅ Sukses: `{success}` group
❌ Gagal: `{failed}` group
🚫 Blacklisted: `{blacklisted}` group
📌 Total group: `{total_chats}`
⏱️ Delay: `{settings.get('delay', 1)}s`
""")

@app.on_message(filters.command("cfdall", prefixes=get_prefix()))
async def forward_to_all_including_blacklist(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("❌ **Reply ke pesan yang mau di-forward!**")

    msg = await message.reply("⏳ **Forwarding ke semua group...**")
    target_msg = message.reply_to_message
    success = 0
    failed = 0

    async for dialog in client.get_dialogs():
        if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            try:
                await client.forward_messages(
                    dialog.chat.id,
                    target_msg.chat.id,
                    target_msg.id
                )
                success += 1
            except Exception as e:
                failed += 1
            await asyncio.sleep(settings.get('delay', 1))

    await msg.edit(f"""
✅ **FORWARD ALL COMPLETE!**
✅ Sukses: `{success}` group
❌ Gagal: `{failed}` group
""")

# ============ BROADCAST ============
@app.on_message(filters.command("bc", prefixes=get_prefix()))
async def broadcast_command(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("❌ **Reply ke pesan yang mau di-broadcast!**")

    msg = await message.reply("⏳ **Broadcasting...**")
    target_msg = message.reply_to_message
    success = 0
    failed = 0

    async for dialog in client.get_dialogs():
        if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            try:
                await client.copy_message(
                    dialog.chat.id,
                    target_msg.chat.id,
                    target_msg.id
                )
                success += 1
            except Exception as e:
                failed += 1
            await asyncio.sleep(0.5)

    await msg.edit(f"""
✅ **BROADCAST COMPLETE!**
✅ Sukses: `{success}` group
❌ Gagal: `{failed}` group
""")

# ============ CLEANER ============
@app.on_message(filters.command("del", prefixes=get_prefix()))
async def delete_bot_messages(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("❌ **Reply ke pesan bot yang mau dihapus!**")

    try:
        await message.reply_to_message.delete()
        await message.delete()
    except Exception as e:
        await message.reply(f"❌ Gagal menghapus: {e}")

@app.on_message(filters.command("purge", prefixes=get_prefix()))
async def purge_command(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("❌ **Reply ke pesan terakhir yang mau di-purge!**")

    msg = await message.reply("⏳ **Menghapus pesan...**")
    count = 0
    
    async for msg_purge in client.get_chat_history(message.chat.id):
        if msg_purge.id == message.reply_to_message.id:
            await msg_purge.delete()
            count += 1
            break
        await msg_purge.delete()
        count += 1

    await msg.edit(f"✅ **Berhasil menghapus {count} pesan!**")

# ============ SETTINGS ============
@app.on_message(filters.command("setprefix", prefixes=get_prefix()))
async def set_prefix(client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("❌ **Gunakan: `.setprefix [prefix]`**")
    
    settings['prefix'] = args[1]
    save_json(SETTINGS_FILE, settings)
    await message.reply(f"✅ **Prefix diubah menjadi: `{args[1]}`**")

@app.on_message(filters.command("setdelay", prefixes=get_prefix()))
async def set_delay(client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("❌ **Gunakan: `.setdelay [detik]`**")
    
    try:
        delay = float(args[1])
        settings['delay'] = delay
        save_json(SETTINGS_FILE, settings)
        await message.reply(f"✅ **Delay diubah menjadi: `{delay}s`**")
    except ValueError:
        await message.reply("❌ **Masukkan angka yang valid!**")

# ============ STATS ============
@app.on_message(filters.command("stats", prefixes=get_prefix()))
async def stats_command(client, message: Message):
    total_groups = 0
    total_users = 0
    
    async for dialog in client.get_dialogs():
        if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            total_groups += 1
        elif dialog.chat.type == enums.ChatType.PRIVATE:
            total_users += 1

    blacklist_count = len(blacklist.get('chats', {}))

    text = f"""
**📊 STATISTIK BOT:**
👥 Total User: `{total_users}`
👨‍👩‍👧‍👦 Total Group: `{total_groups}`
🚫 Blacklist: `{blacklist_count}`
⚡ Prefix: `{settings.get('prefix', '.')}`
⏱️ Delay: `{settings.get('delay', 1)}s`
"""
    await message.reply(text)

@app.on_message(filters.command("log", prefixes=get_prefix()))
async def log_command(client, message: Message):
    if not os.path.exists(LOG_FILE):
        return await message.reply("📭 **Belum ada log.**")
    
    with open(LOG_FILE, 'r') as f:
        logs = f.read().splitlines()[-20:]
    
    text = "**📋 LOG AKTIVITAS (20 terakhir):**\n```\n" + "\n".join(logs) + "\n```"
    await message.reply(text[:4000])

# ============ MISC ============
@app.on_message(filters.command("restart", prefixes=get_prefix()))
async def restart_command(client, message: Message):
    await message.reply("🔄 **Restarting userbot...**")
    os.system("pkill -f userbot.py")
    os.system("python3 userbot.py &")

@app.on_message(filters.command("clone", prefixes=get_prefix()))
async def clone_command(client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("❌ **Gunakan: `.clone [chat_id]`**")
    
    if not message.reply_to_message:
        return await message.reply("❌ **Reply ke pesan yang mau di-clone!**")

    try:
        target_chat = int(args[1])
        await client.copy_message(
            target_chat,
            message.reply_to_message.chat.id,
            message.reply_to_message.id
        )
        await message.reply(f"✅ **Pesan berhasil di-clone ke `{target_chat}`**")
    except Exception as e:
        await message.reply(f"❌ **Gagal clone: {e}**")

# ============ START BOT ============
print("""
╔═══════════════════════════════════════╗
║   🤖 USERBOT TELEGRAM AKTIF!          ║
║   🔥 Siap Tempur Bos!                 ║
║   📌 Gunakan .help untuk menu         ║
╚═══════════════════════════════════════╝
""")

app.run()
