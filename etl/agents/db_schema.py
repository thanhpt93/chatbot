"""
Database Schema & Relationship Registry for Retrieval & QA Agent.
Provides table structures, column mappings, and relationship guides for safe Text-to-SQL.
"""

SCHEMA_SUMMARY = """
CÁC BẢNG DỮ LIỆU CHÍNH TRONG HỆ THỐNG POSTGRESQL (inf_nffice):

1. user_profiles (Hồ sơ chi tiết nhân viên):
   - user_id (int, khóa ngoại sang users.id)
   - display_name (varchar, Họ và tên nhân viên - ví dụ 'Đặng Thị Huyền Trang', 'Hoàng Việt Nam Ly')
   - employee_number (varchar, Mã nhân viên - ví dụ 'INF2408001')
   - position (varchar, Vị trí công việc - ví dụ 'Data Engineer', 'Developer', 'Tester')
   - duty (varchar, Chức danh - ví dụ 'Staff', 'Leader', 'Director')
   - grade (varchar, Cấp bậc - ví dụ 'Junior', 'Senior', 'Pro')
   - department_id (int, khóa ngoại sang departments.id)
   - is_resigned (boolean, true nếu Đã thôi việc/nghỉ việc, false nếu Đang làm việc)
   - joining_date (date, Ngày gia nhập công ty)

2. users (Tài khoản người dùng):
   - id (int, khóa chính)
   - username (varchar, Tên đăng nhập)
   - email (varchar, Email công ty)
   - is_active (boolean, Trạng thái tài khoản hoạt động)
   - is_deleted (boolean, Trạng thái xóa mềm)

3. departments (Cơ cấu phòng ban):
   - id (int, khóa chính)
   - code (varchar, Mã phòng ban)
   - name (varchar, Tên phòng ban - ví dụ 'SW DEVELOPMENT', 'Accounting', 'MC Support')
   - parent_id (int, Phòng ban cha)
   - is_active (boolean, true nếu phòng ban đang hoạt động)

4. approval_requests (Đơn từ đề xuất phê duyệt):
   - id (bigint, khóa chính)
   - code (varchar, Mã phiếu duyệt - ví dụ 'APR-2026-...')
   - title (text, Tiêu đề phiếu - ví dụ 'Xin nghỉ phép', 'Làm thêm giờ', 'Tạm ứng')
   - status (varchar, Trạng thái: 'COMPLETED' (đã duyệt), 'SUBMITTED' (đang chờ duyệt), 'REJECTED' (từ chối), 'DRAFT', 'CANCELLED', 'RETURNED')
   - request_type (varchar, Loại đơn: 'VACATION', 'OVERTIME', 'EXPENSE', 'EXPLANATION', v.v.)
   - created_by_user_id (int, ID nhân viên tạo đơn - LINK với users.id hoặc user_profiles.user_id)
   - total_days (numeric, Số ngày đăng ký nếu là nghỉ phép)
   - start_date, end_date (date, Thời gian nghỉ/áp dụng)
   - created_at (timestamp, Thời điểm tạo đơn)
   - is_deleted (boolean, false nếu đơn còn tồn tại)

5. projects (Dự án công việc):
   - id (int, khóa chính)
   - key (varchar, Mã dự án - ví dụ 'REQ', '42DOT')
   - name (varchar, Tên dự án)
   - status (varchar, Trạng thái dự án: 'new', 'in_progress', 'completed')
   - created_by_user_id (int, Người tạo dự án)
   - members_count (int, Số thành viên dự án)
   - tickets_count (int, Số công việc trong dự án)
   - is_deleted (boolean)

6. tickets (Công việc / Nhiệm vụ):
   - id (int, khóa chính)
   - code (varchar, Mã ticket - ví dụ 'BUGNF-74')
   - title (varchar, Tiêu đề công việc)
   - status (varchar, Trạng thái: 'create', 'in_progress', 'resolved', 'closed')
   - priority (varchar, Độ ưu tiên: 'low', 'medium', 'high', 'urgent')
   - project_id (int, Thuộc dự án nào - projects.id)
   - created_by_user_id (int, Người tạo ticket)
   - is_deleted (boolean)

7. assets (Tài sản thiết bị công ty):
   - id (int, khóa chính)
   - asset_code (varchar, Mã tài sản)
   - name (varchar, Tên thiết bị - ví dụ 'Laptop ThinkPad X1', 'Màn hình Dell 24 inch')
   - serial_number (varchar, Số Serial)
   - status (varchar, 'IN_USE', 'AVAILABLE', 'MAINTENANCE', 'DISPOSED')
   - assigned_user_id (int, Nhân viên đang giữ tài sản - users.id)
   - department_id (int, Phòng ban quản lý tài sản - departments.id)
   - is_deleted (boolean)

8. asset_assignments (Lịch sử bàn giao / cấp phát tài sản):
   - id (bigint)
   - asset_id (int, assets.id)
   - to_user_id (int, Nhân viên nhận bàn giao - users.id)
   - to_department_id (int)
   - assigned_date (date, Ngày bàn giao)
   - ticket_code (varchar, Mã biên bản bàn giao)
   - status (varchar, 'COMPLETED')

9. user_leave_year_balances (Số dư ngày phép năm):
   - user_id (int, users.id)
   - year (int, Năm tính phép - ví dụ 2026)
   - remaining_days (numeric, Số ngày phép còn lại)
   - opening_days (numeric, Ngày phép đầu kỳ)
   - carryover_days (numeric, Ngày phép chuyển từ năm trước)
   - note (text, Ghi chú điều chỉnh)

10. regulations (Quy định & Quy chế công ty):
   - id (int, khóa chính)
   - title (varchar, Tiêu đề quy chế/quy định)
   - content (text, Nội dung văn bản quy chế)
   - category (varchar, Phân loại quy chế)
   - version (varchar, Phiên bản)
   - is_deleted (boolean)

11. schedule_events (Lịch họp / Sự kiện):
   - id (int)
   - title (varchar, Tên cuộc họp/sự kiện)
   - description (text, Nội dung cuộc họp)
   - event_date (date, Ngày diễn ra)
   - start_time, end_time (time)
   - user_id (int, Người chủ trì cuộc họp)
   - location (varchar, Địa điểm hoặc phòng họp)
   - is_deleted (boolean)
"""
