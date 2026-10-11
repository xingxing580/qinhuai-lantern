import base64
import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import pydeck as pdk
import uuid
from PIL import Image
import io
import sqlite3

# ========== 模块4｜历史时光卷轴 + 轮播图（史实版） ==========
def time_scroll_reel():
    """横向时光卷轴 + 卷轴下方图集：点击朝代自动滚动到对应图景"""
    import json

    if "reel_period" not in st.session_state:
        st.session_state["reel_period"] = "wei_jin"

    # ========== 朝代元数据（你的史实完全保留不变） ==========
    dynasty_data = {
        "wei_jin": {
            "name": "魏晋南北朝（六朝）",
            "record": "都城建康（今南京）出现元宵燃灯习俗。梁简文帝萧纲作《列灯赋》，描写宫廷上元张灯盛景；此时灯俗以礼佛、祭祀蚕神为主，灯彩由宫廷逐步流向士族宅邸，秦淮河畔始有零星张灯。",
            "event": [
                "南朝梁简文帝《列灯赋》记载建康宫廷燃灯",
                "上元燃灯融合佛事祭祀，灯俗萌芽",
                "秦淮河沿岸士族宅邸开始效仿宫廷挂灯",
            ],
            "stat": {
                "灯会规模": "宫廷+士族宅邸，民间尚未普及",
                "持续时长": "上元1夜（正月十五）",
                "代表地点": "建康（南京）台城、秦淮河沿岸宅邸",
                "史料出处": "《南史》、梁简文帝《列灯赋》",
            },
        },
        "sui_tang": {
            "name": "隋唐",
            "record": "上元放夜制度确立，正月十四至十六连续三夜解禁夜游。金陵（南京）延续六朝灯俗，民间赏灯风气兴起，灯彩制作技艺提升，秦淮河逐步成为观灯游览区域。",
            "event": [
                "确立上元三夜放夜制度，允许百姓夜游观灯",
                "灯彩从祭祀向民间游乐转型",
                "金陵秦淮河畔形成观灯游览地带",
            ],
            "stat": {
                "灯会规模": "城市官民共同参与",
                "持续时长": "正月十四至十六，共3夜",
                "代表地点": "金陵（南京）、长安、洛阳",
                "史料出处": "《初学记》、唐上元放夜制度记载",
            },
        },
        "ming": {
            "name": "明代（鼎盛期）",
            "record": "朱元璋定都南京，将元宵张灯延长至十夜（正月初八上灯，正月十八落灯），为中国古代最长灯节。洪武五年，秦淮河燃放万盏水灯；余怀《板桥杂记》记载“秦淮灯船之盛，天下所无”。",
            "event": [
                "朱元璋诏令：正月初八至十八，十夜张灯",
                "洪武五年（1372）秦淮河施放万盏水灯",
                "秦淮灯船兴起，十里画舫载灯夜游",
                "《上元灯彩图》记录南京灯市百态",
            ],
            "stat": {
                "灯会规模": "全国顶级灯市，“家家走桥，人人看灯”",
                "持续时长": "正月初八至正月十八，共10夜",
                "代表地点": "南京秦淮河、夫子庙、笪桥、三山街",
                "史料出处": "《七修类稿》《板桥杂记》《陶庵梦忆》",
            },
        },
        "qing": {
            "name": "清代",
            "record": "灯市分为三处：笪桥、评事街、夫子庙。甘熙《白下琐言》记载：“笪桥灯市，为金陵一胜。”花灯以剪纸、彩帛灯为主，后期灯市中心逐步向夫子庙转移。",
            "event": [
                "笪桥灯市为金陵灯市核心，纸灯技艺兴盛",
                "评事街主营彩帛花灯，品类丰富",
                "灯市逐步由笪桥向夫子庙转移",
            ],
            "stat": {
                "灯会规模": "民间市井大型灯市",
                "持续时长": "正月初八上灯，正月十八落灯",
                "代表地点": "笪桥、评事街、夫子庙",
                "史料出处": "甘熙《白下琐言》",
            },
        },
        "modern": {
            "name": "现代（当代）",
            "record": "1977夫子庙恢复灯市；1986首届现代秦淮灯会正式举办。2006年，秦淮灯会列入首批国家级非物质文化遗产名录；灯会融合传统扎灯技艺与现代灯光，每年春节至元宵举办。",
            "event": [
                "1977年夫子庙恢复春节灯市",
                "1986年第一届现代秦淮灯会正式举办",
                "2006年入选首批国家级非物质文化遗产名录",
                "灯会走向全国文旅联展，海外文化交流",
            ],
            "stat": {
                "灯会规模": "百万级游客，国内规模最大民俗灯会之一",
                "持续时长": "春节至元宵，约40‑50天",
                "代表地点": "夫子庙、老门东、白鹭洲公园",
                "史料出处": "南京市文旅局官方档案、非遗名录文件",
            },
        },
    }

    # ---------- URL参数同步：拿到reel之后直接写入session，立刻rerun，不要靠JS监听URL变化（streamlit限制） ----------
    _qp = st.query_params
    reel_from_url = _qp.get("reel")
    if reel_from_url in dynasty_data:
        st.session_state["reel_period"] = reel_from_url
        del _qp["reel"]
        st.rerun()

    cur_key0 = st.session_state["reel_period"]

    # ---------- 横向卷轴HTML（保留全部原有样式） ----------
    html_reel = f'''
    <style>
    * {{
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }}
    body {{
        background: transparent;
        font-family: "KaiTi", "SimSun", serif;
    }}
    .reel-outer {{
        width: 100%;
        background:
            linear-gradient(180deg, rgba(74,13,13,0.96), rgba(26,4,4,0.96)),
            repeating-linear-gradient(
                90deg,
                rgba(201,162,75,0.06) 0px,
                rgba(201,162,75,0.06) 2px,
                transparent 2px,
                transparent 14px
            );
        border-radius: 18px;
        border: 2px solid #8a6d2f;
        box-shadow:
            inset 0 0 30px rgba(0,0,0,0.6),
            0 10px 30px rgba(0,0,0,0.5);
        padding: 18px 14px 14px 14px;
        position: relative;
        overflow: hidden;
    }}

    .reel-outer::before, .reel-outer::after {{
        content: "";
        position: absolute;
        top: 50%;
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #ffd977, #8a6d2f 70%, #4a0d0d);
        border: 2px solid #ffd977;
        box-shadow: 0 0 18px rgba(255,170,50,0.55);
        transform: translateY(-50%);
    }}

    .reel-outer::before {{
        left: -18px;
    }}

    .reel-outer::after {{
        right: -18px;
    }}

    .reel-title {{
        color: #ffd977;
        font-size: 22px;
        font-weight: bold;
        letter-spacing: 8px;
        text-align: center;
        margin-bottom: 14px;
        text-shadow:
            0 0 10px rgba(255,170,50,0.7),
            0 2px 4px rgba(0,0,0,0.9);
    }}

    .reel-title::before, .reel-title::after {{
        content: "🏮";
        margin: 0 12px;
    }}

    .scroll-container {{
        width: 100%;
        overflow-x: auto;
        overflow-y: hidden;
        display: flex;
        gap: 18px;
        padding: 10px 6px 14px 6px;
        scroll-behavior: smooth;
    }}

    .scroll-container::-webkit-scrollbar {{
        height: 10px;
    }}

    .scroll-container::-webkit-scrollbar-track {{
        background: rgba(201,162,75,0.12);
        border-radius: 10px;
    }}

    .scroll-container::-webkit-scrollbar-thumb {{
        background: linear-gradient(90deg, #c9a24b, #ffd977, #c9a24b);
        border-radius: 10px;
        border: 1px solid #8a6d2f;
    }}

    .scroll-container::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(90deg, #ffd977, #ffe9a8, #ffd977);
    }}

    .time-node {{
        min-width: 240px;
        max-width: 260px;
        flex: 0 0 auto;
        background:
            linear-gradient(160deg, rgba(64,24,14,0.96), rgba(26,4,4,0.96));
        border: 2px solid #703820;
        border-radius: 16px;
        padding: 18px 16px;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}

    .time-node::before {{
        content: "";
        position: absolute;
        top: 10px;
        left: 10px;
        width: 14px;
        height: 14px;
        border-top: 2px solid #ffd977;
        border-left: 2px solid #ffd977;
    }}

    .time-node::after {{
        content: "";
        position: absolute;
        bottom: 10px;
        right: 10px;
        width: 14px;
        height: 14px;
        border-bottom: 2px solid #ffd977;
        border-right: 2px solid #ffd977;
    }}

    .time-node:hover {{
        transform: translateY(-6px);
        border-color: #ffbc58;
        box-shadow:
            0 10px 24px rgba(255,120,40,0.45),
            inset 0 0 18px rgba(255,170,50,0.12);
    }}

    .time-node.active {{
        border-color: #ffd066;
        background:
            linear-gradient(160deg, rgba(120,30,20,0.98), rgba(50,10,10,0.98));
        box-shadow:
            0 0 0 2px #ffd977,
            0 0 28px rgba(255,170,50,0.75),
            inset 0 0 22px rgba(255,170,50,0.2);
    }}

    .dynasty-name {{
        color: #ffd977;
        font-size: 20px;
        font-weight: bold;
        letter-spacing: 4px;
        margin-bottom: 10px;
        text-shadow: 0 0 8px rgba(255,170,50,0.6);
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .dynasty-tag {{
        font-size: 12px;
        color: #ffddbb;
        background: rgba(255,170,50,0.12);
        border: 1px solid rgba(255,170,50,0.35);
        border-radius: 10px;
        padding: 2px 8px;
        letter-spacing: 2px;
    }}

    .dynasty-desc {{
        color: #ffddbb;
        font-size: 14px;
        line-height: 1.7;
        letter-spacing: 1px;
    }}

    .node-footer {{
        margin-top: 14px;
        height: 1px;
        background: linear-gradient(90deg, transparent, #c9a24b, transparent);
    }}
    </style>

    <div class="reel-outer">
        <div class="reel-title">🏮 秦淮灯会 · 历史时光卷轴 🏮</div>

        <div class="scroll-container" id="scrollBox">
            <div class="time-node" data-key="wei_jin">
                <div class="dynasty-name">魏晋南北朝 <span class="dynasty-tag">六朝</span></div>
                <div class="dynasty-desc">建康上元灯俗萌芽，《列灯赋》记宫廷燃灯，灯彩渐传士族宅邸。</div>
                <div class="node-footer"></div>
            </div>

            <div class="time-node" data-key="sui_tang">
                <div class="dynasty-name">隋唐 <span class="dynasty-tag">放夜</span></div>
                <div class="dynasty-desc">上元三夜放夜，官民夜游观灯，金陵灯俗由宫廷走向城市市井。</div>
                <div class="node-footer"></div>
            </div>

            <div class="time-node" data-key="ming">
                <div class="dynasty-name">明代 <span class="dynasty-tag">鼎盛</span></div>
                <div class="dynasty-desc">十夜灯节，秦淮灯船甲天下，《上元灯彩图》记录南京灯市盛景。</div>
                <div class="node-footer"></div>
            </div>

            <div class="time-node" data-key="qing">
                <div class="dynasty-name">清代 <span class="dynasty-tag">市井</span></div>
                <div class="dynasty-desc">笪桥灯市兴盛，评事街花灯精巧，灯市中心逐渐转向夫子庙。</div>
                <div class="node-footer"></div>
            </div>

            <div class="time-node" data-key="modern">
                <div class="dynasty-name">现代 <span class="dynasty-tag">非遗</span></div>
                <div class="dynasty-desc">灯会恢复举办，列入首批国家级非遗，成为南京城市文化名片。</div>
                <div class="node-footer"></div>
            </div>
        </div>
    </div>

    <script>
    const initKey = "{cur_key0}";
    const nodes = document.querySelectorAll(".time-node");
    nodes.forEach(function(el){{
        if (el.getAttribute("data-key") === initKey) {{
            el.classList.add("active");
        }}
        el.onclick = function() {{
            const k = this.getAttribute("data-key");
            const p = new URLSearchParams(location.search);
            p.set("reel", k);
            location.search = p.toString();
        }};
    }});
    </script>
    '''

    col1, col2 = st.columns([2.1, 1.3])
    with col1:
        st.components.v1.html(html_reel, height=330, scrolling=False)

        img_map = {
            "wei_jin": "pic_wei.png",
            "sui_tang": "pic_tang.png",
            "ming": "pic_ming.png",
            "qing": "pic_qing.png",
            "modern": "pic_modern.png",
        }

        slides = []
        for k, fname in img_map.items():
            b64 = _img_b64(fname)
            if b64:
                if k == "ming":
                    cap = f"🏮 明代灯会图景"
                else:
                    cap = f"🏮 现代灯会图景"

                slides.append({
                    "key": k,
                    "src": "data:image/png;base64," + b64,
                    "cap": cap
                })

        if slides:
            key_index_map = {item["key"]: idx for idx, item in enumerate(slides)}
            map_json = json.dumps(key_index_map, ensure_ascii=False)
            slides_json = json.dumps(slides, ensure_ascii=False)
            # 👉重点：把当前session的朝代key直接注入JS，不再靠监听浏览器URL
            current_js_key = json.dumps(cur_key0, ensure_ascii=False)

            gallery_html = f'''
            <style>
            .reel-gallery-wrap {{
                width:100%;
                margin-top:8px;
                border:2px solid #703820;
                border-radius:14px;
                box-shadow:0 8px 30px rgba(0,0,0,0.55);
                overflow:hidden;
                background:#1a0404;
            }}
            .reel-gallery {{
                display:flex;
                gap:14px;
                overflow-x:auto;
                overflow-y:hidden;
                padding:12px;
                scroll-behavior:smooth;
            }}
            .reel-gallery::-webkit-scrollbar {{height:10px;}}
            .reel-gallery::-webkit-scrollbar-track {{background:rgba(201,162,75,0.12);border-radius:10px;}}
            .reel-gallery::-webkit-scrollbar-thumb {{
                background:linear-gradient(90deg,#c9a24b,#ffd977,#c9a24b);
                border-radius:10px;border:1px solid #8a6d2f;
            }}
            .gallery-item {{
                flex:0 0 320px;
                height:300px;
                border-radius:8px;
                overflow:hidden;
                position:relative;
            }}
            .gallery-item img {{
                width:100%;height:100%;
                object-fit:contain;
                background:#0e0202;
            }}
            .gallery-cap {{
                position:absolute;
                bottom:0;left:0;right:0;
                padding:8px 10px;
                background:linear-gradient(transparent,rgba(0,0,0,0.75));
                color:#ffdd99;
                text-align:center;
                font-family:"KaiTi",serif;
                font-size:15px;
                letter-spacing:3px;
            }}
            </style>
            <div class="reel-gallery-wrap">
                <div class="reel-gallery" id="galleryScrollBox">
            '''
            for s in slides:
                gallery_html += f'''
                <div class="gallery-item">
                    <img src="{s['src']}" alt="{s['cap']}">
                    <div class="gallery-cap">{s['cap']}</div>
                </div>
                '''
            gallery_html += '''
                </div>
            </div>
            <script>
                const slides = ''' + slides_json + ''';
                const keyToIdx = ''' + map_json + ''';
                const activeKey = ''' + current_js_key + ''';
                const scrollBox = document.getElementById("galleryScrollBox");

                function scrollToEra(key){
                    const idx = keyToIdx[key];
                    if(idx===undefined) return;
                    const item = scrollBox.children[idx];
                    if(item){
                        const offsetLeft = item.offsetLeft - scrollBox.clientWidth/2 + item.offsetWidth/2;
                        scrollBox.scrollTo({left:offsetLeft,behavior:"smooth"});
                    }
                }
                //页面渲染完成直接使用python传入的session_key滚动，不再监听浏览器url
                setTimeout(()=>{
                    scrollToEra(activeKey);
                },120)
            </script>
            '''
            st.components.v1.html(gallery_html, height=345)
        else:
            st.info("💡 在 app 同级目录放入 pic_wei.png / pic_tang.png / pic_ming.png / pic_qing.png / pic_modern.png 即可开启图集。")

    with col2:
        curr = dynasty_data[st.session_state["reel_period"]]
        st.subheader(f"📜 {curr['name']}｜灯会史料")
        st.markdown(f"> {curr['record']}")
        st.markdown("**🔔 关键历史事件**")
        for evt in curr["event"]:
            st.markdown(f"- {evt}")
        st.markdown("---")
        st.markdown("**📊 时代灯会概况**")
        for k, v in curr["stat"].items():
            st.markdown(f"**{k}：** {v}")

    sel = st.selectbox(
        "🕰️ 切换朝代视角",
        options=list(dynasty_data.keys()),
        format_func=lambda x: dynasty_data[x]["name"],
        index=list(dynasty_data.keys()).index(st.session_state["reel_period"]),
        key="reel_sel",
    )
    st.session_state["reel_period"] = sel

