import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import io

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Hệ thống Phát hiện Giao dịch Bất thường",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Thiết lập giao diện tùy chỉnh bằng CSS
st.markdown("""
    <style>
        .reportview-container {
            background: #f0f2f6;
        }
        .main-header {
            font-size: 2.2rem;
            color: #1E3A8A;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-align: center;
        }
        .sub-header {
            font-size: 1.1rem;
            color: #4B5563;
            margin-bottom: 2rem;
            text-align: center;
        }
        .metric-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border-left: 5px solid #2563EB;
            text-align: center;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1F2937;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #6B7280;
            text-transform: uppercase;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 1.1rem;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------- THANH BÊN (SIDEBAR) -----------------
st.sidebar.image("https://img.icons8.com/clouds/150/000000/bank.png", width=120)
st.sidebar.title("Cấu hình & Tải dữ liệu")

# 1. Tải file dữ liệu
uploaded_file = st.sidebar.file_uploader(
    "Tải lên tệp giao dịch (.csv)", 
    type=["csv"],
    help="Hãy tải lên tệp giao dịch có cùng cấu trúc với tệp transactions_Q1_demo.csv"
)

# 2. Cấu hình mô hình Isolation Forest
st.sidebar.subheader("Tham số mô hình AI")
contamination = st.sidebar.slider(
    "Tỷ lệ nhiễm bẩn (Contamination)", 
    min_value=0.001, 
    max_value=0.05, 
    value=0.01, 
    step=0.001,
    help="Tỷ lệ giao dịch bất thường dự kiến trong dữ liệu (Ví dụ: 0.01 = 1%)"
)
n_estimators = st.sidebar.slider(
    "Số lượng cây quyết định (n_estimators)", 
    min_value=50, 
    max_value=500, 
    value=200, 
    step=50,
    help="Số lượng cây ước lượng trong mô hình Isolation Forest"
)
random_state = st.sidebar.number_input(
    "Random State", 
    value=42, 
    step=1,
    help="Giá trị khởi tạo ngẫu nhiên để đảm bảo tính nhất quán của kết quả"
)

# Đọc dữ liệu mặc định hoặc file người dùng tải lên
@st.cache_data
def load_data(file_source):
    try:
        # Nếu là chuỗi, đó là tên file mẫu
        if isinstance(file_source, str):
            df = pd.read_csv(file_source)
        else:
            df = pd.read_csv(file_source)
        
        # Tiền xử lý ngày tháng
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], format='%d/%m/%Y %H:%M', errors='coerce')
        # Điền các giá trị NaT nếu có
        df = df.dropna(subset=['transaction_date'])
        
        # Tạo thêm các cột đặc trưng bổ sung
        df['gio_giao_dich'] = df['transaction_date'].dt.hour
        df['co_nhan_vien'] = df['is_employee'].astype(int)
        return df
    except Exception as e:
        st.error(f"Lỗi khi đọc tệp dữ liệu: {e}")
        return None

# Load dữ liệu đầu vào
if uploaded_file is not None:
    df_raw = load_data(uploaded_file)
    data_info_msg = "📂 Đang sử dụng tệp dữ liệu tải lên từ máy của bạn."
else:
    # Load file mặc định
    default_csv_path = "transactions_Q1_demo.csv"
    df_raw = load_data(default_csv_path)
    data_info_msg = "ℹ️ Đang hiển thị dữ liệu mẫu mặc định (`transactions_Q1_demo.csv`). Hãy tải lên file của bạn ở sidebar để phân tích."

if df_raw is not None:
    df = df_raw.copy()

    # ----------------- TIÊU ĐỀ CHÍNH -----------------
    st.markdown('<div class="main-header">🏦 HỆ THỐNG PHÁT HIỆN GIAO DỊCH BẤT THƯỜNG</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">{data_info_msg}</div>', unsafe_allow_html=True)

    # ----------------- TRAIN MÔ HÌNH ISOLATION FOREST -----------------
    # Lựa chọn 3 biến đặc trưng
    X = df[['amount', 'gio_giao_dich', 'co_nhan_vien']]
    
    # Chuẩn hóa
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Huấn luyện
    iso = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        max_samples="auto",
        random_state=random_state,
        n_jobs=-1
    )
    iso.fit(X_scaled)
    
    # Thêm cột kết quả
    df["anomaly_score"] = iso.decision_function(X_scaled)
    df["is_anomaly"] = iso.predict(X_scaled) == -1

    # Chia các tab tính năng
    tab1, tab2, tab3 = st.tabs(["📊 Tổng Quan Dữ Liệu", "🔍 Phát Hiện Bất Thường", "🚨 Phân Cấp Rủi Ro & Xuất Báo Cáo"])

    # ================= TAB 1: TỔNG QUAN DỮ LIỆU =================
    with tab1:
        st.subheader("Chỉ số thống kê giao dịch")
        
        # Tính toán các chỉ số
        total_txns = len(df)
        total_amount = df['amount'].sum()
        off_hours_txns = df[(df['gio_giao_dich'] < 6) | (df['gio_giao_dich'] > 18)].shape[0]
        emp_txns = df[df['is_employee'] == True].shape[0]

        # Hiển thị Metric Cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Tổng giao dịch</div><div class="metric-value">{total_txns:,}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Tổng tiền (VND)</div><div class="metric-value">{total_amount:,.0f}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Giao dịch ngoài giờ</div><div class="metric-value">{off_hours_txns:,}</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><div class="metric-label">GD từ Nhân viên</div><div class="metric-value">{emp_txns:,}</div></div>', unsafe_allow_html=True)

        st.write("---")
        
        # Biểu đồ giờ giao dịch & phân phối số tiền
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("Phân bố số lượng giao dịch theo giờ")
            hour_counts = df['gio_giao_dich'].value_counts().sort_index().reset_index()
            hour_counts.columns = ['Giờ', 'Số lượng']
            fig_hour = px.bar(
                hour_counts, 
                x='Giờ', 
                y='Số lượng',
                labels={'Giờ': 'Giờ trong ngày', 'Số lượng': 'Số lượng giao dịch'},
                color_discrete_sequence=['#2563EB']
            )
            fig_hour.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1))
            st.plotly_chart(fig_hour, use_container_width=True)
            
        with chart_col2:
            st.subheader("Phân phối số tiền giao dịch")
            # Vẽ biểu đồ Box plot cho amount (Log scale do dải số tiền cực kỳ rộng)
            fig_box = px.box(
                df, 
                y='amount', 
                log_y=True,
                labels={'amount': 'Số tiền giao dịch (Log scale)'},
                color_discrete_sequence=['#10B981']
            )
            st.plotly_chart(fig_box, use_container_width=True)

        # Xem bảng dữ liệu mẫu
        st.subheader("Dữ liệu giao dịch chi tiết (100 dòng đầu tiên)")
        st.dataframe(df.head(100), use_container_width=True)

    # ================= TAB 2: PHÁT HIỆN BẤT THƯỜNG =================
    with tab2:
        st.subheader("Phân tích bất thường bằng thuật toán Isolation Forest")
        
        num_anomalies = df['is_anomaly'].sum()
        anomaly_rate = (num_anomalies / total_txns) * 100
        
        det_col1, det_col2 = st.columns(2)
        with det_col1:
            st.markdown(f'<div class="metric-card" style="border-left-color: #EF4444;"><div class="metric-label">Số giao dịch bất thường phát hiện</div><div class="metric-value">{num_anomalies}</div></div>', unsafe_allow_html=True)
        with det_col2:
            st.markdown(f'<div class="metric-card" style="border-left-color: #F59E0B;"><div class="metric-label">Tỷ lệ bất thường (%)</div><div class="metric-value">{anomaly_rate:.2f}%</div></div>', unsafe_allow_html=True)
            
        st.write("---")
        
        st.subheader("Biểu đồ phân bố các giao dịch bất thường")
        
        # Biểu diễn trực quan bằng Scatter Plot (Giờ vs Số tiền)
        fig_scatter = px.scatter(
            df,
            x='gio_giao_dich',
            y='amount',
            color='is_anomaly',
            color_discrete_map={False: '#3B82F6', True: '#EF4444'},
            labels={
                'gio_giao_dich': 'Giờ thực hiện',
                'amount': 'Số tiền giao dịch (VND)',
                'is_anomaly': 'Bất thường?'
            },
            hover_data=['transaction_id', 'location', 'is_employee'],
            title="Tương quan giữa Giờ giao dịch và Số tiền giao dịch (Đỏ: Bất thường)"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # ================= TAB 3: PHÂN CẤP RỦI RO & XUẤT BÁO CÁO =================
    with tab3:
        st.subheader("Phân chia cấp độ rủi ro của giao dịch bất thường")
        
        # Chỉ làm việc trên tập bất thường
        df_bat_thuong = df[df['is_anomaly'] == True].copy()
        
        if len(df_bat_thuong) > 0:
            # Tính toán phân vị của anomaly_score trên tập bất thường
            scores = df_bat_thuong['anomaly_score']
            q25 = scores.quantile(0.25)
            q50 = scores.quantile(0.50)
            q75 = scores.quantile(0.75)
            
            # Hàm gán cấp độ rủi ro
            def assign_risk_level(score):
                if score < q25:
                    return "Rủi ro khẩn cấp"
                elif score < q50:
                    return "Rủi ro cao"
                elif score < q75:
                    return "Rủi ro trung bình"
                else:
                    return "Rủi ro thấp"
                    
            df_bat_thuong['risk_level'] = df_bat_thuong['anomaly_score'].apply(assign_risk_level)
            
            # Đếm số lượng của từng nhóm
            risk_counts = df_bat_thuong['risk_level'].value_counts()
            
            col_r1, col_r2, col_r3, col_r4 = st.columns(4)
            with col_r1:
                st.markdown(f'<div class="metric-card" style="border-left-color: #7F1D1D;"><div class="metric-label">🚨 Rủi ro khẩn cấp</div><div class="metric-value">{risk_counts.get("Rủi ro khẩn cấp", 0)}</div></div>', unsafe_allow_html=True)
            with col_r2:
                st.markdown(f'<div class="metric-card" style="border-left-color: #DC2626;"><div class="metric-label">⚠️ Rủi ro cao</div><div class="metric-value">{risk_counts.get("Rủi ro cao", 0)}</div></div>', unsafe_allow_html=True)
            with col_r3:
                st.markdown(f'<div class="metric-card" style="border-left-color: #D97706;"><div class="metric-label">🔔 Rủi ro trung bình</div><div class="metric-value">{risk_counts.get("Rủi ro trung bình", 0)}</div></div>', unsafe_allow_html=True)
            with col_r4:
                st.markdown(f'<div class="metric-card" style="border-left-color: #10B981;"><div class="metric-label">💡 Rủi ro thấp</div><div class="metric-value">{risk_counts.get("Rủi ro thấp", 0)}</div></div>', unsafe_allow_html=True)
                
            st.write("---")
            
            # Lựa chọn cấp độ rủi ro muốn hiển thị
            selected_risk = st.selectbox(
                "Chọn cấp độ rủi ro cần xem chi tiết và tải báo cáo:",
                options=["Rủi ro khẩn cấp", "Rủi ro cao", "Rủi ro trung bình", "Rủi ro thấp"],
                index=0
            )
            
            # Lọc dữ liệu theo lựa chọn
            df_selected_risk = df_bat_thuong[df_bat_thuong['risk_level'] == selected_risk]
            
            st.write(f"Hiển thị danh sách: **{selected_risk}** ({len(df_selected_risk)} giao dịch)")
            st.dataframe(df_selected_risk, use_container_width=True)
            
            # Tạo nút tải báo cáo
            # 1. Excel Export
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df_selected_risk.to_excel(writer, index=False, sheet_name=selected_risk)
            excel_data = excel_buffer.getvalue()
            
            # 2. CSV Export
            csv_data = df_selected_risk.to_csv(index=False).encode('utf-8')
            
            # Nút download đặt cạnh nhau
            btn_col1, btn_col2, _ = st.columns([1, 1, 3])
            with btn_col1:
                st.download_button(
                    label=f"📥 Tải Excel ({selected_risk})",
                    data=excel_data,
                    file_name=f"bao_cao_{selected_risk.lower().replace(' ', '_')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            with btn_col2:
                st.download_button(
                    label=f"📥 Tải CSV ({selected_risk})",
                    data=csv_data,
                    file_name=f"bao_cao_{selected_risk.lower().replace(' ', '_')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.info("Không phát hiện giao dịch bất thường nào phù hợp với tham số hiện tại.")
else:
    st.error("Không thể tải dữ liệu lên. Vui lòng kiểm tra định dạng tệp CSV của bạn.")
