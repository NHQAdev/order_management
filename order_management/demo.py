import frappe
from frappe.utils import add_days, now_datetime


def tao_du_lieu_mau():
    """Tạo khách hàng, mặt hàng và vài đơn hàng mẫu để xem báo cáo."""
    for ten in ["Quoc Kiet", "Minh Anh", "Thanh Hai"]:
        if not frappe.db.exists("Khach Hang", ten):
            frappe.get_doc({"doctype": "Khach Hang", "ten_khach_hang": ten}).insert()

    for ten in ["Ao Thun", "Quan Jean", "Non Luoi Trai"]:
        if not frappe.db.exists("Mat Hang", ten):
            frappe.get_doc({"doctype": "Mat Hang", "ten_mat_hang": ten}).insert()

    don_1 = _tao_don("Quoc Kiet", "Ao Thun", 2, 150000, "Đã giao")
    _tao_don("Minh Anh", "Quan Jean", 1, 450000, "Đã giao")
    _tao_don("Thanh Hai", "Non Luoi Trai", 3, 80000, "Hủy")
    _tao_don("Minh Anh", "Ao Thun", 5, 150000)  # để ở trạng thái Mới

    # Lùi ngày tạo của 1 đơn về hôm qua để báo cáo có 2 dòng (chỉ dùng cho dữ liệu mẫu)
    frappe.db.set_value(
        "Don Hang", don_1.name, "creation", add_days(now_datetime(), -1), update_modified=False
    )

    frappe.db.commit()
    print("Đã tạo dữ liệu mẫu")


def _tao_don(khach_hang, mat_hang, so_luong, don_gia, trang_thai="Mới"):
    # Tạo qua get_doc().insert() để validate() chạy như khi tạo từ giao diện
    don = frappe.get_doc(
        {
            "doctype": "Don Hang",
            "khach_hang": khach_hang,
            "mat_hang": mat_hang,
            "so_luong": so_luong,
            "don_gia": don_gia,
        }
    ).insert()
    if trang_thai != "Mới":
        don.trang_thai = trang_thai
        don.save()
    return don