# ---------- 9. 生成 base64 图片 ----------
def generate_lantern_image(lantern):
    width, height = 400, 480
    img = Image.new("RGB", (width, height), "#1a0404")

    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)

    # 背景光晕
    for r in range(120, 0, -5):
        color = (
            int(60 - r * 0.3),
            int(10 + r * 0.15),
            int(10 + r * 0.1),
        )
        draw.ellipse(
            [width // 2 - r, height // 2 - r, width // 2 + r, height // 2 + r],
            fill=color,
        )

    # 主灯体色块
    color_map = {
        "朱砂红": (200, 29, 17),
        "石青": (31, 111, 139),
        "鎏金": (212, 168, 67),
        "藤黄": (239, 180, 43),
    }
    main_color = color_map.get(lantern["color"], (212, 168, 67))

    draw.ellipse([110, 110, 290, 370], fill=main_color, outline=(74, 13, 13), width=4)

    # 编号文字
    try:
        font = ImageFont.truetype("simhei.ttf", 24)
    except:
        font = ImageFont.load_default()

    draw.text((20, 20), lantern["id"], fill=(255, 217, 119), font=font)
    draw.text((20, 430), lantern["comment"], fill=(243, 227, 195), font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ========== 页面基础配置 ==========
st.set_page_config(
    page_title="灯映金陵｜秦淮灯会可视化",
    layout="wide",
    page_icon="🏮"
)

_APP_DIR = os.path.dirname(os.path.abspath(__file__))


def _img_b64(filename):
    """读取同目录图片并转 base64，缺失返回 None"""
    path = os.path.join(_APP_DIR, filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


_GATE_B64 = _img_b64("qinhuai_gate.jpg")  # 首页背景
_DASH_B64 = _img_b64("qinhuai_bg.png")  # 看板背景

# 【新增】首页轮播png图片列表，在这里修改你的图片文件名
slide_file_list = [
    "lamp1.png",
    "lamp2.png",
    "lamp3.png",
    "lamp4.png"
]
slide_b64_list = []
for fname in slide_file_list:
    b64 = _img_b64(fname)
    if b64 is not None:
        slide_b64_list.append(b64)

#  交互状态：page = "home"（首页） / "main"（数据看板）
if "page" not in st.session_state:
    st.session_state.page = "home"

#  🏮 交 互 式 首 页
if st.session_state.page == "home":
    # ---------- 首页专属 CSS：全屏背景 + 动态灯笼 + 大标题 +【新增自动轮播图】 ----------
    if _GATE_B64:
        _home_bg = (
            "background-image:"
            "linear-gradient(rgba(15,4,4,0.42), rgba(15,4,4,0.66)),"
            f"url(\"data:image/jpeg;base64,{_GATE_B64}\");"
            "background-size:cover;"
            "background-position:center;"
            "background-attachment:fixed;"
        )
    else:
        _home_bg = "background:radial-gradient(circle at 50% 20%, #4a0d0d 0%, #1a0404 70%);"

    # 拼接轮播图片div html
    slide_html_parts = []
    for idx, b64data in enumerate(slide_b64_list):
        slide_html_parts.append(f'''
        <div class="carousel-item item{idx + 1}" style="background-image:url(&quot;data:image/png;base64,{b64data}&quot;);"></div>
        ''')
    carousel_inner_html = "\n".join(slide_html_parts)

    st.markdown(f"""
    <style>
        /* 首页隐藏侧边栏与页头，全屏沉浸 */
        section[data-testid="stSidebar"], header[data-testid="stHeader"] {{
            display: none !important;
        }}
        .stApp {{ {_home_bg} }}

         .carousel-wrap {{
             position:relative;
             width:62vw;
             height:32vh;
             margin: 4vh auto 0 auto;
             overflow:hidden;
             border-radius:14px;
             box-shadow:0 0 24px rgba(0,0,0,0.7);
             z-index:1;
         }}
         .carousel-item {{
             position:absolute;
             width:100%;
             height:100%;
             background-size:cover;
             background-position:center;
             opacity:0;
             animation:carouselAnim 12s infinite; /* 4张 ×3s =12s */
         }}
         .item1 {{ animation-delay: 0s; }}
         .item2 {{ animation-delay: 3s; }}
         .item3 {{ animation-delay: 6s; }}
         .item4 {{ animation-delay: 9s; }}
         /* 删除 .item5 这一行，我们只有4张图 */

         @keyframes carouselAnim {{
             0%    {{ opacity: 0; }}
             4%    {{ opacity: 1; }}
             21%   {{ opacity: 1; }}
             25%   {{ opacity: 0; }}
             100%  {{ opacity: 0; }}
         }}

        /* 强制清除streamlit对markdown p标签自带margin，最高优先级 !important */
        div.stMarkdown p.gate-title {{
            font-family: "KaiTi", "SimSun", "serif" !important;
            font-size: 150px !important;
            font-weight: bold !important;
            text-align: center !important;
            color: #ffd977 !important;
            letter-spacing: 40px !important;
            margin: 6vh 0 0 0 !important;
            padding:0 !important;
            text-shadow:
                0 0 12px rgba(255,190,80,0.9),
                0 0 40px rgba(255,140,30,0.55),
                0 4px 8px rgba(0,0,0,0.9);
            animation: titleGlow 3.2s ease-in-out infinite;
            position:relative;
            z-index:2;
        }}
        @keyframes titleGlow {{
            0%, 100% {{ text-shadow: 0 0 12px rgba(255,190,80,0.9), 0 0 40px rgba(255,140,30,0.55), 0 4px 8px rgba(0,0,0,0.9); }}
            50%      {{ text-shadow: 0 0 22px rgba(255,210,110,1.0), 0 0 70px rgba(255,150,40,0.8), 0 4px 8px rgba(0,0,0,0.9); }}
        }}
        @media (max-width: 900px) {{
            .carousel-wrap {{ width:88vw;height:22vh; }}
            div.stMarkdown p.gate-title {{ font-size: 76px !important; letter-spacing: 16px !important; }}
            div.stMarkdown p.gate-subtitle {{ font-size: 20px !important; letter-spacing: 8px !important; }}
            div.stMarkdown p.gate-poem {{ font-size: 15px !important; }}
        }}

        div.stMarkdown p.gate-subtitle {{
            font-family: "KaiTi", "SimSun", serif !important;
            font-size: 26px !important;
            text-align: center !important;
            color: #f3e3c3 !important;
            letter-spacing: 12px !important;
            margin-top: 20px !important;
            padding:0 !important;
            text-shadow: 0 2px 6px rgba(0,0,0,0.9);
            position:relative;
            z-index:2;
        }}
        div.stMarkdown p.gate-poem {{
            font-family: "KaiTi", "SimSun", serif !important;
            font-size: 18px !important;
            text-align: center !important;
            color: rgba(243,227,195,0.85) !important;
            letter-spacing: 5px !important;
            margin-top: 36px !important;
            padding:0 !important;
            text-shadow: 0 2px 4px rgba(0,0,0,0.9);
            position:relative;
            z-index:2;
        }}

        /* ---------- 动态灯笼：左右摇曳升腾 ---------- */
        .lantern {{
            position: fixed;
            font-size: 54px;
            filter: drop-shadow(0 0 14px rgba(255,120,40,0.85));
            opacity: 0.95;
            z-index:0;
            animation: sway 4.5s ease-in-out infinite, floaty 7s ease-in-out infinite;
            user-select: none;
        }}
        .l1 {{ left: 7%;  top: 12%; animation-delay: 0s,   0s;   font-size: 64px; }}
        .l2 {{ left: 15%; top: 46%; animation-delay: .8s,  1.2s; font-size: 44px; }}
        .l3 {{ right: 8%; top: 15%; animation-delay: 1.6s, .6s;  font-size: 60px; }}
        .l4 {{ right: 16%;top: 52%; animation-delay: .4s,  1.8s; font-size: 42px; }}
        .l5 {{ left: 46%; top: 6%;  animation-delay: 2.1s, 1s;   font-size: 38px; opacity: .7; }}
        @keyframes sway {{
            0%, 100% {{ transform: rotate(-7deg); }}
            50%      {{ transform: rotate(7deg); }}
        }}
        @keyframes floaty {{
            0%, 100% {{ margin-top: 0; }}
            50%      {{ margin-top: -22px; }}
        }}

        /* ----------【修复：全屏居中按钮容器】 ---------- */
        div[data-testid="stButton"] {{
            display:flex !important;
            justify-content:center !important;
            width:100% !important;
            margin-top:22px !important;
            position:relative;
            z-index:2;
        }}
        div[data-testid="stButton"] button {{
            background: linear-gradient(180deg, #ffd977 0%, #d4a843 100%);
            color: #4a0d0d;
            font-family: "KaiTi", "SimSun", serif;
            font-size: 28px;
            font-weight: bold;
            letter-spacing: 10px;
            border: 2px solid #8a2b1d;
            border-radius: 44px;
            padding: 18px 72px;
            max-width:220px;
            box-shadow: 0 0 22px rgba(255,170,50,0.5), inset 0 1px 0 rgba(255,255,255,0.5);
            transition: all .25s ease;
        }}
        div[data-testid="stButton"] button:hover {{
            transform: translateY(-3px) scale(1.04);
            box-shadow: 0 0 38px rgba(255,190,70,0.9), inset 0 1px 0 rgba(255,255,255,0.6);
            background: linear-gradient(180deg, #ffe6a3 0%, #e0b452 100%);
        }}
        div[data-testid="stButton"] button p {{ color: #4a0d0d !important; }}

        .gate-footer {{
            position: fixed; bottom: 22px; width: 100%;
            text-align: center; color: rgba(243,227,195,0.55);
            font-size: 13px; letter-spacing: 3px;
            font-family: "KaiTi", "SimSun", serif;
            z-index:2;
        }}
    </style>
    """, unsafe_allow_html=True)

    # ---------- 首页内容 ----------
    st.markdown(
        '<span class="lantern l1">🏮</span><span class="lantern l2">🏮</span>'
        '<span class="lantern l3">🏮</span><span class="lantern l4">🏮</span>'
        '<span class="lantern l5">🏮</span>',
        unsafe_allow_html=True
    )

    # 【新增：渲染轮播图，仅当有有效png图片才渲染】
    if len(slide_b64_list) > 0:
        st.markdown(f'''
        <div class="carousel-wrap">
            {carousel_inner_html}
        </div>
        ''', unsafe_allow_html=True)

    st.markdown('<p class="gate-title">灯映金陵</p>', unsafe_allow_html=True)
    st.markdown('<p class="gate-subtitle">秦淮灯会 · 时空交互式可视化系统</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="gate-poem">十里秦淮灯火灿 &nbsp;·&nbsp; 楼台亭榭绕河堤 &nbsp;·&nbsp; 一梦金陵六百秋</p>',
        unsafe_allow_html=True
    )

    # 入场按钮：三列等宽布局，按钮置于中间列并撑满列宽 -> 严格水平居中
    _, c_btn, _ = st.columns([1, 1, 1])
    with c_btn:
        if st.button("入 场", use_container_width=True):
            st.session_state.page = "main"
            st.rerun()

    st.markdown('<p class="gate-footer">国家级非物质文化遗产 · 秦淮灯彩 ｜ 数据可视化实践</p>',
                unsafe_allow_html=True)
    st.stop()

#  📊 数 据 看 板（红金国风主题）
if _DASH_B64:
    _dash_bg = (
        "background-image:"
        "linear-gradient(rgba(26,4,4,0.78), rgba(26,4,4,0.86)),"
        f"url(\"data:image/png;base64,{_DASH_B64}\");"
        "background-size:cover;"
        "background-position:center;"
        "background-attachment:fixed;"
    )
else:
    _dash_bg = "background:radial-gradient(circle at 50% 20%, #4a0d0d 0%, #1a0404 70%);"

st.markdown(f"""
<style>
    /* ---------- 全局背景：秦淮灯会夜景 + 暗红遮罩，保证文字可读 ---------- */
    .stApp {{
        {_dash_bg}
        color: #f3e3c3;
    }}

    /* ---------- 顶部标题区 ---------- */
    .lantern-title {{
        font-size: 46px;
        color: #ffd977;
        text-align: center;
        font-family: "STKaiti", "KaiTi", "SimSun", serif;
        font-weight: bold;
        letter-spacing: 14px;
        text-shadow: 0 0 18px rgba(255,170,40,0.55), 0 2px 4px rgba(0,0,0,0.8);
        margin-top: 10px;
    }}
    .lantern-subtitle {{
        font-size: 19px;
        color: #e8c27a;
        text-align: center;
        font-family: "STKaiti", "KaiTi", "SimSun", serif;
        letter-spacing: 6px;
        margin-bottom: 36px;
        text-shadow: 0 1px 3px rgba(0,0,0,0.8);
    }}
    .title-divider {{
        display: flex; align-items: center; justify-content: center;
        gap: 18px; margin: 4px 0 30px 0;
    }}
    .title-divider .line {{
        height: 1px; width: 220px;
        background: linear-gradient(90deg, transparent, #c9a24b, transparent);
    }}

    /* ---------- 区块标题 ---------- */
    h2, h3 {{
        font-family: "STKaiti", "KaiTi", "SimSun", serif !important;
        color: #ffd977 !important;
        text-shadow: 0 1px 3px rgba(0,0,0,0.8);
        letter-spacing: 2px;
    }}

    /* ---------- 正文 / 说明文字 ---------- */
    p, li, span, label, .stMarkdown {{ color: #f3e3c3; }}

    /* ---------- 侧边栏：暗红织金 ---------- */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(46,8,8,0.97), rgba(26,4,4,0.97));
        border-right: 1px solid rgba(201,162,75,0.45);
    }}
    section[data-testid="stSidebar"] * {{ color: #f3e3c3; }}
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{ color: #ffd977 !important; }}
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] {{
        background-color: rgba(255,235,200,0.08);
    }}
    /* 看板中的按钮（如返回首页）统一为金线描边风格 */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button {{
        background: rgba(255,217,119,0.1);
        color: #ffd977;
        border: 1px solid #c9a24b;
        border-radius: 8px;
        width: 100%;
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] button p {{ color: #ffd977 !important; }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {{
        background: rgba(255,217,119,0.22);
    }}

    /* ---------- info 区块 ---------- */
    [data-testid="stAlert"] {{
        background-color: rgba(60,14,14,0.85);
        border: 1px solid rgba(201,162,75,0.5);
        border-radius: 10px;
    }}

    /* ---------- 分隔线 ---------- */
    hr {{
        border: none; height: 1px;
        background: linear-gradient(90deg, transparent, #c9a24b, transparent);
        margin: 30px 0;
    }}

    /* ---------- 数据表格 ---------- */
    [data-testid="stDataFrame"] {{
        border: 1px solid rgba(201,162,75,0.4);
        border-radius: 10px;
        overflow: hidden;
    }}

    /* ---------- 图表容器：半透明暗底 ---------- */
    [data-testid="stPlotlyChart"], [data-testid="stPydeckChart"] {{
        background: rgba(26,4,4,0.55);
        border: 1px solid rgba(201,162,75,0.35);
        border-radius: 12px;
        padding: 6px;
    }}

    /* ---------- 滚动条 ---------- */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: #2a0707; }}
    ::-webkit-scrollbar-thumb {{ background: #8a6d2f; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #c9a24b; }}
</style>
""", unsafe_allow_html=True)

# ========== 标题 ==========
st.markdown(
    '<div class="title-divider"><div class="line"></div>🏮<div class="line"></div></div>',
    unsafe_allow_html=True
)
st.markdown('<p class="lantern-title">灯 映 金 陵</p>', unsafe_allow_html=True)
st.markdown('<p class="lantern-subtitle">秦淮灯会 · 时空交互式可视化系统</p>', unsafe_allow_html=True)
st.markdown(
    '<div class="title-divider"><div class="line"></div>✦<div class="line"></div></div>',
    unsafe_allow_html=True
)

# 1.灯会空间点位数据 df_place（史实地点，坐标公开地理点位）
place_data = [
    {"点位": "夫子庙", "朝代": "明代至今", "特色": "秦淮灯会核心主会场，大成殿、江南贡院常设大型灯组", "lon": 118.780,
     "lat": 32.021, "era_tag": "ancient"},
    {"点位": "老门东", "朝代": "当代复兴（2010年后）", "特色": "城南古巷，民俗花灯市集、小型手工灯彩展示", "lon": 118.778,
     "lat": 32.015, "era_tag": "modern"},
    {"点位": "白鹭洲公园", "朝代": "明清延续至今", "特色": "秦淮河水上灯组集中展示区，水上灯会主要举办地",
     "lon": 118.784, "lat": 32.017, "era_tag": "ancient"},
    {"点位": "朝天宫", "朝代": "明清", "特色": "江南规模最大官式古建筑群，古代官办元宵赏灯活动所在地", "lon": 118.770,
     "lat": 32.041, "era_tag": "ancient"},
    {"点位": "十里秦淮河", "朝代": "南朝起源", "特色": "史料记载最早秦淮灯船游赏活动，灯会文化源头", "lon": 118.782,
     "lat": 32.019, "era_tag": "ancient"},
]
df_place = pd.DataFrame(place_data)

# 2.灯会历史兴衰时序数据 df_history
history_data = [
    {"时期": "南朝", "事件": "秦淮河出现灯船夜游，秦淮灯会文化雏形形成", "兴盛度": 25, "era_tag": "ancient"},
    {"时期": "隋唐", "事件": "元宵赏灯风俗普及江南，民间自制花灯广为流行", "兴盛度": 42, "era_tag": "ancient"},
    {"时期": "明代", "事件": "金陵元宵灯会达到历史顶峰，“天下第一灯会”史料记载", "兴盛度": 96, "era_tag": "ancient"},
    {"时期": "清代", "事件": "承袭明代灯会习俗，秦淮河灯船游乐持续繁盛，后期受战乱冲击衰落", "兴盛度": 72,
     "era_tag": "ancient"},
    {"时期": "民国", "事件": "连年战乱，民间灯彩传承萎缩，大规模灯会基本停办", "兴盛度": 28, "era_tag": "ancient"},
    {"时期": "1985", "事件": "南京恢复举办夫子庙元宵灯会，抢救保护灯彩非遗技艺", "兴盛度": 51, "era_tag": "modern"},
    {"时期": "2006", "事件": "秦淮灯会列入第一批国家级非物质文化遗产代表性项目", "兴盛度": 70, "era_tag": "modern"},
    {"时期": "2024", "事件": "秦淮灯会持续出圈，成为南京标志性文旅IP，多地设分会场", "兴盛度": 89, "era_tag": "modern"},
]
df_history = pd.DataFrame(history_data)

# 3.灯彩桑基图数据 sankey_data
sankey_data = {
    "source": ["传统灯彩", "传统灯彩", "传统灯彩", "现代创意灯", "现代创意灯"],
    "target": ["荷花灯", "兔子灯", "走马灯", "大型龙灯装置", "光影灯组"],
    "value": [30, 24, 16, 18, 12]
}

# 4.历年客流数据 df_visitor（单位：万人次）
visitor_data = [
    {"年份": 2015, "游客量": 420},
    {"年份": 2017, "游客量": 540},
    {"年份": 2019, "游客量": 630},
    {"年份": 2023, "游客量": 680},
    {"年份": 2024, "游客量": 780},
]
df_visitor = pd.DataFrame(visitor_data)

# ========== 侧边栏交互筛选 ==========
st.sidebar.header("🏮 交互控制面板")

# 返回首页按钮
if st.sidebar.button("🏠 返回首页"):
    st.session_state.page = "home"
    st.rerun()

st.sidebar.divider()

period_options = ["全部", "古代（南朝‑明清）", "近现代（1985至今）"]
sel_period = st.sidebar.selectbox("时期筛选", period_options)

# --------------------------
# 筛选逻辑（保持不变）
# --------------------------
if sel_period == "全部":
    filter_place = df_place.copy()
    filter_history = df_history.copy()
elif sel_period == "古代（南朝‑明清）":
    filter_place = df_place[df_place["era_tag"] == "ancient"].copy()
    filter_history = df_history[df_history["era_tag"] == "ancient"].copy()
elif sel_period == "近现代（1985至今）":
    filter_place = df_place[df_place["era_tag"] == "modern"].copy()
    filter_history = df_history[df_history["era_tag"] == "modern"].copy()

st.sidebar.markdown(f"**当前筛选：{sel_period}**")
st.sidebar.info(f"点位数量：{len(filter_place)} 个")


time_scroll_reel()


# ========== 1. 空间点位分布地图【pydeck 交互式地图】 ==========
st.subheader("🗺️ 秦淮灯会空间点位分布地图")

layer = pdk.Layer(
    "ScatterplotLayer",
    filter_place,
    get_position=["lon", "lat"],
    get_radius=200,
    get_fill_color=[255, 90, 40, 200],  # 灯笼橙红
    get_line_color=[255, 215, 120, 255],  # 金边描摹
    line_width_min_pixels=2,
    pickable=True,
)

view_state = pdk.ViewState(
    latitude=32.021,
    longitude=118.780,
    zoom=12,
    pitch=0
)

tooltip = {
    "html": """
    <b>点位：{点位}</b><br/>
    朝代：{朝代}<br/>
    特色：{特色}
    """,
    "style": {"backgroundColor": "#2a0707", "color": "#ffd977"}
}

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip=tooltip,
    map_style="dark"  # 暗色底图更衬红金灯火
)
st.pydeck_chart(r)

# ========== 2. 左右双栏：历史兴衰图 + 桑基图 ==========
col1, col2 = st.columns(2)

_GOLD = "#ffd977"
_RED = "#e23b2e"

with col1:
    st.subheader("📜 秦淮灯会千年兴衰时间线")
    fig_history = px.line(
        filter_history,
        x="时期",
        y="兴盛度",
        markers=True,
        text="事件",
        color_discrete_sequence=[_GOLD],
        title=f"灯会千年兴衰演变【{sel_period}】"
    )
    fig_history.update_layout(
        yaxis_title="民俗兴盛程度",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f3e3c3"),
        title_font_color=_GOLD,
        xaxis=dict(gridcolor="rgba(201,162,75,0.25)", linecolor="rgba(201,162,75,0.4)"),
        yaxis=dict(gridcolor="rgba(201,162,75,0.25)", linecolor="rgba(201,162,75,0.4)"),
    )
    fig_history.update_traces(
        textposition="top center",
        textfont=dict(color="#f3e3c3", size=11),
        line=dict(width=3),
        marker=dict(size=10, color=_GOLD, line=dict(color=_RED, width=2)),
    )
    st.plotly_chart(fig_history, use_container_width=True)

with col2:
    st.subheader("🎨 灯彩品类流向桑基图")
    nodes = ["传统灯彩", "现代创意灯", "荷花灯", "兔子灯", "走马灯", "大型龙灯装置", "光影灯组"]
    node_colors = ["#c9a24b", "#a63a2e", "#e26d5a", "#f0a868", "#ffd977", "#d94f3d", "#b8452e"]
    fig_sankey = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="#ffd977", width=1),
            label=nodes,
            color=node_colors
        ),
        link=dict(
            source=[0, 0, 0, 1, 1],
            target=[2, 3, 4, 5, 6],
            value=sankey_data["value"],
            color="rgba(230,120,60,0.35)"
        )
    ))
    fig_sankey.update_layout(
        height=450,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f3e3c3"),
    )
    st.plotly_chart(fig_sankey, use_container_width=True)

