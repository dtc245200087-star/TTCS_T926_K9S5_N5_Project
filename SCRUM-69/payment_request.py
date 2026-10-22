
from decimal import Decimal, InvalidOperation


def tao_de_nghi_thanh_toan(ds_phieu, ky_bat_dau, ky_ket_thuc):
    chi_tiet = []
    tong_tien = Decimal("0")
    ma_phieu_da_xu_ly = set()

    for phieu in ds_phieu:

        # Chỉ lấy phiếu đã được duyệt
        if phieu["trang_thai"] != "DA_DUYET":
            continue

        # Chỉ lấy phiếu thuộc kỳ thanh toán
        ngay = phieu["ngay_nghiem_thu"]

        if not (ky_bat_dau <= ngay <= ky_ket_thuc):
            continue

        # Không tính trùng mã phiếu
        ma_phieu = phieu["ma_phieu"]

        if ma_phieu in ma_phieu_da_xu_ly:
            raise ValueError("Trung ma phieu: " + ma_phieu)

        ma_phieu_da_xu_ly.add(ma_phieu)

        # Tính tiền
        try:
            khoi_luong = Decimal(str(phieu["khoi_luong"]))
            don_gia = Decimal(str(phieu["don_gia"]))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Du lieu so khong hop le")

        if not khoi_luong.is_finite() or not don_gia.is_finite():
            raise ValueError("Gia tri khong hop le")

        if khoi_luong < 0 or don_gia < 0:
            raise ValueError("Khoi luong va don gia phai >= 0")

        thanh_tien = khoi_luong * don_gia

        chi_tiet.append({
            "ma_phieu": ma_phieu,
            "hang_muc": phieu["hang_muc"],
            "khoi_luong": khoi_luong,
            "don_gia": don_gia,
            "thanh_tien": thanh_tien
        })

        tong_tien += thanh_tien

    return {
        "chi_tiet": chi_tiet,
        "tong_tien": tong_tien,
        "so_hang_muc": len(chi_tiet)
    }
