import pandas as pd
import numpy as np

def generate_sebaran_jalur_merah():
    np.random.seed(2026)  # Random seed agar sebaran presisi & konsisten
    
    # Rincian 200 bibit pohon
    bibit_dict = {
        'Salam': 40,
        'Jambu Biji': 20,
        'Beringin': 60,
        'Gayam': 20,
        'Trembesi': 60
    }
    
    # Lintasan Waypoints Jalur Baru (Khusus Mengikuti Lingkaran Merah)
    jalur_merah_track = [
        (-7.216562, 109.945841),  # Pos 1
        (-7.214831, 109.944603),  # Gapura Pandan Wangi
        (-7.212785, 109.943239),  # Pertigaan belokan
        
        # KORIDOR JALUR SETAPAK PUTUS-PUTUS (LINGKARAN MERAH)
        (-7.212500, 109.943800),
        (-7.212620, 109.944900),
        (-7.212750, 109.945900),
        (-7.212820, 109.946700),  # Ujung Timur Jalur Setapak
        (-7.212183, 109.940699),  # Bukit Cendani
        
        (-7.210354, 109.940953)   # Pos 3
    ]
    
    data = []
    count = 1
    
    for jenis, jumlah in bibit_dict.items():
        for _ in range(jumlah):
            # Memilih segmen jalur acak
            idx = np.random.randint(0, len(jalur_merah_track) - 1)
            p1 = jalur_merah_track[idx]
            p2 = jalur_merah_track[idx + 1]
            
            # Interpolasi titik sepanjang lintasan setapak
            t = np.random.uniform(0.05, 0.95)
            base_lat = p1[0] + t * (p2[0] - p1[0])
            base_lon = p1[1] + t * (p2[1] - p1[1])
            
            # Offset pergeseran aman (5-15 meter di kanan-kiri jalur setapak)
            offset_lat = np.random.uniform(-0.00012, 0.00012)
            offset_lon = np.random.uniform(-0.00012, 0.00012)
            
            lat = round(base_lat + offset_lat, 6)
            lon = round(base_lon + offset_lon, 6)
            
            data.append({
                'ID_Pohon': f'PHN-{count:03d}',
                'Jenis_Pohon': jenis,
                'Latitude': lat,
                'Longitude': lon
            })
            count += 1
            
    df = pd.DataFrame(data)
    df.to_csv("pohon_data.csv", index=False)
    print(f"✅ Berhasil mengalihkan {len(df)} titik penanaman ke area Jalur Setapak (Lingkaran Merah)!")

if __name__ == '__main__':
    generate_sebaran_jalur_merah()