# ========== 3. 灯会客流趋势图（客流都是现代数据，不做过滤） ==========
st.subheader("📈 近年秦淮灯会游客量变化（单位：万人次）")
fig_visitor = px.line(
    df_visitor,
    x="年份",
    y="游客量",
    markers=True,
    color_discrete_sequence=[_RED],
    title="夫子庙灯会历年接待游客数量"
)
fig_visitor.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#f3e3c3"),
    title_font_color=_GOLD,
    xaxis=dict(gridcolor="rgba(201,162,75,0.25)", linecolor="rgba(201,162,75,0.4)"),
    yaxis=dict(gridcolor="rgba(201,162,75,0.25)", linecolor="rgba(201,162,75,0.4)"),
)
fig_visitor.update_traces(
    line=dict(width=3),
    marker=dict(size=10, color=_GOLD, line=dict(color=_RED, width=2)),
)
st.plotly_chart(fig_visitor, use_container_width=True)

# ========== 4. 点位详情档案【美化增强交互版｜卡片+筛选+地图联动】 ==========
st.subheader("📖 灯会点位详细档案")

# 交互：点位朝代筛选标签
# 交互：点位朝代筛选标签 tag_options
tag_options = ["全部点位","南朝起源","明清","明代至今","当代复兴"]

# -------- 改动开始 --------
# 增加css强制横向，禁止换行
st.markdown("""
<style>
div[data-testid="stRadio"] div[role="radiogroup"]{
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    gap:12px !important;
    padding-bottom:6px;
}
div[data-testid="stRadio"] label {
    white-space: nowrap !important;
    flex-shrink: 0 !important;
    padding:4px 12px !important;
    border-radius:8px !important;
    border:1px solid rgba(201,162,75,0.4) !important;
    background:rgba(58,16,16,0.4) !important;
}
div[data-testid="stRadio"] input:checked + label {
    border-color:#ffd977 !important;
    background:rgba(255,170,50,0.2) !important;
}
</style>
""",unsafe_allow_html=True)

