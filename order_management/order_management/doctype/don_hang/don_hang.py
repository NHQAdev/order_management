import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

MOI = "Mới"
DA_GIAO = "Đã giao"
HUY = "Hủy"

# Trạng thái cũ -> các trạng thái được phép lưu tiếp.
# Tập rỗng nghĩa là đơn đã chốt: không sửa, không đổi trạng thái.
CHUYEN_TRANG_THAI_HOP_LE = {
    MOI: {MOI, DA_GIAO, HUY},
    DA_GIAO: set(),
    HUY: set(),
}


class DonHang(Document):
    def validate(self):
        # Kiểm tra trạng thái trước để đơn đã chốt bị chặn ngay
        self.kiem_tra_trang_thai()
        self.kiem_tra_so_luong_don_gia()
        self.tinh_thanh_tien()

    def kiem_tra_trang_thai(self):
        if self.is_new():
            if self.trang_thai != MOI:
                frappe.throw(_("Đơn mới tạo phải ở trạng thái {0}").format(MOI))
            return

        truoc = self.get_doc_before_save()
        if not truoc:
            return

        duoc_phep = CHUYEN_TRANG_THAI_HOP_LE.get(truoc.trang_thai, set())
        if not duoc_phep:
            frappe.throw(
                _("Đơn {0} đã ở trạng thái {1}, không thể sửa hay đổi trạng thái").format(
                    self.name, truoc.trang_thai
                )
            )
        if self.trang_thai not in duoc_phep:
            frappe.throw(
                _("Không thể chuyển từ {0} sang {1}").format(truoc.trang_thai, self.trang_thai)
            )

    def kiem_tra_so_luong_don_gia(self):
        if flt(self.so_luong) <= 0:
            frappe.throw(_("Số lượng phải lớn hơn 0"))
        if flt(self.don_gia) <= 0:
            frappe.throw(_("Đơn giá phải lớn hơn 0"))

    def tinh_thanh_tien(self):
        # Server luôn tự tính, bỏ qua mọi giá trị client gửi lên
        self.thanh_tien = flt(
            flt(self.so_luong) * flt(self.don_gia), self.precision("thanh_tien")
        )

    def on_trash(self):
        if self.trang_thai in (DA_GIAO, HUY):
            frappe.throw(_("Không thể xóa đơn đã {0}").format(self.trang_thai.lower()))