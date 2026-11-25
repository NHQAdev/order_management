frappe.query_reports["Doanh Thu Theo Ngay"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("Từ ngày"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			fieldname: "to_date",
			label: __("Đến ngày"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
	],
};