sel_tag = st.radio(
    "🏷️快速筛选点位",
    options=tag_options,
    horizontal=True,
    label_visibility="visible"
)
# -------- 改动结束 --------

# 根据标签筛选原始数据
if sel_tag == "全部点位":
    df_card = df_place.copy()   # ✔使用原始全量表，不要filter_place
elif sel_tag == "南朝起源":
    df_card = df_place[df_place["朝代"].str.contains("南朝")]
elif sel_tag == "明清":
    df_card = df_place[df_place["朝代"].str.contains("明清")]
elif sel_tag == "明代至今":
    df_card = df_place[df_place["朝代"].str.contains("明代至今")]
elif sel_tag == "当代复兴":
    df_card = df_place[df_place["朝代"].str.contains("当代复兴")]

# session存储选中点位，用于地图联动
if "selected_place" not in st.session_state:
    st.session_state.selected_place = None

# 生成点位标签样式（给每个点位打上功能小标签）
def get_point_tag(row):
    tags = []
    if "夫子庙" in row["点位"]:
        tags.append("主会场")
    if "白鹭洲" in row["点位"]:
        tags.append("水上灯会")
    if "朝天宫" in row["点位"]:
        tags.append("古建展区")
    if "十里秦淮河" in row["点位"]:
        tags.append("文化起源地")
    if "老门东" in row["点位"]:
        tags.append("民俗市集")
    return tags

