
from image_validator import kiem_tra_anh

print("================================")
print("HE THONG KIEM TRA ANH NGHIEM THU")
print("================================")

ket_qua = kiem_tra_anh(
    "anh_nghiem_thu.jpg",
    "2026-10-23"
)

print("\nKET QUA KIEM TRA:")
print("Trang thai:", ket_qua["trang_thai"])

if ket_qua["danh_sach_canh_bao"]:
    print("\nDanh sach canh bao:")

    for i, canh_bao in enumerate(
        ket_qua["danh_sach_canh_bao"], 1
    ):
        print(f"{i}. {canh_bao}")
else:
    print("Khong phat hien dau hieu bat thuong")
