import streamlit as st
import pandas as pd
import math
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np

# 页面基础设置
st.set_page_config(page_title="车厢自动拆解演示系统", layout="wide")

# --- 核心算法：骨架与蒙皮拆解 ---
def solve_structure(L, W, H, max_dist, skin_w):
    # 1. 骨架：计算立柱数量与间距
    post_count = math.ceil(L / max_dist) + 1
    actual_dist = L / (post_count - 1)
    
    # 2. 蒙皮：计算标准板材切割
    skin_num = math.ceil(L / skin_w)
    
    # 3. BOM汇总
    bom = [
        {"零件": "主纵梁", "规格": "100x50x4.0 槽钢", "长度": L, "数量": 2},
        {"零件": "横梁", "规格": "80x40x3.0 C型钢", "长度": W, "数量": post_count},
        {"零件": "侧立柱", "规格": "40x40x2.0 方管", "长度": H, "数量": post_count * 2},
        {"零件": "侧蒙皮", "规格": "1.2mm 铝合金板", "宽度": skin_w, "高度": H, "数量": skin_num * 2}
    ]
    return post_count, actual_dist, skin_num, bom

# --- UI 界面 ---
st.title("🚛 货车厢体参数化自动拆解系统")
st.sidebar.header("📐 输入车厢参数")

# 用户交互输入
length = st.sidebar.slider("厢体长度 (L)", 2000, 9600, 4200)
width = st.sidebar.slider("厢体宽度 (W)", 1800, 2600, 2100)
height = st.sidebar.slider("厢体高度 (H)", 1500, 3000, 2100)
max_d = st.sidebar.number_input("立柱最大间距约束", 400, 800, 600)
s_width = st.sidebar.selectbox("标准蒙皮宽度", [1000, 1200, 1500])

# 执行拆解计算
n_posts, dist, n_skins, bom_list = solve_structure(length, width, height, max_d, s_width)

# --- 结果展示区 ---
col1, col2, col3 = st.columns(3)
col1.metric("立柱总数 (单侧)", f"{n_posts} 根")
col2.metric("实际安装间距", f"{dist:.1f} mm")
col3.metric("侧面蒙皮需求", f"{n_skins} 张")

# --- 2D 图形化预览 (原有的) ---
st.subheader("🖼️ 2D 侧围骨架分布预览")
fig_2d, ax_2d = plt.subplots(figsize=(10, 3))
ax_2d.set_facecolor('#f0f2f6')
# 画边框
ax_2d.add_patch(plt.Rectangle((0, 0), length, height, color='white', ec='black', lw=2))
# 画自动生成的立柱
for i in range(n_posts):
    x_pos = i * dist
    ax_2d.axvline(x=x_pos, color='#1f77b4', linestyle='--', alpha=0.7)
    ax_2d.text(x_pos, -200, f"{int(x_pos)}", ha='center', fontsize=7)
ax_2d.set_xlim(-200, length + 200)
ax_2d.set_ylim(-400, height + 200)
ax_2d.set_aspect('equal')
ax_2d.axis('off')
st.pyplot(fig_2d)

# --- 3D 厢体结构预览 ---
st.subheader("✨ 3D 厢体结构预览")

# 定义厢体顶点 (简化为线框模型)
x = [0, length, length, 0, 0, length, length, 0]
y = [0, 0, width, width, 0, 0, width, width]
z = [0, 0, 0, 0, height, height, height, height]

# 骨架线段
# 底部
trace_x = [0, length, length, 0, 0, None, 0, 0, None, length, length]
trace_y = [0, 0, width, width, 0, None, 0, width, None, 0, width]
trace_z = [0, 0, 0, 0, 0, None, height, height, None, height, height]

# 顶部
trace_x += [0, length, length, 0, 0, None, 0, 0, None, length, length]
trace_y += [0, 0, width, width, 0, None, 0, width, None, 0, width]
trace_z += [height, height, height, height, height, None, 0, 0, None, 0, 0] # 这里Z轴是反的，需要注意

# 连接上下层
trace_x += [0, 0, None, length, length, None, length, length, None, 0, 0]
trace_y += [0, 0, None, 0, 0, None, width, width, None, width, width]
trace_z += [0, height, None, 0, height, None, 0, height, None, 0, height]

# 添加立柱 (简化为X方向的线)
for i in range(n_posts):
    x_pos = i * dist
    trace_x.extend([x_pos, x_pos, None])
    trace_y.extend([0, 0, None]) # 假设只显示底部立柱线
    trace_z.extend([0, height, None])

# 创建 Plotly 3D 散点图
fig_3d = px.line_3d(
    x=trace_x, y=trace_y, z=trace_z, 
    range_x=[0, length], range_y=[0, width], range_z=[0, height],
    title="厢体线框预览",
    labels={'x': '长度 (mm)', 'y': '宽度 (mm)', 'z': '高度 (mm)'}
)

# 调整布局，使其更像一个线框图
fig_3d.update_traces(line=dict(color='blue', width=2), mode='lines')
fig_3d.update_layout(scene_aspectmode='data', 
                    scene_camera=dict(eye=dict(x=1.5, y=1.5, z=0.8)), # 调整初始视角
                    margin=dict(l=0, r=0, b=0, t=50)) # 减少边距
st.plotly_chart(fig_3d, use_container_width=True)


# BOM 表输出
st.subheader("📋 自动生成生产下料单 (BOM)")
st.table(pd.DataFrame(bom_list))

# 导出功能
st.download_button(
    label="📥 下载生产数据清单 (CSV)",
    data=pd.DataFrame(bom_list).to_csv(index=False).encode('utf-8'),
    file_name='production_bom.csv',
    mime='text/csv',
)

import ezdxf
import io

def generate_dxf(L, H, n_posts, dist):
    # 创建一个新的 DXF 文件（使用 R2010 格式，兼容性最好）
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # 1. 绘制蒙皮外轮廓 (图层: 0)
    msp.add_lwpolyline([(0, 0), (L, 0), (L, H), (0, H), (0, 0)])

    # 2. 绘制立柱中心线/铆钉线 (图层: MARKING)
    doc.layers.new(name='MARKING', dxfattribs={'color': 1}) # 红色标注线
    for i in range(n_posts):
        x = i * dist
        msp.add_line((x, 0), (x, H), dxfattribs={'layer': 'MARKING'})
        
        # 模拟：在立柱线上每隔 200mm 自动打一个铆钉孔
        for y_hole in range(200, H, 200):
            msp.add_circle((x, y_hole), radius=2.5, dxfattribs={'layer': 'MARKING'})

    # 将 DXF 写入内存流以便下载
    out = io.StringIO()
    doc.write(out)
    return out.getvalue()

# --- 在 Streamlit UI 中增加下载按钮 ---
st.subheader("🛠️ 生产数据对接")
dxf_string = generate_dxf(length, height, n_posts, dist)

col_dxf, col_csv = st.columns(2)
with col_dxf:
    st.download_button(
        label="🚀 下载侧围加工 DXF 图纸",
        data=dxf_string,
        file_name=f"side_panel_{length}x{height}.dxf",
        mime="application/dxf",
        help="此文件可直接导入 AutoCAD 或激光切割系统"
    )
