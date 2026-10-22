
import unittest
from decimal import Decimal

from payment_request import tao_de_nghi_thanh_toan


def tao_phieu(
    ma="NT001",
    trang_thai="DA_DUYET",
    ngay="2026-10-20",
    khoi_luong=10,
    don_gia=1500000
):
    return {
        "ma_phieu": ma,
        "hang_muc": "Thi cong mong",
        "khoi_luong": khoi_luong,
        "don_gia": don_gia,
        "ngay_nghiem_thu": ngay,
        "trang_thai": trang_thai
    }


class TestPaymentRequest(unittest.TestCase):

    def setUp(self):
        self.bat_dau = "2026-10-01"
        self.ket_thuc = "2026-10-31"

    def tinh_tien(self, ds):
        return tao_de_nghi_thanh_toan(
            ds, self.bat_dau, self.ket_thuc
        )

    # TC01: Hai phieu da duyet
    def test_01_tong_tien(self):
        ds = [
            tao_phieu(),
            tao_phieu(
                ma="NT002",
                khoi_luong=20,
                don_gia=350000
            )
        ]
        kq = self.tinh_tien(ds)

        self.assertEqual(
            kq["tong_tien"], Decimal("22000000")
        )
        self.assertEqual(kq["so_hang_muc"], 2)

    # TC02: Khong tinh phieu chua duyet
    def test_02_chua_duyet(self):
        ds = [
            tao_phieu(trang_thai="CHUA_DUYET")
        ]
        kq = self.tinh_tien(ds)

        self.assertEqual(
            kq["tong_tien"], Decimal("0")
        )
        self.assertEqual(kq["so_hang_muc"], 0)

    # TC03: Khong tinh phieu ngoai ky
    def test_03_ngoai_ky(self):
        ds = [
            tao_phieu(ngay="2026-09-15")
        ]
        kq = self.tinh_tien(ds)

        self.assertEqual(
            kq["tong_tien"], Decimal("0")
        )

    # TC04: Khong cho phep khoi luong am
    def test_04_khoi_luong_am(self):
        ds = [
            tao_phieu(khoi_luong=-5)
        ]

        with self.assertRaises(ValueError):
            self.tinh_tien(ds)

    # TC05: Khong cho phep trung ma phieu
    def test_05_trung_ma_phieu(self):
        ds = [
            tao_phieu(ma="NT001"),
            tao_phieu(ma="NT001")
        ]

        with self.assertRaises(ValueError):
            self.tinh_tien(ds)

    # TC06: Danh sach rong
    def test_06_danh_sach_rong(self):
        kq = self.tinh_tien([])

        self.assertEqual(
            kq["tong_tien"], Decimal("0")
        )
        self.assertEqual(kq["so_hang_muc"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
