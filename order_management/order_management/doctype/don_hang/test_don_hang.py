import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt

from order_management.order_management.report.doanh_thu_theo_ngay.doanh_thu_theo_ngay import (
    execute as chay_bao_cao,
)

KHACH_HANG = "_Test Khach Hang"
MAT_HANG = "_Test Mat Hang"


class TestDonHang(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not frappe.db.exists("Khach Hang", KHACH_HANG):
            frappe.get_doc({"doctype": "Khach Hang", "ten_khach_hang": KHACH_HANG}).insert()
        if not frappe.db.exists("Mat Hang", MAT_HANG):
            frappe.get_doc({"doctype": "Mat Hang", "ten_mat_hang": MAT_HANG}).insert()

    def tao_don(self, so_luong=2, don_gia=1000, **khac):
        return frappe.get_doc(
            {
                "doctype": "Don Hang",
                "khach_hang": KHACH_HANG,
                "mat_hang": MAT_HANG,
                "so_luong": so_luong,
                "don_gia": don_gia,
                **khac,
            }
        ).insert()

    def doi_trang_thai(self, don, trang_thai):
        don.trang_thai = trang_thai
        don.save()
        return don

    # ---- Thành tiền ----
    def test_server_tu_tinh_thanh_tien(self):
        don = self.tao_don(so_luong=3, don_gia=1500)
        self.assertEqual(don.thanh_tien, 4500)

    def test_bo_qua_thanh_tien_client_gui_len(self):
        don = self.tao_don(so_luong=2, don_gia=1000, thanh_tien=1)
        self.assertEqual(don.thanh_tien, 2000)

    # ---- Số lượng, đơn giá ----
    def test_so_luong_phai_lon_hon_0(self):
        for so_luong in (0, -1):
            with self.assertRaises(frappe.ValidationError):
                self.tao_don(so_luong=so_luong)

    def test_don_gia_phai_lon_hon_0(self):
        for don_gia in (0, -500):
            with self.assertRaises(frappe.ValidationError):
                self.tao_don(don_gia=don_gia)

    # ---- Trạng thái ----
    def test_don_moi_tao_phai_o_trang_thai_moi(self):
        with self.assertRaises(frappe.ValidationError):
            self.tao_don(trang_thai="Đã giao")

    def test_tu_moi_chuyen_duoc_sang_da_giao_va_huy(self):
        self.assertEqual(self.doi_trang_thai(self.tao_don(), "Đã giao").trang_thai, "Đã giao")
        self.assertEqual(self.doi_trang_thai(self.tao_don(), "Hủy").trang_thai, "Hủy")

    def test_khong_sua_duoc_don_da_giao(self):
        don = self.doi_trang_thai(self.tao_don(), "Đã giao")
        don.so_luong = 10
        with self.assertRaises(frappe.ValidationError):
            don.save()

    def test_khong_doi_trang_thai_don_da_huy(self):
        for trang_thai_moi in ("Mới", "Đã giao"):
            don = self.doi_trang_thai(self.tao_don(), "Hủy")
            don.trang_thai = trang_thai_moi
            with self.assertRaises(frappe.ValidationError):
                don.save()

    def test_khong_xoa_duoc_don_da_giao(self):
        don = self.doi_trang_thai(self.tao_don(), "Đã giao")
        with self.assertRaises(frappe.ValidationError):
            frappe.delete_doc("Don Hang", don.name)

    # ---- Báo cáo ----
    def test_bao_cao_chi_tinh_don_da_giao_theo_ngay_tao(self):
        # Dùng ngày rất cũ để không lẫn với dữ liệu đang có trên site
        ngay_1, ngay_2 = "2000-01-01", "2000-01-02"
        cac_don = [
            (self.tao_don(2, 1000), "Đã giao", f"{ngay_1} 08:00:00"),
            (self.tao_don(1, 500), "Đã giao", f"{ngay_1} 23:59:00"),
            (self.tao_don(3, 1000), "Đã giao", f"{ngay_2} 10:00:00"),
            (self.tao_don(5, 1000), "Hủy", f"{ngay_1} 09:00:00"),  # không tính
            (self.tao_don(7, 1000), "Mới", f"{ngay_2} 09:00:00"),  # không tính
        ]
        for don, trang_thai, ngay_tao in cac_don:
            if trang_thai != "Mới":
                self.doi_trang_thai(don, trang_thai)
            frappe.db.set_value("Don Hang", don.name, "creation", ngay_tao, update_modified=False)

        _, data = chay_bao_cao({"from_date": ngay_1, "to_date": ngay_2})
        ket_qua = {str(dong.ngay): (dong.so_don, flt(dong.tong_thanh_tien)) for dong in data}

        self.assertEqual(ket_qua, {ngay_1: (2, 2500), ngay_2: (1, 3000)})