# 构造卡片HTMLa
card_html = '''
<style>
.place-card-wrap{
    display:grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap:16px;
    margin-top:6px;
}
.point-card{
    background:linear-gradient(145deg, rgba(58,16,16,0.92), rgba(28,5,5,0.94));
    border:1px solid rgba(201,162,75,0.4);
    border-radius:14px;
    padding:18px;
    transition: all 0.3s ease;
    position:relative;
    cursor:pointer;
}
.point-card:hover{
    transform: translateY(-5px);
    border-color:#ffd977;
    box-shadow: 0 10px 26px rgba(255,160,40,0.32), inset 0 0 14px rgba(255,170,50,0.08);
}
.point-card.active-card{
    border:2px solid #ffd977;
    box-shadow: 0 0 20px rgba(255,180,60,0.45);
}
.card-title-row{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:10px;
}
.card-name{
    font-size:20px;
    font-family:"KaiTi",SimSun,serif;
    color:#ffd977;
    font-weight:bold;
    letter-spacing:2px;
}
.card-era{
    font-size:13px;
    color:#ffddbb;
    background:rgba(255,170,50,0.12);
    padding:2px 8px;
    border-radius:6px;
    border:1px solid rgba(201,162,75,0.35);
}
.tag-group{
    display:flex;
    gap:7px;
    margin:10px 0;
    flex-wrap:wrap;
}
.tag-item{
    font-size:12px;
    color:#ffe8bc;
    border:1px solid rgba(255,217,119,0.35);
    padding:2px 7px;
    border-radius:4px;
}
.card-desc{
    color:#f3e3c3;
    font-size:14px;
    line-height:1.65;
}
.card-footer-tip{
    margin-top:12px;
    font-size:12px;
    color:rgba(243,227,195,0.55);
}
</style>
<div class="place-card-wrap">
'''

