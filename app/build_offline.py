# -*- coding: utf-8 -*-
"""
build_offline.py – Sinh file `shoebot_offline.html`: chatbot tra cứu chạy OFFLINE.

Không cần model AI, không cần internet: toàn bộ knowledge base được nhúng vào file
HTML và tìm kiếm bằng thuật toán từ khoá (BM25-ish đơn giản). Dùng làm:
  - công cụ tra cứu nhanh cho nhân viên bán hàng (mở bằng điện thoại/máy tính),
  - bản dự phòng khi chưa kịp fine-tune AI.

Chạy:
    python app/build_offline.py
    # -> app/shoebot_offline.html   (mở bằng trình duyệt bất kỳ)
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "data"))

from knowledge_base import (  # noqa: E402
    ALL_BRANDS, TECHS, SIZE_TABLE, ADIDAS_TABLE, ADIDAS_NOTE, KID_TABLE, KID_NOTE,
    FIT_NOTES, HOW_TO_MEASURE, SIZE_FAQ, GENERAL_FAQ, FAKE_CHECK_GENERAL, CARE, CARE_FAQ,
    TRENDS_2026, COMPARISONS, SCENARIOS, STORE_POLICY, CROSS_SELL,
)


def build_docs():
    docs = []

    def add(cat, title, text, tags=""):
        docs.append({"cat": cat, "title": title, "text": text, "tags": tags})

    for b in ALL_BRANDS:
        ten = b["ten"]
        add("Hãng", f"{ten} – nguồn gốc & định vị",
            f"{ten} là thương hiệu của {b['xuat_xu']}, thành lập năm {b['nam']}."
            + (f" Người sáng lập: {b['sang_lap']}." if b.get("sang_lap") else "")
            + f"\nĐịnh vị: {b['dinh_vi']}."
            + (f"\nKhẩu hiệu: {b['khau_hieu']}." if b.get("khau_hieu") else "")
            + (f"\nKhách mục tiêu: {b['khach']}." if b.get("khach") else ""),
            f"{ten} {b['id']} nguồn gốc nước nào thành lập")
        add("Giá", f"{ten} – khoảng giá", f"Khoảng giá sản phẩm {ten}: {b['gia']} (tham khảo).", f"{ten} giá bao nhiêu")
        add("Sản phẩm", f"{ten} – các dòng nổi bật",
            "Các dòng tiêu biểu:\n" + "\n".join(f"• {m['ten']}: {m['mo_ta']}" for m in b["mau_icon"]),
            f"{ten} dòng nào mẫu nào bán chạy")
        add("Tư vấn", f"{ten} – thế mạnh & điểm yếu",
            "Thế mạnh:\n" + "\n".join(f"• {x}" for x in b["manh"]) +
            "\nĐiểm cần biết:\n" + "\n".join(f"• {x}" for x in b["yeu"]),
            f"{ten} có tốt không nên mua")
        add("Size", f"{ten} – form & chọn size", b["form"],
            f"{ten} size form ôm rộng chân bè đúng size")
        if b.get("check"):
            add("Check chính hãng", f"{ten} – phân biệt thật/giả",
                "Cách kiểm tra:\n" + "\n".join(f"• {x}" for x in b["check"]),
                f"{ten} check real fake chính hãng phân biệt")
        for m in b["mau_icon"]:
            add("Mẫu giày", f"{m['ten']} ({ten})",
                f"{m['mo_ta']}\n• Ra mắt khoảng: {m['nam']}\n• Giá tham khảo: {m['gia']}"
                f"\n• Form/size: {m['form']}\n• Phù hợp: {m['phu_hop']}",
                f"{m['ten']} giá form phù hợp")

    for t in TECHS:
        add("Công nghệ", f"{t['ten']} ({t['hang']})",
            f"{t['mo_ta']}\n• Ưu điểm: {t['uu']}\n• Nhược điểm: {t['nhuoc']}"
            f"\n• Phù hợp: {t['phu_hop']}\n• So sánh: {t['so_sanh']}",
            f"{t['ten']} công nghệ đế đệm {t['loai']}")

    for gioi, rows in SIZE_TABLE.items():
        label = {"nam": "nam", "nu": "nữ", "tre_em": "trẻ em"}[gioi]
        txt = []
        for r in rows:
            if gioi == "tre_em":
                txt.append(f"• {r[0]:g}cm → US {r[1]} / EU {r[2]} ({r[3]})")
            else:
                txt.append(f"• {r[0]:g}cm → US nam {r[1]} | US nữ {r[2]} | UK {r[3]} | EU {r[4]}")
        add("Size", f"Bảng quy đổi size – {label}", "\n".join(txt),
            f"bảng size quy đổi cm us uk eu {label}")
    add("Size", "Cách đo chân & chọn size đúng", "\n".join(HOW_TO_MEASURE),
        "cách đo chân chọn size đi thử")

    for r in ADIDAS_TABLE["nam"]:
        add("Size", f"Adidas chân {r[0]:g} cm – size nào",
            f"Adidas (nam): chân {r[0]:g}cm ≈ US {r[1]} ≈ UK {r[2]} ≈ EU {r[3]}. {ADIDAS_NOTE}",
            f"adidas size {r[3]} chân {r[0]:g}cm hệ size 1/3 quy đổi")

    # Một mục cho MỖI mốc cm – trả lời rất nhanh câu "chân X cm đi size nào"
    for r in SIZE_TABLE["nam"]:
        cm = f"{r[0]:g}"
        add("Size", f"Chân {cm} cm – chọn size nào (nam)",
            f"Chân {cm}cm (≈ {cm} cm) tương đương:\n• US nam: {r[1]}\n• UK: {r[3]}\n• EU: {r[4]}\n"
            f"• US nữ tương đương: {r[2]}\nGợi ý: cộng thêm 0.5–1cm khi chọn lòng giày; nếu chân bè hoặc mẫu ôm "
            f"ngang thì lên thêm nửa size. Giày chạy nên dư 1–1.5cm.",
            f"chân {cm}cm {cm} cm size nam us uk eu quy đổi")
    for r in SIZE_TABLE["nu"]:
        cm = f"{r[0]:g}"
        add("Size", f"Chân {cm} cm – chọn size nào (nữ)",
            f"Chân {cm}cm tương đương:\n• US nữ: {r[2]}\n• US nam (unisex): {r[1]}\n• EU: {r[4]}\n"
            f"• UK: {r[3]}\nLưu ý: size nữ ≈ size nam + 1.5 khi mua giày unisex.",
            f"chân {cm}cm {cm} cm size nữ us eu quy đổi")
    for r in KID_TABLE:
        cm = f"{r[0]:g}"
        add("Size", f"Chân bé {cm} cm – chọn size nào",
            f"Chân bé {cm}cm tương đương size trẻ em US {r[1]} / EU {r[2]} (khoảng {r[3]}). {KID_NOTE}",
            f"chân bé {cm}cm {cm} cm size trẻ em trẻ nhỏ em bé")
    add("Size", "Bảng size trẻ em (quy đổi cm – US – EU – tuổi)",
        "\n".join(f"• {r[0]:g}cm → US {r[1]} / EU {r[2]} (khoảng {r[3]} tuổi)" for r in KID_TABLE) + "\n" + KID_NOTE,
        "bảng size trẻ em bé cm us eu tuổi")

    # Mốc cm tròn (những số khách hay nói) – suy ra từ bảng nam/nữ
    for target in (22, 23, 24, 25, 26, 27, 28):
        near = sorted(SIZE_TABLE["nam"], key=lambda r: abs(r[0] - target))[:2]
        near = sorted(near, key=lambda r: r[0])
        lo, hi = near[0], near[-1]
        add("Size", f"Chân {target} cm – chọn size nào",
            f"Chân khoảng {target}cm thì rơi vào vùng:\n• EU {lo[4]} – {hi[4]}\n• US nam {lo[1]} – {hi[1]}\n"
            f"• UK {lo[3]} – {hi[3]}\n• US nữ tương đương {lo[2]} – {hi[2]}\n"
            f"Nếu chân đúng {target}cm: chọn EU {hi[4]} cho thoải mái (hoặc EU {lo[4]} nếu chân thon). "
            f"Nguyên tắc: đo cuối buổi chiều, còn dư ~1cm ở mũi là vừa.",
            f"chân {target}cm {target} cm size bao nhiêu nam nữ quy đổi us eu uk")

    add("Size", "Chân bè / chân bẹt – nên chọn giày nào",
        "Chân bè nên ưu tiên:\n"
        "• New Balance có size bề ngang D/2E/4E (lựa chọn chuẩn nhất)\n"
        "• Nike Air Force 1, Air Max 1 (mũi rộng) – nhưng Dunk/Air Max hơi hẹp\n"
        "• Asics, Mizuno (form châu Á), Brooks (form Mỹ rộng)\n"
        "• Với dòng hẹp ngang (Samba, Gazelle, Speedcat, Dunk): tăng 0.5–1 size\n"
        "• Chân bẹt khi chạy nên chọn giày ổn định: Asics GEL-Kayano / GT-2000, "
        "Brooks Adrenaline GTS, Hoka Arahi, New Balance 860",
        "chân bè chân bẹt bề ngang 2E 4E nên chọn giày nào")
    for it in SIZE_FAQ:
        add("Size", it["q"], it["a"], "size " + it["q"])

    for it in GENERAL_FAQ:
        add("Hỏi đáp", it["q"], it["a"], it["q"])
    _mat = {"da_thật": "da thật", "da_lộn_suede": "da lộn / suede", "canvas_vải": "vải canvas",
            "luoi_mesh_knit": "lưới / mesh / knit", "cao_su_eva": "cao su / EVA"}
    for key, steps in CARE.items():
        nm = _mat.get(key, key)
        add("Vệ sinh", f"Vệ sinh giày {nm}", "\n".join(f"• {x}" for x in steps),
            f"vệ sinh bảo quản {nm} cách làm sạch")
    for it in CARE_FAQ:
        add("Vệ sinh", it["q"], it["a"], "vệ sinh " + it["q"])
    add("Check chính hãng", "Quy trình check hàng chính hãng",
        "\n".join(f"• {x}" for x in FAKE_CHECK_GENERAL),
        "quy trình check real fake chính hãng dấu hiệu cảnh báo tem mã")
    add("Xu hướng", "Xu hướng giày 2026", "\n".join(f"• {x}" for x in TRENDS_2026),
        "xu hướng hot trend bán chạy 2026 mẫu hot")

    for c in COMPARISONS:
        add("So sánh", f"{c['a']} vs {c['b']}", c["text"],
            f"{c['a']} {c['b']} nên mua cái nào so sánh khác nhau")

    for sc in SCENARIOS:
        add("Tình huống bán hàng", sc["ten"], sc["xu_ly"], sc["ten"] + " xử lý tư vấn khách")
    for p_ in STORE_POLICY:
        k = p_.split(":")[0]
        add("Chính sách shop", k, p_, "chính sách " + k.lower() + " bảo hành đổi trả vận chuyển")
    add("Tình huống bán hàng", "Gợi ý bán kèm (cross-sell)", "\n".join(f"• {x}" for x in CROSS_SELL),
        "bán kèm cross sell tư vấn thêm")
    return docs


HTML = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ShoeBot Offline – Tra cứu nhanh các hãng giày</title>
<style>
  :root{--bg:#0f1115;--card:#171a21;--line:#242833;--txt:#e8ecf3;--muted:#93a0b4;--accent:#4da3ff;--accent2:#1f6feb}
  *{box-sizing:border-box}
  body{margin:0;background:linear-gradient(180deg,#0f1115,#12161d 60%);color:var(--txt);
       font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
  .wrap{max-width:900px;margin:0 auto;padding:18px 14px 90px}
  header{display:flex;align-items:center;gap:12px;margin-bottom:6px}
  .logo{width:42px;height:42px;border-radius:12px;background:linear-gradient(135deg,var(--accent),#7b61ff);
        display:flex;align-items:center;justify-content:center;font-size:22px}
  h1{font-size:19px;margin:0}
  .sub{color:var(--muted);font-size:13px;margin:2px 0 14px}
  .chips{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 16px}
  .chip{background:var(--card);border:1px solid var(--line);color:var(--txt);padding:7px 12px;
        border-radius:999px;font-size:13px;cursor:pointer;transition:.15s}
  .chip:hover{border-color:var(--accent);color:var(--accent)}
  #log{display:flex;flex-direction:column;gap:12px}
  .msg{max-width:88%;padding:12px 14px;border-radius:14px;white-space:pre-wrap;line-height:1.5;font-size:14.5px}
  .me{align-self:flex-end;background:var(--accent2);border-bottom-right-radius:4px}
  .bot{align-self:flex-start;background:var(--card);border:1px solid var(--line);border-bottom-left-radius:4px}
  .tag{display:inline-block;font-size:11px;color:var(--muted);border:1px solid var(--line);
       padding:1px 7px;border-radius:999px;margin-bottom:6px}
  .bar{position:fixed;left:0;right:0;bottom:0;background:#0f1115ee;border-top:1px solid var(--line);
       padding:10px 14px;backdrop-filter:blur(6px)}
  .barInner{max-width:900px;margin:0 auto;display:flex;gap:8px}
  input{flex:1;background:var(--card);border:1px solid var(--line);border-radius:12px;color:var(--txt);
        padding:12px 14px;font-size:15px;outline:none}
  input:focus{border-color:var(--accent)}
  button.go{background:var(--accent2);border:none;color:#fff;padding:12px 18px;border-radius:12px;
            font-size:15px;cursor:pointer;font-weight:600}
  .hint{color:var(--muted);font-size:12px;margin-top:8px;text-align:center}
  a{color:var(--accent)}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="logo">👟</div>
    <div>
      <h1>ShoeBot Offline – tra cứu nhanh các hãng giày</h1>
      <div class="sub">Bản tra cứu không cần internet &amp; không cần GPU (dữ liệu: __NDOCS__ mục, __NBRAND__ hãng)</div>
    </div>
  </header>

  <div class="chips" id="chips"></div>
  <div id="log"></div>
</div>

<div class="bar">
  <div class="barInner">
    <input id="q" placeholder="Ví dụ: chân 25cm đi size nào / Samba giá bao nhiêu / check Nike fake" autocomplete="off">
    <button class="go" onclick="send()">Hỏi</button>
  </div>
  <div class="hint">ShoeBot Offline trả lời theo dữ liệu có sẵn – giá chỉ mang tính tham khảo.</div>
</div>

<script>
const DOCS = __DATA__;

/* ---------- công cụ tìm kiếm từ khoá (tiếng Việt) ---------- */
function norm(s){return s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/đ/g,'d');}
const STOP = new Set(['la','cua','gi','thi','co','khong','cho','em','minh','shop','a','va','hay','nen','mua','muon',
  'hoi','can','duoc','bao','nhieu','the','nao','o','dau','k','nhu','voi','cac','nhung','mot','doi','giay','giup',
  'vay','toi','ban','xin','cam','on','ad','nha','ve','lai','ra','vao','khi','de','nay','kia','do','ma','bang','lam',
  'gia','tam','khoang']);
function tok(s){return norm(s).replace(/[^a-z0-9\\s]/g,' ').split(/\\s+/).filter(w=>w.length>1 && !STOP.has(w));}

const df = {};
DOCS.forEach(d=>{
  d._t = new Set(tok(d.title+' '+d.text+' '+d.tags));
  d._title = tok(d.title);
  const all = (d.title+' '+d.text+' '+d.tags);
  d._raw = all.toLowerCase();
  d._nums = (all.match(/\\d+(?:[.,]\\d+)?/g)||[]).map(x=>parseFloat(x.replace(',','.')));
});
DOCS.forEach(d=>{ d._t.forEach(w=>df[w]=(df[w]||0)+1); });
const N = DOCS.length;
const idf = w => Math.log(1 + N/(1+(df[w]||0)));

function search(q, k=3){
  const qt = tok(q);
  if(!qt.length) return [];
  const sc = DOCS.map(d=>{
    let s=0, hit=0;
    qt.forEach(w=>{
      if(d._t.has(w)){ s += idf(w); hit++; }
      else if([...d._t].some(x=>x.startsWith(w) && w.length>=4)){ s += idf(w)*0.6; hit+=0.6; }
    });
    d._title.forEach(w=>{ if(qt.includes(w)) s += idf(w)*0.8; });
    const phrase = norm(q);
    if(phrase.length>8 && norm(d.title).includes(phrase)) s += 3;
    // khớp số liệu (cm, size) – ví dụ "chân 25cm" khớp mục "Chân 25.4 cm"
    const qraw = q.toLowerCase();
    qraw.split(/\\s+/).forEach(w=>{
      // bỏ ký tự dấu câu ở hai đầu – không dùng regex Unicode để tương thích mọi trình duyệt
      let a=0, b=w.length;
      const isChar = ch => (ch.toLowerCase()!==ch.toUpperCase()) || (ch>='0'&&ch<='9');
      while(a<b && !isChar(w[a])) a++;
      while(b>a && !isChar(w[b-1])) b--;
      w = w.slice(a,b);
      if(w.length>=2 && d._raw.includes(w)) s += 1.2;
    });
    qt.forEach(w=>{
      const m = w.match(/^(\\d+(?:[.,]\\d+)?)(cm|mm)?$/);
      if(!m) return;
      const v = parseFloat(m[1].replace(',','.'));
      if(isNaN(v)) return;
      d._nums.forEach(n=>{
        if(Math.abs(n-v) <= 0.25){ s += 2.6; hit++; }
        else if(Math.abs(n-v) <= 0.6){ s += 1.0; hit++; }
      });
    });
    return {d, s, hit};
  }).filter(x=>x.hit>0).sort((a,b)=>b.s-a.s);
  return sc.slice(0,k);
}

/* ---------- hiển thị ---------- */
const log = document.getElementById('log');
const CHIPS = ["Chân 25cm đi size bao nhiêu?","Adidas Samba giá bao nhiêu?","Chân bè nên mua giày hãng nào?",
  "Cách check giày Nike thật giả?","Giày trắng bị ố vàng xử lý sao?","Chân bẹt nên chọn giày gì?",
  "Hoka Bondi vs Clifton?","Xu hướng giày 2026?"];
const chipsEl = document.getElementById('chips');
CHIPS.forEach(c=>{
  const b=document.createElement('button'); b.className='chip'; b.textContent=c;
  b.onclick=()=>{document.getElementById('q').value=c; send();};
  chipsEl.appendChild(b);
});

function bubble(text, who, tag){
  const div=document.createElement('div');
  div.className='msg '+(who==='me'?'me':'bot');
  if(tag){const t=document.createElement('div'); t.className='tag'; t.textContent=tag; div.appendChild(t);}
  const body=document.createElement('div'); body.textContent=text; div.appendChild(body);
  log.appendChild(div); window.scrollTo({top:document.body.scrollHeight,behavior:'smooth'});
}
function notice(){bubble("👋 Em chào anh/chị! Em là ShoeBot bản offline – tra cứu nhanh về các hãng giày: nguồn gốc, giá, mẫu hot, chọn size, check hàng thật/giả, vệ sinh & tình huống bán hàng.\\n\\nAnh/chị gõ câu hỏi hoặc bấm gợi ý bên trên nhé. (Giá chỉ mang tính tham khảo.)", 'bot');}
notice();

function send(){
  const inp=document.getElementById('q'); const q=inp.value.trim(); if(!q) return;
  bubble(q,'me'); inp.value='';
  const res=search(q,3);
  if(!res.length){
    bubble("Dạ em chưa tìm thấy dữ liệu cho câu này. Anh/chị thử hỏi theo từ khoá khác – ví dụ: 'Nike nguồn gốc', 'Samba giá', 'size chân bè', 'check Adidas fake', 'vệ sinh da lộn', 'chân bẹt giày gì' ạ.", 'bot');
    return;
  }
  const top=res[0];
  let out=top.d.text;
  if(res.length>1){
    const rel=res.slice(1).map(r=>'• '+r.d.title).join('\\n');
    out+='\\n\\n📎 Xem thêm:\\n'+rel;
  }
  bubble(out,'bot', top.d.cat+' · '+top.d.title);
}
document.getElementById('q').addEventListener('keydown',e=>{if(e.key==='Enter')send();});
</script>
</body>
</html>
"""


def main():
    docs = build_docs()
    html = (HTML
            .replace("__DATA__", json.dumps(docs, ensure_ascii=False))
            .replace("__NDOCS__", str(len(docs)))
            .replace("__NBRAND__", str(len(ALL_BRANDS))))
    out = os.path.join(HERE, "shoebot_offline.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    size_kb = os.path.getsize(out) / 1024
    print(f"[✓] Đã tạo {out} ({len(docs)} mục, {size_kb:.0f} KB) – mở bằng trình duyệt là dùng được ngay.")


if __name__ == "__main__":
    main()
