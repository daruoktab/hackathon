#!/usr/bin/env python3
"""
WhatsApp Message Handler
Processes incoming WhatsApp messages and generates appropriate responses
"""

import os
import re
import tempfile
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.processor import process_invoice, save_to_database_robust
from src.analysis import analyze_invoices
from src.database import get_db_session, Invoice
from whatsapp_bot.platform_database import (
    get_or_create_platform_user,
    set_monthly_limit_platform,
    get_monthly_limit_platform,
    check_spending_limit_platform,
    init_platform_tables
)
from whatsapp_bot.waha_client import WahaClient
from telegram_bot.visualizations import get_visualization


class WhatsAppMessageHandler:
    """Handles incoming WhatsApp messages and generates responses."""
    
    def __init__(self):
        self.waha_client = WahaClient()
        # Initialize platform tables
        init_platform_tables()
    
    def extract_phone_number(self, from_field: str) -> str:
        """Extract phone number from WhatsApp message 'from' field."""
        # WhatsApp format: "6281234567890@c.us" -> "+6281234567890"
        phone = from_field.split('@')[0]
        if not phone.startswith('+'):
            phone = f'+{phone}'
        return phone
    
    def parse_command(self, text: str) -> Tuple[str, list]:
        """Parse WhatsApp message for commands."""
        text = text.strip().lower()
        
        # Handle both !command and command formats
        if text.startswith('!'):
            text = text[1:]
        
        parts = text.split()
        command = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        return command, args
    
    async def handle_webhook_message(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming webhook message from n8n/WAHA."""
        try:
            # Extract message data
            message_data = webhook_data.get('data', {})
            if not message_data:
                return {'error': 'No message data found'}
            
            from_phone = self.extract_phone_number(message_data.get('from', ''))
            message_type = message_data.get('type', 'text')
            
            # Get or create platform user
            user_id = get_or_create_platform_user(
                platform='whatsapp',
                platform_user_id=from_phone,
                phone_number=from_phone,
                display_name=message_data.get('fromMe', {}).get('pushName', f'WhatsApp User {from_phone}')
            )
            
            if message_type == 'text':
                return await self.handle_text_message(from_phone, message_data.get('body', ''))
            elif message_type == 'image':
                return await self.handle_image_message(from_phone, message_data)
            else:
                return await self.handle_unsupported_message(from_phone, message_type)
                
        except Exception as e:
            print(f"Error handling webhook message: {e}")
            return {'error': str(e)}
    
    async def handle_text_message(self, phone: str, text: str) -> Dict[str, Any]:
        """Handle text messages (commands)."""
        command, args = self.parse_command(text)
        
        # Route commands
        if command in ['start', 'hello', 'hi']:
            return await self.handle_start_command(phone)
        elif command in ['help', 'bantuan']:
            return await self.handle_help_command(phone)
        elif command in ['analysis', 'analisis', 'summary']:
            return await self.handle_analysis_command(phone)
        elif command in ['recent', 'terbaru']:
            return await self.handle_recent_invoices_command(phone)
        elif command in ['setlimit', 'limit']:
            return await self.handle_set_limit_command(phone, args)
        elif command in ['checklimit', 'ceklimit']:
            return await self.handle_check_limit_command(phone)
        elif command in ['upload', 'kirim']:
            return await self.handle_upload_instructions(phone)
        else:
            return await self.handle_unknown_command(phone, text)
    
    async def handle_image_message(self, phone: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle image messages (invoice processing)."""
        try:
            # Get media URL or ID
            media_url = message_data.get('mediaUrl')
            media_id = message_data.get('id')
            
            if not media_url and not media_id:
                return {
                    'response_type': 'text',
                    'content': '❌ Tidak dapat mengunduh gambar. Silakan coba lagi.',
                    'phone': phone
                }
            
            # Download image to temporary file
            temp_dir = tempfile.gettempdir()
            temp_filename = f"whatsapp_invoice_{phone.replace('+', '')}_{media_id or 'temp'}.jpg"
            temp_path = os.path.join(temp_dir, temp_filename)
            
            # Download media using WAHA client
            if media_id:
                success = await self.waha_client.download_media(media_id, temp_path)
            else:
                # Handle direct media URL if available
                success = False  # Implement URL download if needed
            
            if not success:
                return {
                    'response_type': 'text',
                    'content': '❌ Gagal mengunduh gambar. Silakan coba lagi.',
                    'phone': phone
                }
            
            # Process invoice
            response = await self.process_invoice_image(phone, temp_path)
            
            # Cleanup
            try:
                os.remove(temp_path)
            except:
                pass
            
            return response
            
        except Exception as e:
            print(f"Error handling image message: {e}")
            return {
                'response_type': 'text',
                'content': f'❌ Error memproses gambar: {str(e)}',
                'phone': phone
            }
    
    async def process_invoice_image(self, phone: str, image_path: str) -> Dict[str, Any]:
        """Process invoice image and return response."""
        try:
            # Send processing message
            await self.waha_client.send_text_message(phone, "📄 Memproses invoice... Mohon tunggu.")
            
            # Process the invoice
            invoice_data = process_invoice(image_path)
            
            if invoice_data:
                # Save to database
                save_to_database_robust(invoice_data, image_path)
                
                # Check spending limit
                amount = invoice_data.get('total_amount', 0)
                status = check_spending_limit_platform('whatsapp', phone, amount)
                
                # Format response
                response_text = (
                    f"✅ Invoice berhasil diproses!\n\n"
                    f"📅 Tanggal: {invoice_data.get('invoice_date', 'Tidak diketahui')}\n"
                    f"🏢 Toko: {invoice_data.get('shop_name', 'Tidak diketahui')}\n"
                    f"💰 Total: Rp {amount:,.2f}\n"
                    f"📝 Items: {len(invoice_data.get('items', []))} items\n\n"
                    f"Ketik 'analysis' untuk melihat analisis lengkap."
                )
                
                # Send main response
                main_response = {
                    'response_type': 'text',
                    'content': response_text,
                    'phone': phone
                }
                
                # Check if spending limit warning needed
                if status['has_limit']:
                    if status['exceeds_limit']:
                        warning_text = (
                            "⚠️ PERINGATAN: Pembelian ini melebihi batas pengeluaran bulanan!\n\n"
                            f"{status['message']}"
                        )
                        await self.waha_client.send_text_message(phone, warning_text)
                    elif status['percentage_used'] >= 90:
                        warning_text = (
                            "⚡ PERHATIAN: Anda mendekati batas pengeluaran bulanan!\n\n"
                            f"{status['message']}"
                        )
                        await self.waha_client.send_text_message(phone, warning_text)
                
                return main_response
            else:
                return {
                    'response_type': 'text',
                    'content': '❌ Gagal memproses invoice. Pastikan gambar jelas dan coba lagi.',
                    'phone': phone
                }
                
        except Exception as e:
            print(f"Error processing invoice: {e}")
            return {
                'response_type': 'text',
                'content': f'❌ Error memproses invoice: {str(e)}',
                'phone': phone
            }
    
    async def handle_start_command(self, phone: str) -> Dict[str, Any]:
        """Handle start/welcome command."""
        welcome_text = (
            "👋 Halo! Saya Invoice Helper Bot untuk WhatsApp!\n\n"
            "Saya dapat membantu Anda:\n"
            "📸 Kirim foto struk/invoice untuk diproses\n"
            "📊 Lihat analisis pengeluaran dengan grafik\n"
            "💰 Set dan track budget bulanan\n"
            "📋 Cek riwayat pengeluaran\n\n"
            "💡 Perintah yang tersedia:\n"
            "• Kirim foto invoice langsung\n"
            "• 'analysis' - Lihat analisis & grafik\n"
            "• 'recent' - 5 invoice terbaru\n"
            "• 'setlimit 5000000' - Set budget\n"
            "• 'checklimit' - Cek status budget\n"
            "• 'help' - Bantuan lengkap\n\n"
            "📱 Mulai dengan mengirim foto struk Anda!"
        )
        
        return {
            'response_type': 'text',
            'content': welcome_text,
            'phone': phone
        }
    
    async def handle_help_command(self, phone: str) -> Dict[str, Any]:
        """Handle help command."""
        help_text = (
            "📱 Panduan Invoice Helper Bot:\n\n"
            "📸 Proses Struk/Invoice:\n"
            "• Kirim foto struk langsung ke chat ini\n"
            "• Pastikan foto jelas dan mudah dibaca\n"
            "• Format: JPG, PNG\n\n"
            "💰 Kelola Pengeluaran:\n"
            "• 'analysis' - Analisis & visualisasi lengkap\n"
            "• 'recent' - 5 transaksi terakhir\n\n"
            "🎯 Manajemen Budget:\n"
            "• 'setlimit 5000000' - Set budget Rp 5 juta\n"
            "• 'checklimit' - Cek status pengeluaran\n\n"
            "Perintah Lain:\n"
            "• 'start' - Menu utama\n"
            "• 'help' - Panduan ini\n\n"
            "💡 Tips: Pastikan foto struk terang dan tidak blur!"
        )
        
        return {
            'response_type': 'text',
            'content': help_text,
            'phone': phone
        }
    
    async def handle_analysis_command(self, phone: str) -> Dict[str, Any]:
        """Handle analysis command."""
        try:
            # Send text summary first
            analysis = analyze_invoices()
            
            summary_text = (
                "📊 Ringkasan Invoice\n\n"
                f"Total Invoice: {analysis['total_invoices']}\n"
                f"Total Pengeluaran: Rp {analysis['total_spent']:,.2f}\n"
                f"Rata-rata: Rp {analysis['average_amount']:,.2f}\n\n"
                "Top Vendor:\n"
            )
            
            for vendor in analysis['top_vendors'][:3]:
                summary_text += f"• {vendor['name']}: Rp {vendor['total']:,.2f}\n"
            
            # Send text summary
            await self.waha_client.send_text_message(phone, summary_text)
            
            # Generate and send visualization
            await self.waha_client.send_text_message(phone, "📊 Membuat dashboard analisis...")
            
            # Get visualization
            viz_buffer = get_visualization()
            
            # Save to temporary file
            temp_dir = tempfile.gettempdir()
            viz_filename = f"whatsapp_analysis_{phone.replace('+', '')}.png"
            viz_path = os.path.join(temp_dir, viz_filename)
            
            with open(viz_path, 'wb') as f:
                f.write(viz_buffer.getvalue())
            
            # Send image
            success = await self.waha_client.send_image(
                phone, 
                viz_path, 
                "📊 Dashboard Analisis Pengeluaran Anda"
            )
            
            # Cleanup
            try:
                os.remove(viz_path)
            except:
                pass
            
            if success:
                return {
                    'response_type': 'text',
                    'content': '✅ Analisis lengkap telah dikirim!',
                    'phone': phone
                }
            else:
                return {
                    'response_type': 'text',
                    'content': '❌ Gagal mengirim grafik analisis.',
                    'phone': phone
                }
                
        except Exception as e:
            print(f"Error in analysis command: {e}")
            return {
                'response_type': 'text',
                'content': f'❌ Error mendapatkan analisis: {str(e)}',
                'phone': phone
            }
    
    async def handle_recent_invoices_command(self, phone: str) -> Dict[str, Any]:
        """Handle recent invoices command."""
        try:
            session = get_db_session()
            invoices = session.query(Invoice).order_by(Invoice.processed_at.desc()).limit(5).all()
            
            if not invoices:
                return {
                    'response_type': 'text',
                    'content': 'Belum ada invoice dalam database.',
                    'phone': phone
                }
            
            response_text = "🧾 5 Invoice Terakhir:\n\n"
            for inv in invoices:
                response_text += (
                    f"📅 {inv.invoice_date or 'Tanggal tidak diketahui'}\n"
                    f"🏢 {inv.shop_name}\n"
                    f"💰 Rp {inv.total_amount:,.2f}\n"
                    "───────────────\n"
                )
            
            return {
                'response_type': 'text',
                'content': response_text,
                'phone': phone
            }
            
        except Exception as e:
            print(f"Error getting recent invoices: {e}")
            return {
                'response_type': 'text',
                'content': f'❌ Error mengambil invoice terbaru: {str(e)}',
                'phone': phone
            }
    
    async def handle_set_limit_command(self, phone: str, args: list) -> Dict[str, Any]:
        """Handle set spending limit command."""
        if not args:
            return {
                'response_type': 'text',
                'content': (
                    "Mohon berikan batas pengeluaran bulanan dalam Rupiah.\n"
                    "Contoh: setlimit 5000000 (untuk Rp 5,000,000)"
                ),
                'phone': phone
            }
        
        try:
            limit = float(args[0])
            if limit <= 0:
                return {
                    'response_type': 'text',
                    'content': "❌ Batas pengeluaran harus lebih dari 0.",
                    'phone': phone
                }
            
            if set_monthly_limit_platform('whatsapp', phone, limit):
                return {
                    'response_type': 'text',
                    'content': (
                        f"✅ Batas pengeluaran bulanan diset ke Rp {limit:,.2f}\n\n"
                        f"Anda akan diberitahu ketika mendekati atau melebihi batas ini."
                    ),
                    'phone': phone
                }
            else:
                return {
                    'response_type': 'text',
                    'content': "❌ Gagal mengatur batas pengeluaran. Silakan coba lagi.",
                    'phone': phone
                }
                
        except ValueError:
            return {
                'response_type': 'text',
                'content': "❌ Mohon berikan angka yang valid untuk batas pengeluaran.",
                'phone': phone
            }
    
    async def handle_check_limit_command(self, phone: str) -> Dict[str, Any]:
        """Handle check spending limit command."""
        monthly_limit = get_monthly_limit_platform('whatsapp', phone)
        if not monthly_limit:
            return {
                'response_type': 'text',
                'content': "Belum ada batas pengeluaran. Gunakan 'setlimit' untuk mengaturnya.",
                'phone': phone
            }
        
        try:
            analysis = analyze_invoices()
            total_spent = analysis['total_spent']
            
            percentage_used = (total_spent / monthly_limit) * 100
            remaining = monthly_limit - total_spent
            
            # Determine status indicator
            if percentage_used >= 100:
                indicator = "🚫"
            elif percentage_used >= 90:
                indicator = "⚠️"
            elif percentage_used >= 75:
                indicator = "⚡"
            else:
                indicator = "✅"
            
            message = (
                f"{indicator} Status Pengeluaran Bulanan\n\n"
                f"Batas Bulanan: Rp {monthly_limit:,.2f}\n"
                f"Total Pengeluaran: Rp {total_spent:,.2f}\n"
                f"Sisa: Rp {remaining:,.2f}\n"
                f"Penggunaan: {percentage_used:.1f}%"
            )
            
            return {
                'response_type': 'text',
                'content': message,
                'phone': phone
            }
            
        except Exception as e:
            return {
                'response_type': 'text',
                'content': f'❌ Error memeriksa batas: {str(e)}',
                'phone': phone
            }
    
    async def handle_upload_instructions(self, phone: str) -> Dict[str, Any]:
        """Handle upload instructions."""
        return {
            'response_type': 'text',
            'content': (
                "📸 Cara Kirim Invoice:\n\n"
                "1. Pastikan foto invoice jelas\n"
                "2. Ambil foto atau scan invoice Anda\n"
                "3. Kirim foto langsung ke chat ini\n"
                "4. Tunggu proses analisis selesai\n\n"
                "Tips:\n"
                "• Pastikan foto terang dan tidak blur\n"
                "• Semua informasi penting harus terbaca\n"
                "• Format yang didukung: JPG, PNG\n\n"
                "Silakan kirim foto invoice Anda sekarang! 📸"
            ),
            'phone': phone
        }
    
    async def handle_unknown_command(self, phone: str, text: str) -> Dict[str, Any]:
        """Handle unknown commands."""
        return {
            'response_type': 'text',
            'content': (
                "Mohon kirim foto invoice atau gunakan perintah berikut:\n"
                "• 'analysis' - Lihat analisis\n"
                "• 'recent' - Invoice terbaru\n"
                "• 'help' - Bantuan lengkap\n\n"
                "Atau langsung kirim foto struk/invoice Anda! 📸"
            ),
            'phone': phone
        }
    
    async def handle_unsupported_message(self, phone: str, message_type: str) -> Dict[str, Any]:
        """Handle unsupported message types."""
        return {
            'response_type': 'text',
            'content': f'Maaf, tipe pesan "{message_type}" belum didukung. Silakan kirim foto invoice atau pesan teks.',
            'phone': phone
        }