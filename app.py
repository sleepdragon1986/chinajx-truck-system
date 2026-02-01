import streamlit as st
import pandas as pd
import math
import matplotlib.pyplot as plt

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

# 图形化预览
st.subheader("🖼️ 侧围结构预览 (自动布局)")
fig, ax = plt.subplots(figsize=(10, 3))
ax.set_facecolor('#f0f2f6')
# 画边框
ax.add_patch(plt.Rectangle((0, 0), length, height, color='white', ec='black', lw=2))
# 画自动生成的立柱
for i in range(n_posts):
    x_pos = i * dist
    ax.axvline(x=x_pos, color='#1f77b4', linestyle='--', alpha=0.7)
    ax.text(x_pos, -200, f"{int(x_pos)}", ha='center', fontsize=7)
ax.set_xlim(-200, length + 200)
ax.set_ylim(-400, height + 200)
ax.axis('off')
st.pyplot(fig)



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
