import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": _("Ngày"), "fieldname": "ngay", "fieldtype": "Date", "width": 120},
        {"label": _("Số đơn"), "fieldname": "so_don", "fieldtype": "Int", "width": 100},
        {"label": _("Tổng thành tiền"), "fieldname": "tong_thanh_tien", "fieldtype": "Currency", "width": 180},
    ]
    return columns, get_data(filters)


def get_data(filters):
    # Chỉ tính đơn Đã giao, gom theo ngày tạo đơn
    conditions = ["trang_thai = %(trang_thai)s"]
    values = {"trang_thai": "Đã giao"}

    if filters.get("from_date"):
        conditions.append("DATE(creation) >= %(from_date)s")
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions.append("DATE(creation) <= %(to_date)s")
        values["to_date"] = filters["to_date"]

    return frappe.db.sql(
        f"""
        SELECT
            DATE(creation) AS ngay,
            COUNT(name) AS so_don,
            SUM(thanh_tien) AS tong_thanh_tien
        FROM `tabDon Hang`
        WHERE {" AND ".join(conditions)}
        GROUP BY DATE(creation)
        ORDER BY ngay
        """,
        values,
        as_dict=True,
    )