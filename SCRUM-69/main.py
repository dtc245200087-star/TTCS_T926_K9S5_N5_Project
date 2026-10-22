
from payment_request import tao_de_nghi_thanh_toan

# Danh sach phieu nghiem thu
ds_phieu = [
    {
        "ma_phieu": "NT001",
        "hang_muc": "Thi cong mong",
        "khoi_luong": 10,
        "don_gia": 1500000,
        "ngay_nghiem_thu": "2026-10-20",
        "trang_thai": "DA_DUYET"
    },
    {
        "ma_phieu": "NT002",
        "hang_muc": "Xay tuong",
        "khoi_luong": 20,
        "don_gia": 350000,
        "ngay_nghiem_thu": "2026-10-21",
        "trang_thai": "DA_DUYET"
    },
    {
        "ma_phieu": "NT003",
        "hang_muc": "Lap dat dien",
        "khoi_luong": 5,
        "don_gia": 2000000,
        "ngay_nghiem_thu": "2026-10-22",
        "trang_thai": "CHUA_DUYET"
    }
]

ket_qua = tao_de_nghi_thanh_toan(
    ds_phieu,
    "2026-10-01",
    "2026-10-31"
)

print("======================================")
print("DE NGHI THANH TOAN TU PHIEU NGHIEM THU")
print("======================================")

for dong in ket_qua["chi_tiet"]:
    print("\nMa phieu:", dong["ma_phieu"])
    print("Hang muc:", dong["hang_muc"])
    print("Khoi luong:", dong["khoi_luong"])
    print("Don gia:", f'{dong["don_gia"]:,.0f}')
    print("Thanh tien:", f'{dong["thanh_tien"]:,.0f}', "VND")

print("\n======================================")
print("So hang muc:", ket_qua["so_hang_muc"])
print("TONG TIEN:", f'{ket_qua["tong_tien"]:,.0f}', "VND")