for _,row in df_card.iterrows():
    tag_list = get_point_tag(row)
    tag_str = "".join([f'<span class="tag-item">{t}</span>' for t in tag_list])
    is_active = "active-card" if st.session_state.selected_place==row["点位"] else ""
    card_html += f'''
<div class="point-card {is_active}" onclick="window.parent.postMessage({{type:'placeClick',payload:'{row['点位']}'}},'*')">
    <div class="card-title-row">
        <div class="card-name">{row['点位']}</div>
        <div class="card-era">{row['朝代']}</div>
    </div>
    <div class="tag-group">
        {tag_str}
    </div>
    <div class="card-desc">{row['特色']}</div>
    <div class="card-footer-tip">👆点击卡片，地图定位到此点位</div>
</div>
'''
card_html += "</div>"

# 渲染卡片组件【修改此处高度、关闭内部滚动】
st.components.v1.html(card_html, height=360, scrolling=False)

# --- 接收卡片点击消息，写入session触发rerun，实现选中高亮
qp_place = st.query_params.get("place")
if qp_place is not None:
    st.session_state.selected_place = qp_place
    del st.query_params["place"]
    st.rerun()

listen_js = '''
<script>
window.addEventListener("message",function(e){
    if(e.data && e.data.type==="placeClick"){
        const p = new URLSearchParams(location.search);
        p.set("place", e.data.payload);
        location.search = p.toString();
    }
})
</script>
'''
st.components.v1.html(listen_js,height=0)

