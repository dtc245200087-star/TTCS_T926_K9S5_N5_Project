
from PIL import Image
from datetime import datetime
from image_validator import kiem_tra_anh


def tao_anh_test(ten_file, kich_thuoc, model=None, ngay_chup=None):
    anh = Image.new("RGB", kich_thuoc, "white")
    exif = Image.Exif()

    if model:
        exif[272] = model

    if ngay_chup:
        exif_ifd = exif.get_ifd(0x8769)
        exif_ifd[36867] = ngay_chup

    anh.save(ten_file, "JPEG", exif=exif)


def chay_test(ten, file, ngay, ket_qua_mong_doi):
    ket_qua = kiem_tra_anh(file, ngay)
    thuc_te = ket_qua["trang_thai"]

    print(f"\n{ten}")
    print("Trang thai:", thuc_te)
    print("Canh bao:", ket_qua["danh_sach_canh_bao"])

    assert thuc_te == ket_qua_mong_doi, (
        f"That bai: mong doi {ket_qua_mong_doi}, "
        f"nhan duoc {thuc_te}"
    )
    print("PASS")


# TC01: Ảnh có EXIF và ngày chụp hợp lệ
tao_anh_test(
    "test_hop_le.jpg",
    (1600, 1200),
    "Canon",
    "2026:10:22 10:00:00"
)

chay_test(
    "TC01 - Anh hop le",
    "test_hop_le.jpg",
    "2026-10-23",
    "KHONG_CO_CANH_BAO"
)


# TC02: Ảnh thiếu EXIF
tao_anh_test(
    "test_thieu_exif.jpg",
    (1600, 1200)
)

chay_test(
    "TC02 - Anh thieu EXIF",
    "test_thieu_exif.jpg",
    "2026-10-23",
    "CANH_BAO"
)


# TC03: Ảnh có kích thước màn hình
tao_anh_test(
    "test_man_hinh.jpg",
    (1920, 1080),
    "Canon",
    "2026:10:23 10:00:00"
)

chay_test(
    "TC03 - Kich thuoc man hinh",
    "test_man_hinh.jpg",
    "2026-10-23",
    "CANH_BAO"
)


# TC04: Ảnh có ngày chụp quá xa
tao_anh_test(
    "test_sai_ngay.jpg",
    (1600, 1200),
    "Canon",
    "2026:09:01 10:00:00"
)

chay_test(
    "TC04 - Ngay chup qua xa",
    "test_sai_ngay.jpg",
    "2026-10-23",
    "CANH_BAO"
)

print("\nDA HOAN THANH 4 TEST CASE!")
