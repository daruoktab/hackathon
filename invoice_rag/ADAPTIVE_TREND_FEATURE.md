# 📊 Fitur Adaptive Time Granularity

## 🎯 Tujuan
Membuat dashboard lebih adaptif dengan otomatis memilih antara tampilan **Daily Trend** atau **Weekly Trend** berdasarkan rentang data yang tersedia, sehingga visualisasi selalu menampilkan informasi yang paling relevan dan informatif.

## 🔄 Cara Kerja

### 1. **Deteksi Otomatis Granularitas**
Sistem mengevaluasi data invoice dan memutuskan granularitas waktu terbaik:

- **Daily Trend** dipilih jika:
  - Rentang data < 14 hari, ATAU
  - Jumlah minggu unik < 2
  
- **Weekly Trend** dipilih jika:
  - Rentang data ≥ 14 hari, DAN
  - Jumlah minggu unik ≥ 2

### 2. **Fungsi Baru di `src/analysis.py`**

#### `determine_time_granularity(weeks_back=4)`
Menentukan granularitas waktu yang tepat berdasarkan data.

**Return:**
```python
{
    'granularity': 'daily' atau 'weekly',
    'reason': 'short_range', 'sufficient_range', 'no_data', dll,
    'data_range_days': jumlah hari,
    'sufficient_for_trend': True/False
}
```

#### `calculate_daily_totals(weeks_back=4)`
Menghitung total pengeluaran per hari.

**Return:**
```python
{
    'total_days': total hari dalam periode,
    'days_with_data': hari dengan transaksi,
    'daily_average': rata-rata harian,
    'total_spent': total pengeluaran,
    'transaction_count': jumlah transaksi,
    'daily_breakdown': {
        'YYYY-MM-DD': {
            'total': jumlah,
            'count': transaksi,
            'date': datetime object,
            'label': 'DD/MM'
        }
    }
}
```

#### `analyze_daily_trends(weeks_back=4)`
Menganalisis tren pengeluaran harian (mirip dengan `analyze_spending_trends` untuk mingguan).

**Return:**
```python
{
    'trend': 'increasing', 'decreasing', 'stable', atau 'insufficient_data',
    'trend_percentage': persentase perubahan,
    'granularity': 'daily',
    'daily_data': data terurut,
    'message': deskripsi tren
}
```

### 3. **Perubahan di `telegram_bot/visualizations.py`**

#### Import Baru
```python
from src.analysis import (
    analyze_invoices,
    calculate_weekly_averages,
    calculate_daily_totals,          # BARU
    analyze_spending_trends,
    analyze_daily_trends,            # BARU
    analyze_transaction_types,
    parse_invoice_date,
    determine_time_granularity       # BARU
)
```

#### Logic Adaptif di `create_comprehensive_dashboard()`
```python
# Deteksi granularitas
granularity_info = determine_time_granularity(weeks_back=weeks_back)

# Ambil data sesuai granularitas
if granularity_info['granularity'] == 'daily':
    time_data = calculate_daily_totals(weeks_back=weeks_back)
    trends = analyze_daily_trends(weeks_back=weeks_back)
else:
    time_data = calculate_weekly_averages(weeks_back=weeks_back)
    trends = analyze_spending_trends(weeks_back=weeks_back)
```

#### Rendering Adaptif
- Grafik tren otomatis menyesuaikan:
  - **Judul**: "Daily Spending Trend" vs "Weekly Spending Trend"
  - **Label X-axis**: Tanggal (DD/MM) vs Minggu (W1, W2, dst)
  - **Data points**: Harian vs mingguan
  
- Badge tren tetap ditampilkan dengan warna sesuai arah:
  - 🔴 Merah: Increasing
  - 🟢 Hijau: Decreasing
  - 🟡 Kuning: Stable

- Insights footer menyesuaikan:
  - Daily mode: Hanya menampilkan daily average
  - Weekly mode: Menampilkan weekly + daily average

## 📈 Skenario Penggunaan

### Skenario 1: Data Baru (< 2 minggu)
```
Input: 5 invoice dalam 10 hari terakhir
Output: Daily Trend Chart
- Menampilkan bar/line per hari
- Lebih detail untuk rentang pendek
- Memudahkan tracking harian
```

### Skenario 2: Data Cukup (≥ 2 minggu)
```
Input: 20 invoice dalam 8 minggu terakhir
Output: Weekly Trend Chart
- Menampilkan line per minggu
- Lebih jelas untuk melihat pola jangka panjang
- Mengurangi noise dari fluktuasi harian
```

### Skenario 3: Data Sangat Sedikit
```
Input: 1-2 invoice saja
Output: "More data needed" message
- Tidak memaksakan visualisasi
- Memberikan instruksi jelas untuk upload lebih banyak
```

## ✅ Keuntungan

1. **Otomatis & Cerdas**: Tidak perlu pengaturan manual, sistem memutuskan sendiri
2. **Selalu Informatif**: Menampilkan level detail yang tepat sesuai data
3. **Konsisten**: Logic terpusat, tidak tersebar di banyak tempat
4. **Scalable**: Mudah ditambah level lain (bulanan, kuartalan) di masa depan
5. **User-friendly**: Pengguna tidak perlu tahu complexity di belakang layar

## 🧪 Testing

Jalankan test script untuk melihat bagaimana sistem beradaptasi:

```bash
cd d:\Codings\hackathon\invoice_rag
python test_adaptive_trend.py
```

Script ini akan menunjukkan:
- Granularitas yang dipilih untuk berbagai periode
- Alasan pemilihan
- Data yang dihasilkan untuk setiap mode

## 🔮 Pengembangan Masa Depan

Fitur ini membuka jalan untuk:
- **Monthly aggregation**: Untuk data > 3 bulan
- **Quarterly/Yearly views**: Untuk analisis jangka panjang
- **Custom time ranges**: User bisa pilih sendiri
- **Smooth transitions**: Animasi saat switch granularity
- **Comparison views**: Daily vs Weekly side-by-side

## 📝 Catatan Teknis

- Semua fungsi backward-compatible dengan kode lama
- Tidak ada breaking changes pada API existing
- Performance optimal dengan caching di level database query
- Error handling untuk edge cases (data kosong, tanggal invalid, dll)

---

**Status**: ✅ Implemented & Ready to Use  
**Version**: 1.0  
**Date**: October 22, 2025