# ----------------------
# 【地图联动增强：如果选中点位，更新pydeck视角】
# ----------------------
if st.session_state.selected_place is not None:
    sel_p = df_place[df_place["点位"]==st.session_state.selected_place].iloc[0]
    st.info(f"📍已选中点位：**{sel_p['点位']}** —— 地图已自动定位，可查看弹窗详情")
    # 覆盖原来view_state，聚焦选中点位
    view_state = pdk.ViewState(
        latitude=sel_p["lat"],
        longitude=sel_p["lon"],
        zoom=14.2,
        pitch=0
    )
else:
    # 默认南京全局视角
    view_state = pdk.ViewState(
        latitude=32.021,
        longitude=118.780,
        zoom=12,
        pitch=0
    )

# ========== 答题模块【无SQLite版本｜国风UI重制】 ==========
# 题库数据（直接写在内存里）
quiz_bank = [
    {
        "id": 1,
        "question": "秦淮灯会被列入国家级非物质文化遗产是哪一年？",
        "opt_a": "1985",
        "opt_b": "2006",
        "opt_c": "2024",
        "answer": "2006",
        "analysis": "解析：2006年，秦淮灯会列入我国第一批国家级非物质文化遗产代表性项目名录。",
        "difficulty": "简单"
    },
    {
        "id": 2,
        "question": "秦淮灯会历史上的鼎盛时期是哪个朝代？",
        "opt_a": "南朝",
        "opt_b": "明代",
        "opt_c": "清代",
        "answer": "明代",
        "analysis": "解析：明代朱元璋定都南京，将元宵张灯延长至十夜，是古代灯会时长最长的时期，秦淮灯会达到顶峰。",
        "difficulty": "普通"
    },
    {
        "id": 3,
        "question": "史料记载秦淮河灯船夜游最早起源于？",
        "opt_a": "南朝",
        "opt_b": "隋唐",
        "opt_c": "民国",
        "answer": "南朝",
        "analysis": "解析：六朝建康时期秦淮河沿岸士族已经有上元张灯，是秦淮灯船游赏文化的源头。",
        "difficulty": "普通"
    },
    {
        "id": 4,
        "question": "明代南京元宵灯会一共持续多少个夜晚？",
        "opt_a": "3夜",
        "opt_b": "7夜",
        "opt_c": "10夜",
        "answer": "10夜",
        "analysis": "解析：明代正月初八上灯，正月十八落灯，前后共计十夜，为古代最长灯节。",
        "difficulty": "中等"
    },
    {
        "id": 5,
        "question": "梁简文帝哪篇赋描写了建康宫廷上元燃灯景象？",
        "opt_a": "《列灯赋》",
        "opt_b": "《灯赋》",
        "opt_c": "《上元赋》",
        "answer": "《列灯赋》",
        "analysis": "解析：梁简文帝萧纲《列灯赋》，现存最早描写南京上元张灯的文学作品。",
        "difficulty": "中等"
    },
    {
        "id": 6,
        "question": "下列哪一处不是清代金陵传统灯市？",
        "opt_a": "笪桥",
        "opt_b": "评事街",
        "opt_c": "老门东",
        "answer": "老门东",
        "analysis": "解析：清代灯市集中在笪桥、评事街；老门东是当代复兴的民俗市集。",
        "difficulty": "普通"
    },
    {
        "id": 7,
        "question": "哪一幅古画记录了明代南京元宵灯市的百态景象？",
        "opt_a": "《清明上河图》",
        "opt_b": "《上元灯彩图》",
        "opt_c": "《金陵图》",
        "answer": "《上元灯彩图》",
        "analysis": "解析：《上元灯彩图》真实描绘明代南京夫子庙、三山街一带元宵灯市繁华面貌。",
        "difficulty": "中等"
    },
    {
        "id": 8,
        "question": "秦淮灯彩里经典的传统花灯“兔子灯”主要盛行于？",
        "opt_a": "民间市井",
        "opt_b": "皇家宫廷",
        "opt_c": "寺庙道观",
        "answer": "民间市井",
        "analysis": "解析：兔子灯属于南京民间百姓喜爱的民俗灯彩，扎根市井百姓生活。",
        "difficulty": "简单"
    },
]

# 初始化session状态
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0
if "finished_qids" not in st.session_state:
    st.session_state.finished_qids = []
if "quiz_mode" not in st.session_state:
    st.session_state.quiz_mode = "order"  # order顺序 / random随机
if "quiz_start_time" not in st.session_state:
    st.session_state.quiz_start_time = None
if "quiz_records" not in st.session_state:
    st.session_state.quiz_records = []  # 存储答题记录，[{qid,user_select,is_right}]

# 答题模块CSS（适配你当前页面暗红+金边，和截图视觉统一）
quiz_css = '''
<style>
.quiz-container{
    width:100%;
    border: 2px solid #8a6d2f;
    border-radius:20px;
    background: linear-gradient(145deg, rgba(58,16,16,0.80), rgba(26,4,4,0.85));
    padding: 2rem;
}
.quiz-title{
    text-align:center;
    font-family: "KaiTi",SimSun,serif;
    font-size: 28px;
    color:#ffd977;
    letter-spacing: 6px;
    margin-bottom:1.2rem;
}
.quiz-header-row{
    display:flex;
    justify-content:space-between;
    color:#ffddbb;
    font-size:15px;
    margin-bottom:0.8rem;
}
.progress-wrap{
    width:100%;
    height:10px;
    background:rgba(201,162,75,0.15);
    border-radius: 10px;
    border:1px solid rgba(201,162,75,0.35);
    margin-bottom:1.5rem;
}
.progress-fill{
    height:100%;
    border-radius:10px;
    background:linear-gradient(90deg,#c9a24b,#ffd977);
}
.question-card{
    background:rgba(74,13,13,0.45);
    border:1px solid rgba(201,162,75,0.35);
    border-radius:14px;
    padding:1.5rem;
    margin-bottom:1.5rem;
}
.question-diff-tag{
    display:inline-block;
    padding:2px 8px;
    border-radius:6px;
    border:1px solid #ffd977;
    color:#ffd977;
    font-size:13px;
    margin-bottom:0.8rem;
}
.question-text{
    font-family:"KaiTi",SimSun,serif;
    font-size:20px;
    color:#ffddbb;
    line-height:1.7;
}
/* 美化单选框 */
div[data-testid="stRadio"] > label{display:none !important;}
div[data-testid="stRadio"] div[role="radiogroup"]{
    display:flex;
    flex-direction:column;
    gap:12px;
}
div[data-testid="stRadio"] label.st-eb{
    background:rgba(74,13,13,0.35);
    border:1px solid rgba(201,162,75,0.35);
    border-radius:10px;
    padding:14px 18px;
    color:#f3e3c3;
    font-size:16px;
    transition:0.25s ease;
}
div[data-testid="stRadio"] label.st-eb:hover{
    border-color:#ffd977;
    background:rgba(255,217,119,0.1);
}
div[data-testid="stRadio"] input:checked + label.st-eb{
    border:2px solid #ffd977;
    background:rgba(255,170,50,0.15);
    box-shadow: 0 0 12px rgba(255,170,50,0.3);
}
/* 按钮美化 */
.quiz-btn-area{
    display:flex;
    gap:1rem;
    margin-top:1.5rem;
}
.quiz-btn-area div[data-testid="stButton"] button{
    background:rgba(255,217,119,0.1);
    color:#ffd977;
    border:1px solid #c9a24b;
    border-radius:8px;
}
.quiz-btn-area div[data-testid="stButton"] button:hover{
    background:rgba(255,217,119,0.2);
}
.submit-btn div[data-testid="stButton"] button{
    background:linear-gradient(180deg,#ffd977,#d4a843);
    color:#4a0d0d;
    font-weight:bold;
}
/* 完成报告卡片 */
.report-card{
    background:rgba(74,13,13,0.45);
    border:2px solid #c9a24b;
    border-radius:16px;
    padding:2rem;
    text-align:center;
}
.report-title{
    font-family:"KaiTi",SimSun,serif;
    font-size:24px;
    color:#ffd977;
    letter-spacing:4px;
    margin-bottom:1rem;
}
.report-score{
    font-size:36px;
    color:#ffbc58;
    font-weight:bold;
    margin:0.8rem 0;
}
.wrong-item{
    background:rgba(42,7,7,0.5);
    border-left:3px solid #e23b2e;
    padding:12px;
    border-radius:8px;
    margin:8px 0;
    color:#ffddbb;
    text-align:left;
}
</style>
'''
st.markdown(quiz_css, unsafe_allow_html=True)

