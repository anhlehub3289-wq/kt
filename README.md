# Hệ Thống Phát Hiện Giao Dịch Bất Thường (Banking Anomaly Detection Dashboard)

Ứng dụng web được xây dựng bằng **Streamlit** giúp phân tích dữ liệu giao dịch ngân hàng và tự động phát hiện các giao dịch bất thường (outliers) dựa trên thuật toán học máy **Isolation Forest**.

## 🌟 Tính năng chính
- **Tải tệp linh hoạt**: Ứng dụng tự động chạy trên file mẫu mặc định `transactions_Q1_demo.csv` khi khởi chạy, và cho phép người dùng tự tải tệp CSV của mình để phân tích.
- **Biểu đồ trực quan tương tác**: Vẽ đồ thị phân bố số lượng giao dịch theo giờ và biểu đồ phân phối số tiền giao dịch bằng thư viện Plotly.
- **Mô hình AI Isolation Forest**: Điều chỉnh trực tiếp tham số `contamination` (tỷ lệ nhiễm bẩn) và `n_estimators` (số cây quyết định) từ giao diện để tối ưu hóa kết quả lọc bất thường.
- **Phân cấp rủi ro (4 Cấp độ)**: Phân nhóm 1% giao dịch bất thường nhất thành 4 cấp độ: Khẩn cấp, Cao, Trung bình, Thấp dựa trên phân vị điểm số rủi ro.
- **Xuất báo cáo**: Cho phép tải tệp báo cáo Excel (`.xlsx`) hoặc CSV tương ứng cho cấp độ rủi ro đang lựa chọn.

---

## 💻 Hướng dẫn chạy trên máy tính cá nhân (Local)

### 1. Chuẩn bị môi trường Python
Yêu cầu máy tính của bạn đã cài đặt Python (phiên bản >= 3.8). Nên tạo một môi trường ảo (virtual environment) trước khi cài đặt:

```bash
# Tạo môi trường ảo (Ví dụ trên Windows)
python -m venv venv

# Kích hoạt môi trường ảo
venv\Scripts\activate
```

### 2. Cài đặt các thư viện cần thiết
Chạy lệnh sau để cài đặt toàn bộ các thư viện có trong tệp `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng Streamlit
Khởi chạy ứng dụng Web cục bộ bằng lệnh:

```bash
streamlit run app.py
```
Sau khi chạy lệnh, trình duyệt web sẽ tự động mở trang dashboard tại địa chỉ `http://localhost:8501`.

---

## 🚀 Hướng dẫn tải lên GitHub và Deploy lên Streamlit Cloud

### 1. Đưa dự án lên GitHub
1. Khởi tạo Git trong thư mục chứa dự án:
   ```bash
   git init
   ```
2. Thêm file `.gitignore` để bỏ qua thư mục môi trường ảo (nếu bạn tạo venv trong thư mục dự án):
   Tạo tệp `.gitignore` và ghi nội dung:
   ```text
   venv/
   __pycache__/
   .streamlit/
   ```
3. Commit và đẩy mã nguồn lên một repository mới trên GitHub của bạn:
   ```bash
   git add .
   git commit -m "Initial commit for Streamlit Banking Anomaly app"
   git branch -M main
   git remote add origin <URL_REPO_GITHUB_CỦA_BẠN>
   git push -u origin main
   ```

### 2. Deploy lên Streamlit Cloud (Miễn phí)
1. Truy cập vào trang web [Streamlit Community Cloud](https://share.streamlit.io/) và đăng nhập bằng tài khoản GitHub của bạn.
2. Nhấn vào nút **"New app"** ở góc trên bên phải.
3. Cấu hình các thông tin ứng dụng:
   - **Repository**: Chọn repository GitHub bạn vừa tạo ở trên.
   - **Branch**: Chọn `main` (hoặc nhánh chứa code của bạn).
   - **Main file path**: Nhập `app.py` (file chứa mã nguồn chạy Streamlit).
4. Nhấn nút **"Deploy!"**. 
5. Streamlit Cloud sẽ tự động tải các gói phụ thuộc từ tệp `requirements.txt` và xây dựng ứng dụng web. Sau vài phút, ứng dụng của bạn sẽ hoạt động trực tuyến với một đường link chia sẻ được.
