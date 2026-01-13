import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ===== CẤU HÌNH TRANG =====
st.set_page_config(
    page_title="Hospital Data Analytics",
    layout="wide",
    page_icon="🏥",
    initial_sidebar_state="expanded"
)

# ===== HÀM LOAD CSS =====
def load_css(file_name):
    """Load CSS từ file và inject vào Streamlit"""
    try:
        with open(file_name, "r") as f:
            css = f"<style>{f.read()}</style>"
            st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown("""
        <style>
        .stApp { font-family: 'Inter', sans-serif; }
        [data-testid="stMetricValue"] { font-size: 1.5rem; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)

# Load CSS
load_css("style.css")

# ===== PHẦN UPLOAD FILE =====
st.sidebar.header("📤 Tải lên dữ liệu")

# Kiểm tra nếu đã có file trong session state
if 'df' not in st.session_state:
    st.session_state.df = None

uploaded_file = st.sidebar.file_uploader(
    "Chọn file CSV", 
    type=['csv'],
    help="Tải lên file unique_data.csv",
    key="file_uploader"
)

# Nút reset dữ liệu
if st.session_state.df is not None:
    if st.sidebar.button("🔄 Reset dữ liệu"):
        st.session_state.df = None
        st.rerun()

# ===== HÀM XỬ LÝ DỮ LIỆU =====
def process_data(df):
    """Xử lý và làm sạch dữ liệu"""
    if df.empty:
        return df
    
    # Chuyển đổi kiểu dữ liệu
    if 'ngay_tiep_nhan' in df.columns:
        df['date_clean'] = pd.to_datetime(df['ngay_tiep_nhan'], errors='coerce')
    
    if 'tongdoanhthu' in df.columns:
        # Loại bỏ ký tự không phải số trước khi chuyển
        df['revenue'] = pd.to_numeric(
            df['tongdoanhthu'].astype(str).str.replace(',', '').str.replace(' ', ''),
            errors='coerce'
        )
    
    return df

# ===== HÀM LOAD DỮ LIỆU =====
@st.cache_data(show_spinner="Đang tải dữ liệu...")
def load_data(uploaded_file):
    """Load dữ liệu từ file upload hoặc file local"""
    
    # Ưu tiên file upload
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.sidebar.success(f"✅ Đã tải lên: {uploaded_file.name}")
            return process_data(df)
        except Exception as e:
            st.sidebar.error(f"Lỗi khi đọc file: {e}")
            return pd.DataFrame()
    
    # Thử đọc file local (chỉ dành cho chạy local)
    try:
        df = pd.read_csv('unique_data.csv')
        st.sidebar.info("📁 Đang dùng file local")
        return process_data(df)
    except FileNotFoundError:
        # Nếu không có file local và không có upload
        if uploaded_file is None:
            st.sidebar.warning("⚠️ Vui lòng tải lên file CSV")
        return pd.DataFrame()
    except Exception as e:
        st.sidebar.error(f"Lỗi khi đọc file local: {e}")
        return pd.DataFrame()

# ===== LOAD DỮ LIỆU =====
df = load_data(uploaded_file)

# Lưu vào session state nếu có dữ liệu
if not df.empty and uploaded_file is not None:
    st.session_state.df = df

# Sử dụng dữ liệu từ session state nếu có
if st.session_state.df is not None and uploaded_file is None:
    df = st.session_state.df

# Kiểm tra nếu có dữ liệu
if df.empty:
    st.title("🏥 Hospital Data Analytics Dashboard")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/2917/2917633.png", width=150)
    
    with col2:
        st.header("Chào mừng đến với Dashboard!")
        st.markdown("""
        ### 📤 Vui lòng tải lên dữ liệu để bắt đầu
        
        1. Sử dụng **sidebar bên trái** để tải lên file CSV
        2. File cần có các cột: `nam`, `thang`, `tongdoanhthu`, `sotiepnhan`, v.v.
        3. Định dạng file: **unique_data.csv**
        
        ### 🎯 Tính năng chính:
        - 📊 Phân tích doanh thu theo thời gian
        - 📈 So sánh nhóm dịch vụ
        - 👥 Phân tích đối tượng khách hàng
        - 🎨 Giao diện hiện đại với Tailwind CSS
        """)
    
    # Hiển thị hướng dẫn định dạng file
    with st.expander("📋 Định dạng file CSV yêu cầu"):
        st.markdown("""
        File CSV cần có ít nhất các cột sau:
        
        | Cột | Kiểu dữ liệu | Mô tả |
        |------|--------------|-------|
        | `nam` | số nguyên | Năm |
        | `thang` | số nguyên | Tháng (1-12) |
        | `tongdoanhthu` | số | Doanh thu (có thể có dấu phẩy) |
        | `sotiepnhan` | số nguyên | Số lượt tiếp nhận |
        | `tennhomdichvu` | text | Tên nhóm dịch vụ |
        | `tendichvu` | text | Tên dịch vụ |
        | `loai_dich_vu` | text | Loại dịch vụ (Nội trú/Ngoại trú) |
        """)
        
        # Hiển thị sample data
        sample_data = pd.DataFrame({
            'nam': [2023, 2023, 2024],
            'thang': [1, 2, 1],
            'tongdoanhthu': ['1,500,000', '2,000,000', '1,800,000'],
            'sotiepnhan': [100, 120, 110],
            'tennhomdichvu': ['Xét nghiệm', 'Chẩn đoán hình ảnh', 'Xét nghiệm'],
            'tendichvu': ['Xét nghiệm máu', 'X-quang ngực', 'Xét nghiệm nước tiểu'],
            'loai_dich_vu': ['Ngoại trú', 'Nội trú', 'Ngoại trú']
        })
        st.dataframe(sample_data)
    
    st.stop()  # Dừng app nếu không có dữ liệu

# ===== CUSTOM COMPONENTS =====
def render_header(title, subtitle=""):
    """Render header đẹp với gradient"""
    st.markdown(f"""
    <div class="custom-header">
        <h1 class="text-4xl font-bold">{title}</h1>
        {f'<p class="text-xl mt-2 opacity-90">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def render_kpi_card(label, value, change=None, icon="📊"):
    """Render KPI card đẹp"""
    if change:
        change_class = "badge-success" if change >= 0 else "badge-warning"
        change_html = f'<div class="{change_class} metric-badge mt-2">{icon} {"+" if change >= 0 else ""}{change:.1f}%</div>'
    else:
        change_html = ""
    
    st.markdown(f"""
    <div class="kpi-card">
        <div class="flex items-center justify-between">
            <div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
            </div>
            <div class="text-3xl">{icon}</div>
        </div>
        {change_html}
    </div>
    """, unsafe_allow_html=True)

# ===== PHẦN SIDEBAR (BỘ LỌC) =====
st.sidebar.header("🎯 Bộ lọc dữ liệu")

if 'nam' not in df.columns:
    st.error("File CSV không có cột 'nam'. Vui lòng kiểm tra lại dữ liệu.")
    st.stop()

year_list = sorted(df['nam'].dropna().unique())
if not year_list:
    st.error("Không có dữ liệu năm nào")
    st.stop()

selected_year = st.sidebar.selectbox(
    "**Chọn Năm**", 
    year_list, 
    index=len(year_list)-1,
    help="Chọn năm để phân tích dữ liệu"
)

# Thêm các filter khác
if 'tennhomdichvu' in df.columns:
    service_groups = ["Tất cả"] + sorted(df['tennhomdichvu'].dropna().unique().tolist())
    selected_service = st.sidebar.selectbox(
        "**Lọc theo nhóm dịch vụ**",
        service_groups
    )

show_details = st.sidebar.checkbox("Hiển thị bảng dữ liệu", value=True)
chart_height = st.sidebar.slider("Chiều cao biểu đồ", 300, 600, 400)

# ===== LỌC DỮ LIỆU =====
df_filtered = df[df['nam'] == selected_year].copy()

if selected_service != "Tất cả" and 'tennhomdichvu' in df.columns:
    df_filtered = df_filtered[df_filtered['tennhomdichvu'] == selected_service]

if df_filtered.empty:
    st.warning(f"Không có dữ liệu cho năm {selected_year}" + 
               (f" và nhóm dịch vụ '{selected_service}'" if selected_service != "Tất cả" else ""))
    st.stop()

# ===== HIỂN THỊ DASHBOARD =====
render_header(
    f"🏥 Phân Tích Dữ Liệu Y Tế", 
    f"Năm {selected_year} | Tổng {len(df_filtered):,} bản ghi" +
    (f" | Nhóm: {selected_service}" if selected_service != "Tất cả" else "")
)

# ===== PHẦN 1: KPI CARDS =====
st.markdown('<div class="mt-6"></div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if 'revenue' in df_filtered.columns:
        total_rev = df_filtered['revenue'].sum()
        render_kpi_card("Tổng Doanh Thu", f"{total_rev:,.0f} VNĐ", icon="💰")

with col2:
    if 'sotiepnhan' in df_filtered.columns:
        total_patients = df_filtered['sotiepnhan'].nunique()
        render_kpi_card("Tổng Lượt Tiếp Nhận", f"{total_patients:,}", icon="👥")

with col3:
    if 'revenue' in df_filtered.columns:
        avg_rev = df_filtered['revenue'].mean()
        render_kpi_card("Doanh Thu Trung Bình", f"{avg_rev:,.0f} VNĐ", icon="📈")

with col4:
    if 'tennhomdichvu' in df_filtered.columns and 'revenue' in df_filtered.columns:
        try:
            top_service = df_filtered.groupby('tennhomdichvu')['revenue'].sum().idxmax()
            render_kpi_card("Nhóm DV Cao Nhất", str(top_service)[:20], icon="🏆")
        except:
            render_kpi_card("Nhóm DV Cao Nhất", "N/A", icon="🏆")

st.markdown('<div class="mt-8"></div>', unsafe_allow_html=True)

# ===== PHẦN 2: TABS VỚI CHART =====
tab1, tab2, tab3 = st.tabs([
    "📈 **Xu Hướng Doanh Thu**", 
    "📊 **Cơ Cấu Dịch Vụ**", 
    "👥 **Đối Tượng & Chính Sách**"
])

# TAB 1: Xu hướng doanh thu
with tab1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('### <span class="text-gray-800 font-bold">📈 Xu Hướng Doanh Thu Theo Tháng</span>', unsafe_allow_html=True)
    
    if 'thang' in df_filtered.columns and 'revenue' in df_filtered.columns:
        monthly_data = df_filtered[['thang', 'revenue']].dropna()
        if not monthly_data.empty:
            monthly_rev = monthly_data.groupby('thang')['revenue'].sum().reset_index()
            
            fig_line = px.line(
                monthly_rev, 
                x='thang', 
                y='revenue',
                markers=True,
                line_shape='spline',
                title=f"Biến động doanh thu năm {selected_year}",
                labels={'thang': 'Tháng', 'revenue': 'Doanh thu (VNĐ)'},
                template='plotly_white'
            )
            
            fig_line.update_traces(
                line=dict(width=4, color='#7c3aed'),
                marker=dict(size=10, color='#8b5cf6')
            )
            
            fig_line.update_layout(
                height=chart_height,
                plot_bgcolor='white',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Không có dữ liệu doanh thu theo tháng")
    else:
        st.info("Thiếu cột 'thang' hoặc 'revenue' trong dữ liệu")
    
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 2: Cơ cấu dịch vụ
with tab2:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('### <span class="text-gray-800 font-bold">📊 Doanh Thu Theo Nhóm Dịch Vụ</span>', unsafe_allow_html=True)
        
        if 'tennhomdichvu' in df_filtered.columns and 'revenue' in df_filtered.columns:
            group_data = df_filtered[['tennhomdichvu', 'revenue']].dropna()
            if not group_data.empty:
                group_rev = group_data.groupby('tennhomdichvu')['revenue'].sum().sort_values(ascending=True).reset_index()
                
                fig_bar = px.bar(
                    group_rev.tail(10),  # Top 10
                    x='revenue', 
                    y='tennhomdichvu', 
                    orientation='h',
                    title="Top 10 nhóm dịch vụ doanh thu cao nhất",
                    labels={'revenue': 'Doanh thu (VNĐ)', 'tennhomdichvu': 'Nhóm dịch vụ'},
                    color='revenue',
                    color_continuous_scale='Viridis',
                    template='plotly_white'
                )
                
                fig_bar.update_layout(height=chart_height, showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_b:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('### <span class="text-gray-800 font-bold">🥧 Top 10 Dịch Vụ Phổ Biến</span>', unsafe_allow_html=True)
        
        if 'tendichvu' in df_filtered.columns:
            service_counts = df_filtered['tendichvu'].value_counts().head(10).reset_index()
            if not service_counts.empty:
                fig_pie = px.pie(
                    service_counts, 
                    values='count', 
                    names='tendichvu',
                    hole=0.3,
                    title="Tỉ lệ lượt thực hiện dịch vụ",
                    template='plotly_white',
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(height=chart_height)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Không có dữ liệu dịch vụ")
        
        st.markdown('</div>', unsafe_allow_html=True)

# TAB 3: Đối tượng và chính sách
with tab3:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('### <span class="text-gray-800 font-bold">👥 Phân Tích Loại Dịch Vụ</span>', unsafe_allow_html=True)
    
    if 'loai_dich_vu' in df_filtered.columns and 'tennhomdichvu' in df_filtered.columns and 'revenue' in df_filtered.columns:
        sun_data = df_filtered[['loai_dich_vu', 'tennhomdichvu', 'revenue']].dropna()
        if not sun_data.empty:
            fig_sun = px.sunburst(
                sun_data, 
                path=['loai_dich_vu', 'tennhomdichvu'], 
                values='revenue',
                title="Cấu trúc doanh thu theo loại và nhóm dịch vụ",
                template='plotly_white',
                color_continuous_scale='RdBu'
            )
            
            fig_sun.update_layout(height=chart_height + 100)
            st.plotly_chart(fig_sun, use_container_width=True)
        else:
            st.info("Không đủ dữ liệu để vẽ biểu đồ sunburst")
    else:
        st.info("Thiếu cột cần thiết cho biểu đồ")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===== PHẦN 3: DATA TABLE =====
if show_details:
    st.markdown('<div class="mt-8"></div>', unsafe_allow_html=True)
    with st.expander("📋 **Xem Dữ Liệu Chi Tiết**", expanded=False):
        st.markdown('<div class="data-table">', unsafe_allow_html=True)
        st.dataframe(
            df_filtered.head(100),
            use_container_width=True,
            height=400
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption(f"Hiển thị 100 dòng đầu tiên trong tổng số {len(df_filtered):,} dòng")

# ===== FOOTER =====
st.markdown("---")
st.markdown("""
<div class="text-center text-gray-500 text-sm mt-8">
    <p>🏥 <strong>Hospital Data Analytics Dashboard</strong> | Built with Streamlit & Plotly</p>
    <p class="mt-2">📊 Phiên bản 2.0 | Giao diện Tailwind CSS Inspired | Dữ liệu: {file_name}</p>
</div>
""".format(file_name=uploaded_file.name if uploaded_file else "local file"), unsafe_allow_html=True)