st.markdown("""
<style>
.title-box{
    border:2px solid #d4a843;
    border-radius:16px;
    padding:24px 16px;
    width:100%;
}
.title-text{
    text-align:center;
    font-size:32px;
    color:#ffdd77;
    margin:0;
}
</style>

<div class="title-box">
    <h2 class="title-text">🏮 秦淮灯会小答题 · 非遗知识自测 🏮</h2>
</div>
""",unsafe_allow_html=True)

# 模式选择
col_mode1, col_mode2 = st.columns([1,1])
with col_mode1:
    mode_sel = st.radio("答题模式",["顺序刷题","随机抽题"],horizontal=True)
    if mode_sel == "顺序刷题":
        st.session_state.quiz_mode = "order"
    else:
        st.session_state.quiz_mode = "random"

# 获取所有题目ID
all_qid = [item["id"] for item in quiz_bank]
unfinished = [qid for qid in all_qid if qid not in st.session_state.finished_qids]
total_num = len(all_qid)
done_num = len(st.session_state.finished_qids)
score = st.session_state.quiz_score

# 计时逻辑
if done_num == 0 and st.session_state.quiz_start_time is None:
    from datetime import datetime
    st.session_state.quiz_start_time = datetime.now()

used_time_str = ""
if st.session_state.quiz_start_time:
    from datetime import datetime
    time_delta = datetime.now() - st.session_state.quiz_start_time
    used_time_str = f"⏱答题用时：{time_delta.seconds//60}分{time_delta.seconds%60}秒"

# 进度栏
progress_ratio = done_num / total_num if total_num >0 else 0
st.markdown(f'''
<div class="quiz-header-row">
    <span>📖 已完成：{done_num}/{total_num}题｜✅得分：{score}</span>
    <span>{used_time_str}</span>
</div>
<div class="progress-wrap">
    <div class="progress-fill" style="width:{progress_ratio*100}%"></div>
</div>
''', unsafe_allow_html=True)

# 获取下一题函数
def get_next_question_id():
    if not unfinished:
        return None
    if st.session_state.quiz_mode == "random":
        import random
        return random.choice(unfinished)
    else:
        for qid in all_qid:
            if qid not in st.session_state.finished_qids:
                return qid
    return None

next_qid = get_next_question_id()

if next_qid is not None:
    # 找到当前题目
    current_question = next(item for item in quiz_bank if item["id"] == next_qid)
    q_text = current_question["question"]
    oa = current_question["opt_a"]
    ob = current_question["opt_b"]
    oc = current_question["opt_c"]
    real_ans = current_question["answer"]
    ana = current_question["analysis"]
    diff = current_question["difficulty"]

    st.markdown(f'''
    <div class="question-card">
        <span class="question-diff-tag">{diff}</span>
        <div class="question-text">❓ {q_text}</div>
    </div>
    ''', unsafe_allow_html=True)

    user_answer = st.radio("", options=[oa, ob, oc], key=f"quiz_{next_qid}")

    st.markdown('<div class="quiz-btn-area submit-btn">', unsafe_allow_html=True)
    if st.button("📝 提交本题答案"):
        is_right = 1 if user_answer == real_ans else 0
        # 存入答题记录
        st.session_state.quiz_records.append({
            "qid": next_qid,
            "user_select": user_answer,
            "is_right": is_right
        })
        st.session_state.finished_qids.append(next_qid)
        if is_right:
            st.success(f"🏮 答对啦！\n\n💡 {ana}")
            st.session_state.quiz_score += 1
        else:
            st.error(f"⚠️ 答错了。正确答案：**{real_ans}**\n\n💡 {ana}")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # 答题全部完成，生成报告卡片
    st.markdown('<div class="report-card">', unsafe_allow_html=True)
    st.markdown('<div class="report-title">🎉答题全部完成</div>', unsafe_allow_html=True)
    accuracy = (score / total_num *100) if total_num>0 else 0
    st.markdown(f'<div class="report-score">得分 {score}/{total_num}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:#f3e3c3; font-size:17px;">答题正确率：{accuracy:.1f}%</div>', unsafe_allow_html=True)

    # 评价文案
    if accuracy >= 85:
        eval_text = "🏆 灯火通晓，你已是秦淮灯会小行家！"
    elif accuracy >=60:
        eval_text = "✨ 略知灯俗，再多了解金陵灯会历史吧。"
    else:
        eval_text = "📜 尚需研读，欢迎翻阅上方历史时光卷轴。"
    st.markdown(f'<div style="color:#ffddbb; margin-top:0.8rem; font-size:16px;">{eval_text}</div>', unsafe_allow_html=True)

    # 错题列表
    wrong_records = [r for r in st.session_state.quiz_records if r["is_right"] == 0]
    if len(wrong_records) >0:
        st.markdown("#### 📖 你的错题回顾", unsafe_allow_html=True)
        for rec in wrong_records:
            q_item = next(item for item in quiz_bank if item["id"] == rec["qid"])
            st.markdown(f'''
            <div class="wrong-item">
                题目：{q_item["question"]}<br/>
                你的选择：{rec["user_select"]}｜正确答案：{q_item["answer"]}
            </div>
            ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 底部功能按钮
st.markdown('<div class="quiz-btn-area">', unsafe_allow_html=True)
col_btn1, col_btn2 = st.columns([1,1])
with col_btn1:
    if st.button("🔁 重置本次答题"):
        st.session_state.quiz_score =0
        st.session_state.finished_qids = []
        st.session_state.quiz_start_time = None
        st.session_state.quiz_records = []
        st.rerun()
with col_btn2:
    if st.button("📋 查看全部答题记录"):
        if len(st.session_state.quiz_records) >0:
            for rec in st.session_state.quiz_records:
                q_item = next(item for item in quiz_bank if item["id"] == rec["qid"])
                mark = "✅" if rec["is_right"] else "❌"
                st.markdown(f"{mark} {q_item['question']}\n你的选择:{rec['user_select']}｜正确:{q_item['answer']}")
        else:
            st.info("暂无答题记录")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 底部数据说明
st.divider()
st.markdown("""
**📌 数据说明**
1. 点位、历史事件文字参考《南京地方志》、秦淮灯会国家级非物质文化遗产档案；
2. 「兴盛度」、桑基图权重为**基于非遗史料调研的相对评估指数，无官方标准化测量值**；
3. 游客量来源于南京文旅官方对外公开报道的灯会期间接待游客数据。
""")