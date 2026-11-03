import asyncio
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# ==================== CONFIGURATION ====================
# Gunakan placeholder untuk keamanan portofolio publik
TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
GAS_API_URL = os.getenv("GAS_API_URL", "YOUR_GOOGLE_APPS_SCRIPT_WEB_APP_URL")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "YOUR_TELEGRAM_CHAT_ID")
POLL_INTERVAL = 30  # Detik
# =======================================================

async def check_new_orders(context: ContextTypes.DEFAULT_TYPE):
    """Fungsi latar belakang untuk mengecek pesanan baru dari Google Sheets via GAS API"""
    try:
        response = requests.get(f"{GAS_API_URL}?action=getPendingOrders")
        if response.status_code == 200:
            data = response.json()
            orders = data.get("pendingOrders", [])
            
            for order in orders:
                order_id = order.get("orderId")
                customer_name = order.get("customerName")
                items = order.get("items")
                total = order.get("total")
                
                text = (
                    f"🚨 **PESANAN BARU MASUK!**\n\n"
                    f"🆔 ID: `{order_id}`\n"
                    f"👤 Pemesan: {customer_name}\n"
                    f"📦 Produk: {items}\n"
                    f"💰 Total: Rp {total}"
                )
                
                keyboard = [
                    [InlineKeyboardButton("🚚 Tandai Dikirim", callback_data=f"ship_{order_id}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await context.bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=text,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
    except Exception as e:
        print(f"Error polling orders: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani interaksi klik tombol inline di Telegram"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("ship_"):
        order_id = data.replace("ship_", "")
        
        # Kirim request update status ke Google Apps Script
        try:
            res = requests.post(GAS_API_URL, json={"action": "updateStatus", "orderId": order_id, "status": "Dikirim"})
            if res.status_code == 200:
                await query.edit_message_text(
                    text=f"✅ Pesanan `{order_id}` berhasil **Dikirim** dan stok telah dikurangi secara otomatis!",
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text(text=f"❌ Gagal memperbarui status pesanan {order_id}.")
        except Exception as e:
            await query.edit_message_text(text=f"⚠️ Terjadi kesalahan koneksi: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💧 Air Mata Duyung Bot System is running securely.")

def main():
    if TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("⚠️ PERINGATAN: Anda masih menggunakan Token placeholder. Harap konfigurasikan dengan benar sebelum dijalankan.")
        
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Daftarkan job polling berkala
    job_queue = app.job_queue
    job_queue.run_repeating(check_new_orders, interval=POLL_INTERVAL, first=10)
    
    print("Bot is up and running...")
    app.run_polling()

if __name__ == "__main__":
    main()