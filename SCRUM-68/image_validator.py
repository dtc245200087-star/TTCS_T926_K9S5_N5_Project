
from PIL import Image
from datetime import datetime


def kiem_tra_anh(duong_dan, ngay_nghiem_thu):
    canh_bao = []

    with Image.open(duong_dan) as anh:
        width, height = anh.size
        exif = anh.getexif()

        # 1. Kiểm tra thông tin máy ảnh
        model = exif.get(272)

        if not model:
            canh_bao.append(
                "Anh thieu thong tin may anh"
            )

        # 2. Kiểm tra kích thước ảnh
        kich_thuoc_man_hinh = [
            (1920, 1080),
            (1366, 768),
            (2560, 1440)
        ]

        if (width, height) in kich_thuoc_man_hinh:
            canh_bao.append(
                "Anh co kich thuoc giong man hinh"
            )

        # 3. Kiểm tra ngày chụp
        try:
            exif_chi_tiet = exif.get_ifd(0x8769)
            ngay_chup = exif_chi_tiet.get(36867)
        except (ValueError, TypeError, KeyError):
            ngay_chup = None

        if not ngay_chup:
            canh_bao.append(
                "Anh khong co ngay chup"
            )
        else:
            try:
                ngay = datetime.strptime(
                    ngay_chup, "%Y:%m:%d %H:%M:%S"
                ).date()

                nghiem_thu = datetime.strptime(
                    ngay_nghiem_thu, "%Y-%m-%d"
                ).date()

                if abs((nghiem_thu - ngay).days) > 7:
                    canh_bao.append(
                        "Ngay chup cach ngay nghiem thu qua 7 ngay"
                    )
            except (ValueError, TypeError):
                canh_bao.append(
                    "Ngay chup khong hop le"
                )

    return {
        "trang_thai": (
            "CANH_BAO" if canh_bao
            else "KHONG_CO_CANH_BAO"
        ),
        "danh_sach_canh_bao": canh_bao
    }
