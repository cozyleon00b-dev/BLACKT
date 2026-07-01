# BLACKT TEAM SYSTEM — PREMIUM EDITION

## DESKRIPSI
Sistem manajemen tim berbasis web + Roblox dengan 3 role:
- **MEMBER** — Limit 5 per minggu, auto reset
- **STAFF** — Limit 10 per 2 minggu, bisa monitor aktivitas Member
- **DEVELOPER** — Unlimited, hapus akses user online, post announcement, lihat semua logs

## FITUR
- Background hitam, text neon biru
- Tanpa emoji, tanpa kategori/komentar
- Full logic real-time
- Auto reset usage per role
- Logs & announcement terintegrasi

## INSTALLASI BACKEND
1. Install Python 3.8+
2. Install dependencies: `pip install flask`
3. Jalankan: `python server.py`
4. Buka browser: `http://localhost:5000`

## INTEGRASI ROBLOX
1. Copy script `RobloxScript.lua` ke **StarterGui**
2. Pastikan `HttpService` diaktifkan di Roblox Studio
3. Ganti `BASE_URL` dengan IP server lo (jangan localhost di Roblox)
4. Player akan otomatis terdaftar sebagai **MEMBER** saat join

## ENDPOINT API
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| GET | `/api/data` | Ambil semua data (users, logs, announcements) |
| POST | `/api/user` | Tambah user (butuh role) |
| DELETE | `/api/user/<username>` | Hapus user (hanya Developer) |
| POST | `/api/announcement` | Post announcement (hanya Developer) |

## ATURAN SISTEM
- **MEMBER**: Max 5, reset tiap 7 hari
- **STAFF**: Max 10, reset tiap 14 hari, bisa lihat logs
- **DEVELOPER**: Unlimited, akses penuh

## PERINGATAN
- Sistem ini untuk edukasi & testing
- Jangan gunakan untuk aktivitas ilegal