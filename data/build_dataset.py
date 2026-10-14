# -*- coding: utf-8 -*-
"""
build_dataset.py – Sinh dataset huấn luyện (chat JSONL) từ knowledge base.

Chạy:
    python data/build_dataset.py                       # xuất vào ../dataset
    python data/build_dataset.py --out dataset --seed 42 --val-ratio 0.05

Kết quả:
    dataset/train.jsonl, dataset/val.jsonl   (mỗi dòng: {"messages":[...], "category": "..."})
    dataset/build_report.md

Nguyên tắc: câu trả lời GROUNDED trong kb/*.py (sửa KB → dataset tự cập nhật).
Giọng điệu: trợ lý bán hàng giày Việt Nam — dạ/ạ, xưng 'em', gọi khách 'anh/chị', ngắn gọn, có bước tiếp theo.
Nhiều mẫu được sinh 2–3 biến thể câu trả lời để model học ngữ điệu, không học vẹt 1 câu.
"""

import argparse
import json
import os
import random
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from knowledge_base import (  # noqa: E402
    ALL_BRANDS, BRAND_BY_ID, GROUPS, TECHS, SIZE_TABLE, ADIDAS_TABLE, ADIDAS_NOTE, KID_TABLE, KID_NOTE,
    FIT_NOTES, HOW_TO_MEASURE, SIZE_FAQ, GENERAL_FAQ, FAKE_CHECK_GENERAL, COMPARISONS, CARE, CARE_FAQ,
    TRENDS_2026, SCENARIOS, STORE_POLICY, CROSS_SELL, all_models, LUXURY_IDS, VN_IDS,
)

rng = random.Random(42)

# ============================================================ PERSONA
SYSTEMS = [
    ("Bạn là ShoeBot – trợ lý bán hàng của một chuỗi bán lẻ giày/sneaker tại Việt Nam. "
     "Bạn am hiểu các hãng giày (thể thao, sneaker, hàng hiệu, giày Việt), công nghệ đế, cách chọn size, "
     "cách kiểm tra hàng chính hãng, vệ sinh – bảo quản giày. Trả lời ngắn gọn, thân thiện, xưng 'em', "
     "gọi khách là 'anh/chị', luôn đưa thông tin thực tế và gợi ý bước tiếp theo để chốt đơn."),
    ("Bạn là nhân viên tư vấn giày chuyên nghiệp của shop giày chính hãng tại Việt Nam. "
     "Khách hàng có thể là người mua lẫn nhân viên mới cần được hướng dẫn. Hãy tư vấn như một người bán hàng giỏi: "
     "hỏi đúng nhu cầu, trả lời theo dữ liệu thực (giá, size, form giày, cách check hàng), nói rõ khi giá chỉ là tham khảo, "
     "gợi ý thêm phụ kiện/chăm sóc khi phù hợp. Giọng dạ/ạ, gần gũi, không lan man."),
    ("Bạn là chuyên gia giày (shoe expert) kiêm tư vấn bán hàng tại Việt Nam. Bạn nắm rõ 40+ thương hiệu quốc tế và nội địa, "
     "hơn 100 mẫu giày, công nghệ đệm/đế, bảng size US–UK–EU–cm, mẹo phân biệt hàng thật – hàng giả và cách chăm sóc theo chất liệu. "
     "Khi trả lời: đi thẳng vào ý chính, số liệu cụ thể, xưng 'em', gọi khách 'anh/chị', kết thúc bằng câu hỏi hoặc gợi ý nhẹ để tiếp tục tư vấn."),
]

INTRO = ["", "", "Dạ, ", "Dạ em tư vấn ạ: ", "Dạ anh/chị tham khảo nhé: ", "Dạ vâng, "]
OUTRO = [
    "", "", "",
    " Anh/chị cần em gợi ý thêm mẫu nào cùng tầm giá không ạ?",
    " Anh/chị cho em số cm chân để em chốt size luôn nhé.",
    " Nếu anh/chị muốn, em gửi luôn vài mẫu tương tự đang có sẵn size ạ.",
    " Anh/chị cứ để lại nhu cầu, em lọc mẫu phù hợp ngay ạ.",
]
PRICE_NOTE = "(giá chỉ mang tính tham khảo, anh/chị xác nhận lại tại shop nhé)"


# ============================================================ TIỆN ÍCH
def rnd(seq):
    return rng.choice(list(seq))


def clean_text(a: str) -> str:
    """Dọn lỗi nhỏ: dấu chấm đôi, khoảng trắng thừa, khoảng trắng trước dấu câu."""
    a = a.replace("...", "\u00a7").replace("..", ".").replace("\u00a7", "...")
    a = a.replace(" .", ".").replace(" ,", ",").replace("  ", " ")
    return a.strip()


def decorate(answer: str) -> str:
    """Thêm mở đầu/kết thúc biến thể (KHÔNG đổi chữ hoa/thường của nội dung)."""
    a = clean_text(answer)
    if rng.random() < 0.35 and not a.startswith(("Dạ", "Chào", "Vâng")):
        a = rnd(["Dạ, ", "Dạ em tư vấn ạ: ", "Dạ vâng, "]) + a
    if rng.random() < 0.3:
        a = clean_text(a + rnd(OUTRO))
    return a


def parse_prices(s: str):
    """Trích khoảng giá (VND) từ chuỗi kiểu '2.6–3.2 triệu', '950k–1.4 triệu'."""
    if not s:
        return None
    t = s.lower().replace('≈', ' ').replace('~', ' ')
    vals = []
    for m in re.finditer(r'(\d+(?:[.,]\d+)?)\s*(triệu|tr\b)', t):
        vals.append(float(m.group(1).replace(',', '.')) * 1_000_000)
    for m in re.finditer(r'(\d+(?:[.,]\d+)?)\s*(k\b|nghìn|ngàn)', t):
        vals.append(float(m.group(1).replace(',', '.')) * 1_000)
    if not vals:
        return None
    return min(vals), max(vals)


MODELS = all_models()
MODELS_WITH_PRICE = [(b, m) for b, m in MODELS if parse_prices(m.get('gia', ''))]


def find_models_in_budget(lo, hi, limit=6):
    out = []
    for b, m in MODELS_WITH_PRICE:
        pr = parse_prices(m.get('gia', ''))
        if pr and pr[0] <= hi and pr[1] >= lo:
            out.append((b, m))
    rng.shuffle(out)
    return out[:limit]


# Nhu cầu thường gặp → mẫu gợi ý (tên mẫu + hãng + lý do, grounded với KB)
NEED_MAP = [
    ("đi mưa nhiều", [("Crocs", "Classic Clog", "nhựa rửa nước được, khô nhanh"),
                      ("Dr. Martens", "1460", "đế AirWair kín, da chống nước tốt"),
                      ("Salomon", "XT-6 GORE-TEX", "màng chống nước, bám tốt đường trơn")]),
    ("đứng nhiều cả ngày", [("Hoka", "Bondi 9", "đệm dày êm nhất phân khúc, giảm áp lực chân"),
                            ("New Balance", "1080v14", "Fresh Foam X êm, có bản bề ngang 2E"),
                            ("Skechers", "GOwalk 7", "nhẹ, Memory Foam, giá dễ chịu")]),
    ("chân bè", [("New Balance", "574 (bản 2E/4E)", "hãng có size bề ngang rộng chuẩn"),
                 ("Asics", "Gel-Nimbus 26", "form châu Á, mũi rộng vừa"),
                 ("Adidas", "Superstar", "mũi vỏ sò rộng, dễ chịu cho chân bè")]),
    ("chân bẹt / lật vào", [("Asics", "Gel-Kayano 31", "dòng ổn định 4D Guidance hỗ trợ chân lật vào"),
                            ("Brooks", "Adrenaline GTS 24", "GuideRails mềm mà vẫn ổn định"),
                            ("Hoka", "Arahi 8", "J-Frame cho chân bẹt kèm đệm êm")]),
    ("chạy bộ người mới", [("Nike", "Pegasus 41", "đôi chạy quốc dân, bền, dễ chọn size"),
                           ("Asics", "GT-2000 13", "ổn định phổ thông, giá vừa"),
                           ("Mizuno", "Wave Rider 28", "bền, form châu Á")]),
    ("chạy bộ tốc độ / race", [("Adidas", "Adizero (Boston 12 / Adios Pro)", "Lightstrike Pro + thanh carbon"),
                               ("Saucony", "Endorphin Speed 4", "PWRRUN PB + plate nylon, giá tốt nhất phân khúc"),
                               ("Hoka", "Mach X 2", "đệm nhanh nhẹn cho tempo")]),
    ("tập gym / tập tạ", [("Reebok", "Nano X4", "đế phẳng vững cho nâng tạ"),
                          ("Nike", "Metcon 9", "ổn định, bền cho HIIT"),
                          ("Adidas", "Dropset 3", "chắc chân khi tập chân")]),
    ("đi học, sinh viên", [("Biti's", "Hunter X", "nhẹ, êm, dưới 1 triệu"),
                           ("Ananas", "Basas", "đế lưu hoá bền, giá sinh viên"),
                           ("Converse", "Chuck Taylor All Star", "form retro, dễ phối đồ")]),
    ("đi làm văn phòng (lịch sự)", [("Adidas", "Stan Smith / Superstar", "trắng sạch, tối giản"),
                                    ("New Balance", "574 / 550", "vừa thanh lịch vừa êm"),
                                    ("Clarks", "Desert Boot", "da lộn, form tối giản sang")]),
    ("tặng quà / đôi đôi", [("New Balance", "550", "màu dễ phối, ai cũng dùng được"),
                            ("Nike", "Air Force 1 trắng", "món quà 'an toàn' nhất"),
                            ("Coach", "Lowline / Soho", "tầm trung sang, hợp quà tặng")]),
    ("người lớn tuổi đi bộ", [("Skechers", "Slip-ins / GOwalk", "xỏ không cần cúi, êm, nhẹ"),
                              ("New Balance", "1080 (bản 2E)", "êm tối đa, bề ngang rộng"),
                              ("Biti's", "Hunter X", "nhẹ, giá tốt, dễ mua thay thế")]),
    ("đi biển / đi du lịch", [("Crocs", "All-Terrain Clog", "quai gót chắc, đi nước được"),
                              ("Birkenstock", "Arizona EVA", "nhẹ, chống nước, mát chân"),
                              ("Salomon", "RX Moc", "dép phục hồi êm, đi dạo tốt")]),
]



# So sánh hãng với hãng (khách hay hỏi)
BRAND_VS = [
    ("Nike", "Adidas", "Nike mạnh về chất liệu kể chuyện + độ hot (AF1, Dunk, Jordan) và đệm Air/Zoom; Adidas mạnh về "
     "kỹ thuật chạy (Adizero) và thời trang tối giản (Samba, Gazelle, Stan Smith). Cùng phân khúc giá, chọn theo gu: "
     "thích icon đường phố → Nike; thích retro tối giản, 'sạch' → Adidas."),
    ("Nike", "New Balance", "Nike nghiêng về thể thao + streetwear đậm nét; New Balance nghiêng về đi bộ/dad shoe êm, "
     "bền và ĐẶC BIỆT có size bề ngang 2E/4E cho chân bè. Đi làm cả ngày, chân bè → NB; cần độ hot và nhiều lựa chọn → Nike."),
    ("Adidas", "Puma", "Đều là hãng Đức cùng gốc gia đình Dassler. Adidas phủ rộng hơn (chạy, bóng đá, thời trang), "
     "Puma đang lên về thời trang trẻ (Palermo, Speedcat) và giá thường tốt hơn chút. Nếu muốn khác biệt đám đông → Puma."),
    ("New Balance", "Asics", "Cùng nhóm êm & bền. Asics mạnh về chạy bộ/ổn định (Kayano, Nimbus, GT-2000) và form châu Á; "
     "NB mạnh về lifestyle + bề ngang rộng. Chạy nghiêm túc → Asics; đi bộ/đi làm, chân bè → NB."),
    ("Hoka", "On", "Cùng là giày đế dày 'đi êm'. Hoka đệm dày hơn, rẻ hơn chút, hợp đứng nhiều (Bondi/Clifton); "
     "On sang hơn, gu đi làm tốt hơn (Cloud 5, Cloudtilt) nhưng form NHỎ nên phải lên nửa size và giá cao hơn."),
    ("Hoka", "Asics", "Asics là chuyên gia chạy lâu năm với foam êm-bền (Nimbus/Kayano); Hoka nổi bật ở max-cushion đế dày "
     "và dòng trail (Speedgoat). Chạy đường nhựa hằng ngày → Asics; đi bộ/đứng nhiều và gu chunky → Hoka."),
    ("Brooks", "Saucony", "Hai 'chuyên gia chạy' ít đại chúng ở VN. Brooks có GuideRails cho chân lật vào, đệm bền; "
     "Saucony có Endorphin Speed (giá rất tốt cho chạy tempo) và PWRRUN êm. Chân bẹt → Brooks Adrenaline; chạy tốc độ → Saucony Endorphin."),
    ("Mizuno", "Asics", "Cùng gốc Nhật, form hợp chân châu Á. Mizuno mạnh về độ bền (Wave + X10) và giá tốt; "
     "Asics đa dạng hơn, nhiều công nghệ hơn và có dòng ổn định nổi tiếng (Kayano). Ưu tiên bền, giá vừa → Mizuno."),
    ("Nike", "Jordan", "Jordan là thương hiệu con của Nike, cùng công ty ạ. Jordan tập trung vào retro bóng rổ (AJ1–AJ4, "
     "giá cao, tính sưu tầm mạnh), Nike phủ rộng và dễ mua hơn. Muốn icon bóng rổ/đầu tư sưu tầm → Jordan; dùng hằng ngày → Nike."),
    ("Converse", "Vans", "Cùng nhóm canvas/skate cổ điển. Converse Chuck form cổ điển mũi cao su trắng, đế mỏng; "
     "Vans Old Skool bám tốt hơn (đế waffle) và ổn định hơn. Đi học phối đồ → cả hai; trượt ván/đi mưa nhẹ → Vans."),
    ("Crocs", "Birkenstock", "Crocs là EVA nhẹ, rẻ (1–1,6 triệu), đi mưa/đi biển tốt, không hỗ trợ vòm nhiều. "
     "Birkenstock là lót cork định hình vòm (2–5 triệu), tốt cho chân/gót nhưng không ngâm nước và cần 2–4 tuần làm quen."),
    ("Dr. Martens", "Timberland", "Cùng boot da bền. Dr. Martens nhẹ hơn, hợp đi phố/style; Timberland nubuck chống nước, "
     "đế lug bám địa hình, hợp leo trèo mùa lạnh nhưng nặng hơn. Đi mưa hằng ngày ở thành phố → 1460; đi rừng → Timberland."),
    ("Clarks", "Dr. Martens", "Clarks thanh lịch, nhẹ, hợp đi làm (Desert Boot/Wallabee); Dr. Martens cá tính, đế bền hơn "
     "nhưng nặng và cần 'phá giày'. Văn phòng lịch sự → Clarks; đi mưa/gu đường phố → Dr. Martens."),
    ("Salomon", "Merrell", "Đều là giày trail/hiking. Salomon mạnh về chạy trail tốc độ (Speedcross, XT-6) và trend gorpcore; "
     "Merrell Moab là lựa chọn hiking bình dân, êm, bền, giá dễ hơn. Hiking phổ thông → Moab; trail/địa hình khó → Salomon."),
    ("Gucci", "Louis Vuitton", "Cùng đỉnh luxury. Gucci thiết kế táo bạo hơn (logo GG, sọc Web), dễ nhận diện; "
     "LV tối giản sang và 'quyền lực' hơn (LV Trainer đang cực hot). Gucci giá thường dễ chịu hơn có mẫu 13–20 triệu, LV Trainer 30–40 triệu."),
    ("Gucci", "Prada", "Cùng luxury Ý. Gucci phô trương, nhiều logo; Prada tối giản kiểu 'quiet luxury' (America's Cup). "
     "Muốn được nhìn ra ngay → Gucci; muốn sang kín đáo → Prada."),
    ("Balenciaga", "Off-White", "Hai 'ông trùm' street luxury: Balenciaga (Triple S, Track) đế to, cá tính mạnh; "
     "Off-White (OOO, ODSY) nghiêng về hype + ziptie/dấu ngoặc. Cả hai nhiều fake, cần mua chỗ uy tín và giữ hoá đơn."),
    ("Golden Goose", "Alexander McQueen", "Cùng tầm 12–18 triệu. Golden Goose 'đế bẩn cố ý', da mềm, thoải mái; "
     "McQueen đế platform dày, tôn dáng, hợp chụp ảnh. Đi nhiều → Golden Goose; cần chiều cao/tạo dáng → McQueen."),
    ("Skechers", "Biti's", "Cùng nhóm 'êm, giá dễ chịu'. Skechers êm hơn (Memory Foam, Arch Fit) và có Slip-ins cho người lớn tuổi, "
     "giá 1,2–2,4 triệu. Biti's rẻ hơn hẳn (400k–1,5 triệu), nhẹ, phù hợp học sinh. Ngân sách quan trọng → Biti's; cần êm tối đa → Skechers."),
    ("Biti's", "Ananas", "Cùng giày Việt. Biti's mạnh về giày thể thao nhẹ, giá siêu dễ tiếp cận, phủ cửa hàng rộng; "
     "Ananas mạnh về sneaker canvas form retro, đế lưu hoá bền, 'chất' hơn về thời trang. Đi học/đi chơi trẻ trung → Ananas; đa dụng, tiết kiệm → Biti's."),
    ("MLB", "New Balance", "MLB (Big Ball Chunky) cực chunky, gu Hàn, đế to, chất liệu tổng hợp; "
     "New Balance 9060 cũng chunky nhưng êm hơn, bền hơn và ít lỗi mốt. Tôn dáng + gu Hàn → MLB; đi nhiều, cần êm → NB 9060."),
    ("Fila", "Skechers", "Fila (Disruptor) đế chunky, giá học sinh, chất liệu cơ bản; Skechers êm hơn nhiều (Max Cushioning/Arch Fit). "
     "Ngân sách dưới 1,5 triệu, cần form chunky → Fila; cần êm cho chân mỏi → Skechers."),
    ("Reebok", "Adidas", "Reebok Club C/Classic Leather tối giản trắng giá tốt (1,5–2,5 triệu), Nano tốt cho gym; "
     "Adidas phủ rộng hơn, hot hơn và công nghệ đệm đa dạng hơn. Muốn trắng sạch giá tốt → Reebok; muốn đúng trend → Adidas."),
    ("Under Armour", "Nike", "UA (HOVR, Curry) mạnh về hiệu năng gym/bóng rổ, chất lượng tốt, ít đại chúng; "
     "Nike phủ mọi phân khúc, dễ mua, nhiều mẫu. Tập gym/bóng rổ muốn khác biệt → UA; mọi thứ khác → Nike."),
]

# ============================================================ SINH DỮ LIỆU
def rows():
    R = []

    def add(category, user, assistant):
        R.append({
            "messages": [
                {"role": "system", "content": rnd(SYSTEMS)},
                {"role": "user", "content": user.strip()},
                {"role": "assistant", "content": decorate(assistant)},
            ],
            "category": category,
        })

    def add_variants(category, questions, answers):
        """Ghép nhiều câu hỏi × nhiều câu trả lời (mỗi tổ hợp 1 mẫu)."""
        for a in answers:
            add(category, rnd(questions), a)

    # ------------------------------------------------ 1. Nguồn gốc & tổng quan hãng
    for b in ALL_BRANDS:
        ten, xuat, nam = b['ten'], b['xuat_xu'], b['nam']
        add_variants("brand_origin",
                     [f"{ten} là thương hiệu của nước nào?",
                      f"Cho em hỏi hãng {ten} có nguồn gốc ở đâu ạ?",
                      f"{ten} của nước nào và thành lập năm bao nhiêu?",
                      f"Giới thiệu nhanh về nguồn gốc hãng {ten} giúp em"],
                     [f"{ten} là thương hiệu {xuat}, ra đời năm {nam}. {b.get('sang_lap','')} "
                      f"Định vị hiện tại: {b['dinh_vi']}",
                      f"Dạ {ten} đến từ {xuat} (từ năm {nam}). {b.get('sang_lap','')} "
                      f"Ngày nay {ten} được biết đến với vai trò: {b['dinh_vi']}"])

        add_variants("brand_overview",
                     [f"Hãng {ten} có gì đáng mua ạ?",
                      f"Tóm tắt về thương hiệu {ten} cho em với",
                      f"Định vị của {ten} trong phân khúc giày thế nào?",
                      f"Vì sao khách nên chọn {ten}?"],
                     [f"{ten} ({xuat}, từ {nam}): {b['dinh_vi']} Khoảng giá tại Việt Nam: {b['gia']}{PRICE_NOTE}. "
                      f"Điểm mạnh: " + "; ".join(b['manh']) + ".",
                      f"Dạ nói gọn về {ten}: {b['dinh_vi']} Giá bán tham khảo: {b['gia']}. "
                      f"Ưu điểm nổi bật: " + "; ".join(b['manh']) + ".",
                      f"{ten} mạnh ở: " + "; ".join(b['manh']) +
                      f". Khoảng giá: {b['gia']}." + (f" Khách của {ten} thường là: {b['khach']}" if b.get('khach') else "")])

        add_variants("brand_weakness",
                     [f"{ten} có nhược điểm gì không ạ?",
                      f"Nhược điểm của {ten} là gì?",
                      f"Có nên mua {ten} không hay chọn hãng khác?"],
                     [f"Dạ {ten} nhìn chung đáng mua ở phân khúc của hãng, nhưng có vài điểm anh/chị nên biết: " +
                      "; ".join(b['yeu']) + f". Bù lại, điểm mạnh là: " + "; ".join(b['manh']) + ".",
                      f"Dạ {ten} có mặt yếu cần cân nhắc: " + "; ".join(b['yeu']) +
                      f". Nếu anh/chị quan tâm độ bền/giá, em gợi ý thêm phương án khác để so sánh nhé."])

        if b.get('khach'):
            add("brand_customer",
                rnd([f"Ai thường mua {ten} ạ?", f"{ten} phù hợp với khách nào?",
                     f"Khách nào nên chọn {ten}?"]),
                f"Dạ khách của {ten} thường là: {b['khach']} Kèm theo, {ten} mạnh ở: " +
                "; ".join(b['manh']) + f". Anh/chị thuộc nhóm nào để em tư vấn sâu hơn ạ?")

    # ------------------------------------------------ 2. Danh mục mẫu giày của hãng
    for b in ALL_BRANDS:
        ms = b.get('mau_icon', [])
        if not ms:
            continue
        lines = "\n".join(f"• {m['ten']}: {m['mo_ta']} — giá {m['gia']}." for m in ms)
        add_variants("brand_models",
                     [f"{b['ten']} có những dòng giày nào nổi bật?",
                      f"Kể tên vài mẫu giày đáng chú ý của {b['ten']} giúp em",
                      f"Các mẫu giày bán chạy nhất của {b['ten']} là gì ạ?"],
                     [f"Dạ {b['ten']} có những mẫu tiêu biểu sau:\n{lines}\n"
                      f"Anh/chị quan tâm mẫu nào để em nói kỹ hơn (size, form, so sánh) ạ?",
                      f"Dạ các mẫu khách hỏi nhiều của {b['ten']}:\n{lines}\n"
                      f"Mẫu nào đúng gu anh/chị, em kiểm tra size và màu ngay ạ."])

    # ------------------------------------------------ 3. Thông tin từng mẫu giày
    for b, m in MODELS:
        name, hang = m['ten'], b['ten']
        add_variants("model_info",
                     [f"Cho em hỏi về đôi {name} của {hang}",
                      f"Đôi {name} ({hang}) thế nào ạ?",
                      f"Thông tin đôi {name} {hang} giúp em với",
                      f"{hang} {name} có gì đặc biệt?"],
                     [f"Dạ {name} ({hang}): {m['mo_ta']} Giá tham khảo {m['gia']} — {PRICE_NOTE}. "
                      f"Form: {m['form']}. Phù hợp: {m['phu_hop']}.",
                      f"Dạ về đôi {name} của {hang}: {m['mo_ta']} Giá khoảng {m['gia']}. "
                      f"Anh/chị lưu ý form giày: {m['form']} — nên thử hoặc cho em số cm chân ạ."])

        add("model_price",
            rnd([f"{name} giá bao nhiêu ạ?",
                 f"Đôi {name} của {hang} bán khoảng bao nhiêu?",
                 f"Giá đôi {name} ({hang}) hiện tại thế nào?",
                 f"{name} tầm bao nhiêu tiền ạ?"]),
            rnd([f"Dạ {name} ({hang}) có giá tham khảo {m['gia']}. {PRICE_NOTE}. "
                 f"Anh/chị cho em biết cần size gì và màu nào để em kiểm tra tồn kho nhé!",
                 f"Dạ giá đôi {name} khoảng {m['gia']}. Giá thay đổi theo đợt sale và màu, anh/chị cần em báo giá chính xác thì cho em size + màu ạ."]))

        add("model_fit",
            rnd([f"{name} đi có đúng size không ạ?",
                 f"Form đôi {name} chạy rộng hay nhỏ?",
                 f"Chân em bè thì {name} lấy size sao ạ?"]),
            rnd([f"Dạ về form của {name} ({hang}): {m['form']}. Lưu ý chung của hãng {hang}: {b['form']} "
                 f"Anh/chị cho em số cm chân, em quy đổi size chính xác nhất nhé.",
                 f"Dạ {name} có form: {m['form']}. {b['form']} Em khuyên anh/chị đo chân cuối ngày rồi gửi em số cm ạ."]))

        add("model_usecase",
            rnd([f"{name} có đi học/đi làm được không ạ?",
                 f"{name} phù hợp với nhu cầu gì?",
                 f"Em định mua {name} để {m['phu_hop'].split(',')[0].strip()} thì có ổn không?"]),
            f"Dạ {name} hợp nhất với: {m['phu_hop']}. {m['mo_ta']} "
            f"Nếu anh/chị dùng chủ yếu để đi lại hằng ngày thì mẫu này rất ổn; còn cần chạy bộ hoặc leo núi em sẽ gợi ý dòng chuyên hơn ạ.")

    # ------------------------------------------------ 4. Form/size theo hãng
    for ten_hang, note in FIT_NOTES:
        add_variants("brand_fit",
                     [f"Form giày {ten_hang} thế nào ạ?",
                      f"Giày {ten_hang} đi size thế nào so với size thường?",
                      f"Em chân bè, mua {ten_hang} cần tăng size không?",
                      f"{ten_hang} nên lấy size nào cho chuẩn?"],
                     [f"Dạ về form của {ten_hang}: {note} Anh/chị cho em số cm chân để em chốt size chuẩn ạ.",
                      f"Dạ kinh nghiệm chọn size {ten_hang}: {note} Nếu anh/chị đang phân vân 2 size, gửi em số cm chân em tư vấn ngay."])

    # ------------------------------------------------ 5. Check chính hãng theo hãng
    for b in ALL_BRANDS:
        ck = b.get('check', [])
        if not ck:
            continue
        body = "\n".join(f"• {c}" for c in ck)
        add_variants("brand_authenticity",
                     [f"Cách phân biệt {b['ten']} thật và giả?",
                      f"Check giày {b['ten']} chính hãng thế nào ạ?",
                      f"Em mua {b['ten']} trên mạng, làm sao biết hàng thật?",
                      f"{b['ten']} fake và real khác nhau ở đâu?"],
                     [f"Dạ với {b['ten']}, anh/chị kiểm tra các điểm sau:\n{body}\n"
                      f"Nếu vẫn chưa chắc, anh/chị chụp rõ tem size, lưỡi giày, đế và hộp gửi em xem giúp nhé. "
                      f"Check qua ảnh được khoảng 80%, muốn chắc 100% nên cầm trực tiếp ạ.",
                      f"Dạ {b['ten']} có các dấu hiệu cần soi:\n{body}\n"
                      f"Mẹo nhanh: so cùng một lúc nhiều điểm — tem, mã, đường may, keo. Sai 1 điểm nhỏ chưa kết luận được, nhưng sai 2–3 điểm là nên nghi ngờ ạ."])

    # ------------------------------------------------ 6. Công nghệ giày
    for t in TECHS:
        add_variants("tech_info",
                     [f"{t['ten']} là gì ạ?",
                      f"Nghe nói {t['ten']} của {t['hang']} hay, giải thích giúp em",
                      f"Công nghệ {t['ten']} ({t['hang']}) hoạt động thế nào?",
                      f"{t['ten']} có đáng tiền không?"],
                     [f"Dạ {t['ten']} ({t['hang']}) – {t['loai']}: {t['mo_ta']} Ưu điểm: {t['uu']} "
                      f"Nhược điểm cần biết: {t['nhuoc']}",
                      f"Dạ em giải thích ngắn: {t['ten']} ({t['hang']}) là {t['loai'].lower()}. {t['mo_ta']} "
                      f"Điểm được: {t['uu']} Điểm chưa được: {t['nhuoc']}"])

        add("tech_advice",
            rnd([f"Nên chọn giày dùng {t['ten']} không?",
                 f"{t['ten']} phù hợp với ai ạ?",
                 f"Có nên trả tiền cho công nghệ {t['ten']} không?",
                 f"Ai nên mua giày có {t['ten']}?"]),
            rnd([f"Dạ {t['ten']} phù hợp nhất với: {t['phu_hop']} So sánh nhanh: {t['so_sanh']} "
                 f"Nếu nhu cầu của anh/chị khác (đi làm, đi bộ nhẹ), em gợi ý phương án tiết kiệm hơn ạ.",
                 f"Dạ nên chọn {t['ten']} nếu anh/chị thuộc nhóm: {t['phu_hop']} "
                 f"So với công nghệ tương đương: {t['so_sanh']}"]))

        add("tech_compare",
            rnd([f"{t['ten']} so với công nghệ khác thế nào?", f"{t['ten']} khác gì đối thủ?"]),
            f"Dạ {t['so_sanh']} Anh/chị đang cân nhắc giữa hai mẫu cụ thể nào không? Em so sánh trực tiếp đôi đó cho dễ quyết ạ.")

    # ------------------------------------------------ 7. Bảng size & quy đổi
    for cm, us_m, us_w, uk, eu in SIZE_TABLE['nam']:
        cm_s = f"{cm:g}".replace('.', ',')
        add_variants("size_convert",
                     [f"Chân {cm_s}cm đi giày size bao nhiêu ạ?",
                      f"Chân dài {cm_s}cm, nam, mua size mấy?",
                      f"Em đo chân được {cm_s}cm thì chọn size nào?"],
                     [f"Dạ chân {cm_s}cm tương đương US nam {us_m} ≈ UK {uk} ≈ EU {eu} (chuẩn Nike). "
                      f"US nữ tương đương {us_w}. Adidas dùng bảng 1/3 riêng, anh/chị nhớ so theo cm cho chắc ạ. "
                      f"Chân bè hoặc mẫu hẹp ngang thì lên nửa size; giày chạy nên dư 1–1,5cm.",
                      f"Dạ chân {cm_s}cm thì anh/chị lấy khoảng US {us_m} (nam) = UK {uk} = EU {eu}. "
                      f"Nữ tương ứng US {us_w}. Nếu chân bè hoặc mẫu ôm ngang, lên nửa size là an toàn nhất ạ."])

    for cm, us_w, us_m, uk, eu in SIZE_TABLE['nu']:
        cm_s = f"{cm:g}".replace('.', ',')
        add_variants("size_convert",
                     [f"Chân nữ {cm_s}cm đi size bao nhiêu ạ?",
                      f"Em là nữ, chân {cm_s}cm, chọn size gì?",
                      f"Chân {cm_s}cm thì size nữ là mấy?"],
                     [f"Dạ chân {cm_s}cm tương đương US nữ {us_w} ≈ UK {uk} ≈ EU {eu}; quy đổi sang size nam "
                      f"(giày unisex) khoảng US {us_m}. Mua giày unisex anh/chị lấy size nam tương ứng này nhé.",
                      f"Dạ chân nữ {cm_s}cm = US nữ {us_w} = EU {eu}. Nếu anh/chị mua mẫu unisex (size nam), "
                      f"lấy khoảng US {us_m} nam ạ."])

    for cm, us, uk, eu in ADIDAS_TABLE['nam']:
        cm_s = f"{cm:g}".replace('.', ',')
        add("size_convert",
            rnd([f"Adidas size {eu} tương đương bao nhiêu ạ?",
                 f"Chân {cm_s}cm mua Adidas size nào?",
                 f"Adidas dùng hệ size 1/3 là sao ạ?"]),
            f"Dạ Adidas dùng bước 1/3: chân {cm_s}cm ≈ US {us} ≈ UK {uk} ≈ EU {eu}. {ADIDAS_NOTE}")

    for cm, us, eu, tuoi in KID_TABLE:
        cm_s = f"{cm:g}".replace('.', ',')
        add("size_kids",
            rnd([f"Bé nhà em chân {cm_s}cm đi size nào ạ?",
                 f"Giày trẻ em {cm_s}cm là size mấy?",
                 f"Mua giày cho bé chân {cm_s}cm ({tuoi}) chọn size sao?"]),
            f"Dạ chân bé {cm_s}cm tương đương size trẻ em US {us} / EU {eu} (khoảng {tuoi}). {KID_NOTE}")

    for item in SIZE_FAQ:
        add("size_faq", rnd([item['q'], item['q'].replace('?', ' ạ?')]), item['a'])

    add_variants("size_guide",
                 ["Cách đo chân để chọn size giày đúng?",
                  "Hướng dẫn đo size giày tại nhà giúp em",
                  "Làm sao chọn size giày mà không cần thử?"],
                 ["Dạ anh/chị làm theo các bước sau:\n" + "\n".join(HOW_TO_MEASURE) +
                  "\nNếu vẫn lăn tăn giữa 2 size, anh/chị gửi em số cm để em tư vấn theo đúng mẫu định mua nhé.",
                  "Dạ nguyên tắc chọn size chuẩn nhất là dựa trên SỐ CM chân (không dựa vào size hãng khác). " +
                  " ".join(HOW_TO_MEASURE[:4]) + " Anh/chị gửi em số cm, em quy đổi sang đúng hãng đang mua ạ."])

    # ------------------------------------------------ 8. FAQ chung
    for item in GENERAL_FAQ:
        add("faq_sales", item['q'], item['a'])

    # ------------------------------------------------ 9. Check chính hãng chung
    add_variants("fakecheck_general",
                 ["Làm sao để không mua phải giày giả?",
                  "Mẹo check giày chính hãng nhanh nhất?",
                  "Cho em xin các bước check giày chính hãng với ạ",
                  "Check hàng thật hàng giả cần lưu ý gì?"],
                 ["Dạ anh/chị nắm các nguyên tắc sau:\n" + "\n".join(FAKE_CHECK_GENERAL) +
                  "\nNgoài ra em có thể check giúp anh/chị nếu gửi ảnh tem size, lưỡi giày và đế ạ.",
                  "Dạ em tóm lại 3 lớp kiểm tra: (1) giá – quá rẻ bất thường là rủi ro; (2) tem/mã sản phẩm phải khớp hộp và bill; "
                  "(3) hoàn thiện: đường may đều, keo gọn, mùi vật liệu tự nhiên. Cần soi kỹ hơn, anh/chị xem hướng dẫn chi tiết sau:\n" +
                  "\n".join(FAKE_CHECK_GENERAL[:6])])

    for tip in FAKE_CHECK_GENERAL:
        add("fakecheck_tip",
            rnd([f"Nghe nói '{tip[:45]}...' có đúng không ạ?",
                 "Check chính hãng cần chú ý gì nữa ạ?",
                 f"Có mẹo check nào riêng cho tip '{tip[:30]}...' không ạ?"]),
            f"Dạ đúng ạ – đây là một điểm quan trọng khi check: {tip} "
            f"Anh/chị kết hợp kiểm tra nhiều điểm cùng lúc, đừng chỉ dựa vào 1 chi tiết nhé.")

    # ------------------------------------------------ 10. So sánh các cặp giày
    for c in COMPARISONS:
        for qs, ans in [
            ([f"So sánh {c['a']} và {c['b']} giúp em",
              f"Nên mua {c['a']} hay {c['b']} ạ?",
              f"{c['a']} khác gì {c['b']}?"],
             [f"Dạ so sánh nhanh {c['a']} vs {c['b']}: {c['text']} "
              f"Anh/chị cho em biết sẽ dùng giày chủ yếu vào việc gì (đi làm, đi học, chạy bộ...) để em chốt giúp ạ.",
              f"Dạ hai đôi này khác nhau ở chỗ: {c['text']} Em nghiêng về đôi hợp nhu cầu của anh/chị hơn — nói em nhu cầu chính là em chọn luôn ạ."]),
            ([f"Em phân vân giữa {c['b']} và {c['a']}, chọn đôi nào?",
              f"Với ngân sách đủ mua 1 trong 2 thì nên lấy {c['b']} hay {c['a']}?",
              f"{c['b']} có hơn gì {c['a']} không ạ?"],
             [f"Dạ ngược lại cũng cùng câu chuyện: {c['text']} "
              f"Tóm gọn: chọn theo nhu cầu và cảm giác thử chân, còn nếu anh/chị muốn em chọn hộ thì nói em nhu cầu cụ thể nhé!",
              f"Dạ nếu để em chọn hộ, em cần biết: (1) dùng hằng ngày hay dịp đặc biệt; (2) ưu tiên êm hay form đẹp; (3) ngân sách. "
              f"Còn so sánh máy móc thì: {c['text']}"]),
        ]:
            add("comparison", rnd(qs), rnd(ans))

    # ------------------------------------------------ 11. Vệ sinh / chăm sóc
    mat_name = {"da_thật": "da thật", "da_lộn_suede": "da lộn/suede", "canvas_vải": "vải canvas",
                "luoi_mesh_knit": "lưới/mesh", "cao_su_eva": "cao su/EVA"}
    mat_q = {
        "da_thật": ["Giày da thật vệ sinh thế nào?", "Cách bảo dưỡng giày da ạ?", "Giày da bị bẩn lau bằng gì?"],
        "da_lộn_suede": ["Giày da lộn vệ sinh thế nào ạ?", "Suede dính bẩn xử lý ra sao?", "Bảo quản giày da lộn cần chú ý gì?"],
        "canvas_vải": ["Giày vải giặt được không ạ?", "Canvas bẩn thì vệ sinh sao?", "Giày canvas bị ố vàng phải làm sao?"],
        "luoi_mesh_knit": ["Giày lưới mesh giặt máy được không?", "Vệ sinh giày lưới thế nào ạ?", "Giày knit bị bẩn xử lý sao?"],
        "cao_su_eva": ["Giày cao su/nhựa vệ sinh sao ạ?", "Đế cao su bẩn thì làm gì?", "Giày EVA bị vàng xử lý thế nào?"],
    }
    for key, steps in CARE.items():
        body = "\n".join(f"• {s}" for s in steps)
        add_variants("care_material", mat_q.get(key, ["Vệ sinh loại giày này thế nào ạ?"]),
                     [f"Dạ với {mat_name.get(key,key)}:\n{body}\n"
                      f"Nếu anh/chị gửi ảnh tình trạng giày, em hướng dẫn xử lý cụ thể hơn nhé.",
                      f"Dạ chăm sóc {mat_name.get(key,key)} như sau:\n{body}\n"
                      f"Mẹo thêm: nên vệ sinh định kỳ thay vì để bẩn lâu — sạch dễ hơn tẩy ạ."])
    for item in CARE_FAQ:
        add("care_faq", item['q'], item['a'])

    # ------------------------------------------------ 12. Xu hướng
    add_variants("trends",
                 ["Xu hướng giày 2026 là gì ạ?", "Dạo này khách chọn giày theo xu hướng nào?",
                  "Mẫu giày nào đang trend năm nay?"],
                 ["Dạ các xu hướng giày 2025–2026 tại Việt Nam:\n" + "\n".join(f"• {t}" for t in TRENDS_2026) +
                  "\nAnh/chị muốn theo hướng nào (tối giản đi làm, retro, chunky hay giày Việt), em gợi ý mẫu cụ thể luôn ạ.",
                  "Dạ em tóm 3 xu hướng lớn nhất: " + "; ".join(t.split(':')[0].split('(')[0].strip() for t in TRENDS_2026[:3]) +
                  ". Chi tiết:\n" + "\n".join(f"• {t}" for t in TRENDS_2026[:5]) +
                  "\nAnh/chị thích hướng nào để em lọc mẫu đang có size ạ."])
    for t in TRENDS_2026:
        key = t.split(':')[0].split('(')[0].strip()
        add("trends_detail",
            rnd([f"Xu hướng '{key}' là sao ạ?", f"Năm nay có nên mua giày theo kiểu '{key}' không?",
                 f"'{key}' có phù hợp để đi làm không ạ?"]),
            f"Dạ đây là xu hướng đang lên: {t} Em có sẵn vài mẫu hợp xu hướng này, anh/chị xem thử không ạ?")

    # ------------------------------------------------ 13. Tình huống tư vấn
    for sc in SCENARIOS:
        add("scenario_staff",
            rnd([f"Tình huống: {sc['ten']}. Xử lý thế nào?",
                 f"Nếu gặp tình huống '{sc['ten']}' thì nên xử lý sao cho khéo?",
                 f"Hướng dẫn xử lý: {sc['ten']}"]),
            f"Dạ cách xử lý: {sc['xu_ly']} Nguyên tắc chung: luôn lắng nghe trước, xác nhận cảm nhận của khách, "
            f"rồi mới đưa giải pháp cụ thể và bước tiếp theo ạ.")

    # ------------------------------------------------ 14. Ngân sách
    BANDS = [("dưới 500k", 0, 500_000),
             ("500k–1 triệu", 500_000, 1_000_000),
             ("1–1,5 triệu", 1_000_000, 1_500_000),
             ("1,5–2 triệu", 1_500_000, 2_000_000),
             ("2–2,5 triệu", 2_000_000, 2_500_000),
             ("2,5–3 triệu", 2_500_000, 3_000_000),
             ("3–4 triệu", 3_000_000, 4_000_000),
             ("4–5 triệu", 4_000_000, 5_000_000),
             ("5–7 triệu", 5_000_000, 7_000_000),
             ("từ 10 triệu trở lên", 10_000_000, 100_000_000)]
    for label, lo, hi in BANDS:
        picks = find_models_in_budget(lo, hi, limit=5)
        if not picks:
            continue
        body = "\n".join(f"• {m['ten']} ({b['ten']}): {m['gia']} — phù hợp {m['phu_hop']}" for b, m in picks)
        add_variants("budget_advice",
                     [f"Ngân sách {label} thì mua giày gì ạ?",
                      f"Em có {label}, shop gợi ý mẫu nào?",
                      f"Tầm giá {label} có đôi nào đáng mua không?"],
                     [f"Dạ với ngân sách {label}, anh/chị tham khảo:\n{body}\n"
                      f"Nếu nói rõ nhu cầu (đi học, đi làm, chạy bộ, đi mưa...), em lọc còn 1–2 mẫu đúng nhất nhé.",
                      f"Dạ tầm {label} em có mấy phương án:\n{body}\n"
                      f"Anh/chị ưu tiên êm chân, bền hay đẹp để em chốt 1 đôi thôi ạ?"])

    # ------------------------------------------------ 15. Chính sách – bán kèm
    for p in STORE_POLICY:
        key = p.split(':')[0].replace('Chính sách ', '').strip()
        add("policy",
            rnd([f"Shop có chính sách {key.lower()} không?", f"Cho em hỏi về {key.lower()} của shop?",
                 f"{p.split(':')[0]} thế nào ạ?"]),
            rnd([f"Dạ {p} Anh/chị cần em hỗ trợ thêm phần nào không ạ?",
                 f"Dạ {p} Có gì chưa rõ anh/chị hỏi em ngay nhé."]))

    for ctx, sug in CROSS_SELL:
        add("cross_sell",
            rnd([f"Mua {ctx.lower()} thì có cần thêm gì không?", f"{ctx} nên dùng kèm gì ạ?",
                 f"Em mua giày rồi thì cần mua thêm gì để chăm sóc ạ?"]),
            f"Dạ với {ctx.lower()}, anh/chị nên dùng kèm: {sug} Nếu mua cùng bill, em xin phép gộp nhẹ giá cho anh/chị ạ.")

    # ------------------------------------------------ 16. Gợi ý theo nhu cầu (NEED_MAP)
    for need, lst in NEED_MAP:
        body = "\n".join(f"• {ten} {model}: {why}" for ten, model, why in lst)
        add_variants("need_advice",
                     [f"Em cần giày để {need}, gợi ý giúp em với",
                      f"Nhu cầu của em là {need} thì chọn giày nào ạ?",
                      f"Giày cho việc {need} nên mua đôi nào?"],
                     [f"Dạ với nhu cầu {need}, em gợi ý:\n{body}\n"
                      f"Anh/chị cho em ngân sách và số cm chân, em chốt đúng 1 đôi luôn ạ.",
                      f"Dạ nhu cầu {need} thì các lựa chọn hợp lý:\n{body}\n"
                      f"Nếu ngân sách còn eo hẹp, em có phương án rẻ hơn vẫn đáp ứng tốt, anh/chị muốn xem không ạ?"])

    # ------------------------------------------------ 17. Câu hỏi mơ hồ → hỏi lại (kỹ năng sale)
    VAGUE = [
        ("Em muốn mua giày", "Anh/chị cho em vài thông tin để tư vấn chuẩn ạ: (1) dùng để đi học/đi làm/chạy bộ/đi chơi? "
                             "(2) ngân sách khoảng bao nhiêu? (3) giới tính và số cm chân? Có 3 thông tin này là em lọc ra đúng 1 đôi cho anh/chị luôn."),
        ("Giày nào tốt nhất shop?", "Dạ 'tốt nhất' còn tuỳ nhu cầu ạ. Anh/chị dùng chính vào việc gì và ngân sách bao nhiêu để em chọn đôi tối ưu? "
                                    "Ví dụ đi làm cả ngày khác hoàn toàn với chạy bộ 10km ạ."),
        ("Có đôi nào rẻ không?", "Dạ shop có nhiều mức giá ạ. Anh/chị cho em khoảng ngân sách cụ thể (ví dụ 500k, 1 triệu, 2 triệu) "
                                 "và nhu cầu sử dụng, em sẽ gợi ý đôi đáng tiền nhất trong tầm đó ạ."),
        ("Giày này xịn không?", "Dạ để em trả lời đúng, anh/chị cho em biết đang nói tới mẫu nào ạ? "
                                "Nếu có ảnh hoặc tên mẫu, em nói rõ ưu/nhược và mức giá hợp lý cho đôi đó."),
        ("Shop có giày nam không?", "Dạ có ạ. Anh/chị cần giày cho dịp gì (đi làm, đi chơi, thể thao), tầm giá bao nhiêu và chân dài bao nhiêu cm ạ? "
                                    "Em gửi 3–5 mẫu đang có size phù hợp."),
        ("Mua giày tặng thì chọn gì?", "Dạ tặng giày nên chọn mẫu 'an toàn': trắng/kem, form trung tính và shop có đổi size. "
                                       "Anh/chị cho em biết người nhận là nam/nữ, tầm tuổi và ngân sách để em gợi ý ạ."),
    ]
    for q, a in VAGUE:
        add("clarify", q, a)

    # ------------------------------------------------ 18. Hội thoại nhiều lượt
    # 18a. Tư vấn chọn giày đi làm (7 lượt)
    picks = find_models_in_budget(2_000_000, 4_000_000, limit=3)
    if picks:
        b1, m1 = picks[0]
        b2, m2 = picks[1] if len(picks) > 1 else picks[0]
        R.append({"messages": [
            {"role": "system", "content": SYSTEMS[0]},
            {"role": "user", "content": rnd(["Shop ơi em cần mua đôi giày đi làm văn phòng",
                                             "Tư vấn giúp em giày đi làm ạ"])},
            {"role": "assistant", "content": (f"Dạ được ạ! Anh/chị cho em biết giới tính, ngân sách khoảng bao nhiêu và chỗ làm "
                                              f"yêu cầu lịch sự hay được mặc tự do, để em lọc mẫu chuẩn ạ. Nhân đây em gửi vài mẫu hay được chọn: "
                                              + ", ".join(f"{m['ten']} ({b['ten']})" for b, m in picks) + ".")},
            {"role": "user", "content": rnd(["Ngân sách của em 2–4 triệu, em là nữ ạ", "Tầm 2–4 triệu thôi ạ, em là nữ"])},
            {"role": "assistant", "content": (f"Dạ tầm này em gợi ý {m1['ten']} ({b1['ten']}): {m1['mo_ta']} Giá {m1['gia']}, "
                                              f"hợp {m1['phu_hop']}. Ngoài ra anh/chị xem thêm {m2['ten']} ({b2['ten']}) ạ.")},
            {"role": "user", "content": "Chân em 24cm, vậy lấy size gì ạ?"},
            {"role": "assistant", "content": ("Dạ chân 24cm ≈ US nữ 7.5 / EU 38 (quy đổi UNISEX là US nam 6). "
                                              "Nếu mẫu hơi hẹp ngang, chị lên nửa size. Shop đổi size miễn phí trong 7 ngày nên chị yên tâm ạ.")},
            {"role": "user", "content": rnd(["Ok chốt đôi đầu tiên nhé, mai em ghé lấy", "Vậy em lấy đôi đầu nha, chiều mai ghé shop"])},
            {"role": "assistant", "content": ("Dạ em giữ đôi {a} size EU 38 cho chị tới chiều mai nhé. Khi tới chị mang thử 5–10 phút cho chắc, "
                                              "nếu chưa vừa em đổi size ngay tại chỗ. Chị cho em số điện thoại để em xác nhận đơn ạ.").format(a=m1['ten'])},
        ], "category": "multiturn_advise"})

    # 18b. Check hàng chính hãng (5 lượt)
    b = rnd([x for x in ALL_BRANDS if x['id'] in ('nike', 'adidas', 'jordan', 'newbalance', 'gucci', 'vans')])
    ck = b.get('check', [])[:4]
    R.append({"messages": [
        {"role": "system", "content": SYSTEMS[1]},
        {"role": "user", "content": rnd([f"Em mới mua đôi {b['ten']} trên mạng, shop check giúp em có phải hàng thật không ạ",
                                         f"Em mua {b['ten']} giá 1,2 triệu, shop xem giúp có ổn không"])},
        {"role": "assistant", "content": (f"Dạ anh/chị gửi em vài ảnh rõ: tem size trong lưỡi giày, mặt lưỡi (nhãn hãng), "
                                          f"đế giày và hộp có nhãn giá nhé. Với {b['ten']}, anh/chị có thể tự check sơ bộ: "
                                          + "; ".join(ck) + ". Em chờ ảnh của anh/chị ạ.")},
        {"role": "user", "content": "Em gửi rồi đó shop, mà giá đôi này em mua có 1,2 triệu, rẻ hơn shop khác nhiều"},
        {"role": "assistant", "content": (f"Dạ với mức giá đó thì cần cẩn thận ạ: hàng chính hãng của {b['ten']} thường có giá tham khảo "
                                          f"{b['gia']}. Giá quá thấp so với mặt bằng chung là dấu hiệu rủi ro. Anh/chị gửi ảnh em xem kỹ "
                                          f"từng điểm ở trên; nếu mua nơi có hoá đơn, giữ lại để đối chiếu. Cần chắc 100%, anh/chị mang qua shop "
                                          f"kiểm tra trực tiếp miễn phí ạ.")},
        {"role": "user", "content": "Vậy để chiều em qua shop, shop check được cho em mấy giờ ạ?"},
        {"role": "assistant", "content": "Dạ shop mở cửa 9h–21h hằng ngày, anh/chị ghé lúc nào cũng có nhân viên check ạ. Anh/chị mang theo giày và hộp để em đối chiếu cho nhanh nhé."},
    ], "category": "multiturn_check"})

    # 18c. Chọn size (7 lượt)
    cm = rng.choice([23.5, 24.1, 24.8, 25.4, 26.0, 26.7])
    row = min(SIZE_TABLE['nam'], key=lambda r: abs(r[0] - cm))
    row_nu = min(SIZE_TABLE['nu'], key=lambda r: abs(r[0] - cm))
    cm_s = f"{cm:g}".replace('.', ',')
    R.append({"messages": [
        {"role": "system", "content": SYSTEMS[0]},
        {"role": "user", "content": f"Chân em dài {cm_s}cm, đi giày size bao nhiêu ạ?"},
        {"role": "assistant", "content": (f"Dạ chân {cm_s}cm tương đương US {row[1]} nam ≈ UK {row[3]} ≈ EU {row[4]} ạ. "
                                          f"Anh/chị là nam hay nữ để em quy đổi chính xác? Và chân có bè không ạ?")},
        {"role": "user", "content": rnd(["Nữ ạ, chân cũng hơi bè", "Nam ạ, chân bè nhẹ", "Nữ ạ, chân thon"])},
        {"role": "assistant", "content": (f"Dạ nữ thì US nữ ≈ {row_nu[2]} / EU {row_nu[4]}. Chân bè nhẹ thì anh/chị lấy đúng size này, "
                                          f"chỉ lên nửa size nếu mẫu hẹp ngang. Mua online nên chọn shop đổi size miễn phí nhé ạ.")},
        {"role": "user", "content": "Ok vậy em chọn size đó, cảm ơn shop"},
        {"role": "assistant", "content": ("Dạ không có gì ạ. Khi nhận giày, anh/chị đi 5–10 phút quanh nhà để kiểm tra, "
                                          "nếu chưa vừa thì báo em đổi size trong 7 ngày nhé. Cảm ơn anh/chị đã tin shop!")},
    ], "category": "multiturn_size"})

    # 18d. So sánh & chốt (5 lượt)
    c = rnd(COMPARISONS)
    R.append({"messages": [
        {"role": "system", "content": SYSTEMS[2]},
        {"role": "user", "content": f"Em phân vân giữa {c['a']} và {c['b']}, nên mua đôi nào ạ?"},
        {"role": "assistant", "content": f"Dạ cho em hỏi anh/chị định dùng giày vào việc gì chính ạ (đi học/đi làm/chạy bộ), "
                                         f"và ưu tiên êm chân hay form đẹp? Trong lúc chờ, em nói nhanh: {c['text']}"},
        {"role": "user", "content": rnd(["Em ưu tiên đi êm chân, dùng đi học hằng ngày", "Em thích form đẹp, đi chơi là chính"])},
        {"role": "assistant", "content": ("Dạ với nhu cầu đó, em nghiêng về đôi hợp tiêu chí của anh/chị nhất và khuyên thử cả hai nếu ghé shop ạ. "
                                          "Anh/chị cho em size hoặc số cm chân, em kiểm tra tồn kho và giữ mẫu luôn nhé!")},
    ], "category": "multiturn_compare"})

    # 18e. Chăm sóc giày (5 lượt)
    R.append({"messages": [
        {"role": "system", "content": SYSTEMS[0]},
        {"role": "user", "content": "Giày da lộn của em bị dính bùn, giờ xử lý sao ạ?"},
        {"role": "assistant", "content": ("Dạ anh/chị để bùn khô tự nhiên trước (đừng chùi khi còn ướt), sau đó dùng bàn chải cao su chuyên da lộn "
                                          "chải theo một chiều để lấy bùn ra. Còn vết thì chấm nhẹ hỗn hợp giấm trắng + nước (1:1), để khô rồi chải lại. "
                                          "Tuyệt đối không ngâm nước và không sấy nóng nhé ạ.")},
        {"role": "user", "content": "Có cần mua xịt gì không shop?"},
        {"role": "assistant", "content": ("Dạ nên mua xịt protector/nano ạ: xịt khi giày sạch và khô, cách 20cm, 2 lớp mỏng, để khô 24 giờ; "
                                          "sau đó phủ lại 1–2 tháng/lần. Shop có combo bàn chải cao su + xịt khoảng 180k, em để dành cho anh/chị nhé?")},
    ], "category": "multiturn_care"})

    # 18f. Nhân viên xử lý khiếu nại (3 lượt)
    R.append({"messages": [
        {"role": "system", "content": SYSTEMS[1]},
        {"role": "user", "content": "Tình huống: khách quay lại nói giày mua 3 tuần đã bung keo, tôi (nhân viên mới) nên xử lý thế nào?"},
        {"role": "assistant", "content": ("Dạ anh/chị xử lý theo 4 bước: (1) xin lỗi và ghi nhận trước – 'Dạ em rất tiếc vì trải nghiệm này ạ'; "
                                          "(2) kiểm tra lỗi: chụp ảnh vị trí bung, hỏi cách sử dụng (ngâm nước, phơi nắng...); "
                                          "(3) xử lý theo chính sách: trong 6 tháng bảo hành keo/đế do NSX → dán keo chuyên dụng miễn phí hoặc đổi đôi nếu lỗi nặng; "
                                          "(4) ghi sổ theo dõi và hẹn ngày cụ thể. Luôn giữ thái độ tích cực, không tranh luận đúng–sai trước mặt khách ạ.")},
    ], "category": "multiturn_complaint"})

    # 18g. Hàng hiệu (5 lượt)
    lux = [x for x in ALL_BRANDS if x['id'] in LUXURY_IDS][:3]
    lb = rnd(lux)
    lm = rnd(lb.get('mau_icon', [{'ten': 'sneaker', 'mo_ta': '', 'gia': lb['gia'], 'form': lb['form'], 'phu_hop': 'đi chơi'}]))
    R.append({"messages": [
        {"role": "system", "content": SYSTEMS[2]},
        {"role": "user", "content": f"Em định mua {lb['ten']} {lm['ten']}, tầm {lm['gia']} có đáng không ạ?"},
        {"role": "assistant", "content": (f"Dạ {lb['ten']} {lm['ten']}: {lm['mo_ta']} Giá tham khảo {lm['gia']}. "
                                          f"Điểm cần biết: " + "; ".join(lb['yeu']) + ". Nếu anh/chị coi đây là món phụ kiện đẳng cấp thì hợp lý; "
                                          f"còn nếu cần công năng (chạy bộ, đứng nhiều) em khuyên chọn giày hiệu năng cùng tầm giá ạ.")},
        {"role": "user", "content": "Vậy mua ở shop thì check chính hãng thế nào ạ?"},
        {"role": "assistant", "content": ("Dạ hàng hiệu thì anh/chị kiểm tra: " + "; ".join(lb['check'][:3]) +
                                          ". Shop nhập chính ngạch, có hoá đơn và bảo hành lỗi sản xuất; anh/chị nhận giày nhớ giữ hộp và bill để tiện đối chiếu về sau ạ.")},
    ], "category": "multiturn_luxury"})


    # ------------------------------------------------ 19. So sánh hãng với hãng
    for a, b_, text in BRAND_VS:
        add("brand_vs_brand",
            rnd([f"So sánh {a} và {b_} giúp em với",
                 f"{a} hay {b_} tốt hơn ạ?",
                 f"Nên chọn {a} hay {b_}?",
                 f"{a} với {b_} khác nhau chỗ nào?"]),
            rnd([f"Dạ so sánh {a} vs {b_}: {text} Anh/chị cho em nhu cầu chính và ngân sách, em chốt đúng hãng cho anh/chị ạ.",
                 f"Dạ hai hãng này đều tốt nhưng khác triết lý: {text} Nếu được, anh/chị ghé shop thử cả hai bên chân là chắc nhất ạ."]))

    # ------------------------------------------------ 20. Khoảng giá theo hãng
    for b in ALL_BRANDS:
        ms = b.get('mau_icon', [])[:3]
        sample = "; ".join(f"{m['ten']} ({m['gia']})" for m in ms)
        add("brand_price",
            rnd([f"Giày {b['ten']} giá bao nhiêu ạ?",
                 f"{b['ten']} tầm giá nào là phổ biến nhất?",
                 f"Đôi {b['ten']} rẻ nhất khoảng bao nhiêu?"]),
            rnd([f"Dạ {b['ten']} có khoảng giá: {b['gia']}. Một vài mốc tham khảo: {sample}. {PRICE_NOTE}.",
                 f"Dạ mặt bằng giá {b['ten']} tại Việt Nam: {b['gia']}. Ví dụ: {sample}. Anh/chị muốn em lọc mẫu theo ngân sách cụ thể không ạ?"]))

    # ------------------------------------------------ 21. Hội thoại: mua quà (5 lượt)
    picks = find_models_in_budget(1_800_000, 3_200_000, limit=3)
    if picks:
        g1, gm1 = picks[0]
        R.append({"messages": [
            {"role": "system", "content": SYSTEMS[0]},
            {"role": "user", "content": "Em muốn mua giày tặng bạn gái, ngân sách 2–3 triệu, mua gì được ạ?"},
            {"role": "assistant", "content": (f"Dạ tặng giày nên chọn mẫu 'an toàn': màu trắng/kem, form trung tính, shop có đổi size ạ. "
                                              f"Tầm 2–3 triệu em gợi ý {gm1['ten']} ({g1['ten']}), New Balance 550, Nike Air Force 1 trắng. "
                                              f"Chị ấy thường mặc style gì (nữ tính hay thể thao) để em chọn đúng gu?")},
            {"role": "user", "content": "Bạn ấy mặc kiểu nữ tính, hay đi làm nữa"},
            {"role": "assistant", "content": "Dạ vậy em nghiêng về mẫu form gọn màu sáng, đế hơi cao nhẹ để tôn dáng (ví dụ NB 550 hoặc Chuck 70 trắng). Nếu chị ấy đã có giày trắng, mình đổi sang màu be/nâu nhạt cũng rất sang ạ."},
            {"role": "user", "content": "Ok vậy chốt NB 550 nhé, mà chị không biết size của bạn"},
            {"role": "assistant", "content": ("Dạ an toàn nhất: anh/chị hỏi khéo size giày bạn ấy, hoặc 'mượn' 1 đôi đang dùng để đọc size trong lưỡi. "
                                              "Mua tặng mà chưa chắc size thì cứ lấy theo size phổ biến của nữ (US 7–8 / EU 37.5–38.5), giữ nguyên hộp và bill, "
                                              "shop hỗ trợ đổi size trong 7 ngày nên món quà vẫn trọn vẹn ạ!")},
        ], "category": "multiturn_gift"})

    # ------------------------------------------------ 22. Hội thoại: khách lớn tuổi (5 lượt)
    R.append({"messages": [
        {"role": "system", "content": SYSTEMS[0]},
        {"role": "user", "content": "Chú muốn mua giày đi bộ, chân hơi rộng, hay bị đau gót. Tư vấn giúp chú"},
        {"role": "assistant", "content": ("Dạ chào chú ạ. Với đau gót + chân rộng, chú ưu tiên: đệm êm dày (giảm áp lực gót), form rộng hoặc có bề ngang 2E, "
                                          "và lót hỗ trợ vòm. Chú tham khảo: Skechers Arch Fit/GOwalk, New Balance 1080 bản 2E, Asics Nimbus. "
                                          "Chú cho cháu số cm chân (đo buổi chiều) để cháu chọn size chuẩn ạ.")},
        {"role": "user", "content": "Chân chú 26,5cm"},
        {"role": "assistant", "content": ("Dạ 26,5cm ≈ US 9 nam / EU 42.5. Chân chú hơi rộng nên cháu tư vấn lấy EU 42.5 của New Balance bản 2E, "
                                          "hoặc Skechers thì lấy đúng số cm. Chú đi tất như bình thường khi thử để chắc chắn ạ.")},
        {"role": "user", "content": "Chú hay đi bộ công viên 1–2 tiếng mỗi sáng"},
        {"role": "assistant", "content": ("Dạ vậy Skechers Arch Fit hoặc New Balance 1080 v14 đều ổn ạ. Chú nên thêm lót than tre khử mùi (80k) và mua luôn "
                                          "bàn chải + xịt để giữ giày. Cháu để sẵn đôi EU 42.5 cho chú đến thử, chú đi 5–10 phút rồi mình quyết ạ.")},
    ], "category": "multiturn_senior"})

    return R


# ============================================================ GHÉP + TÁCH TẬP
def load_handcrafted(path):
    out = []
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
    return out


def main():
    ap = argparse.ArgumentParser(description="Sinh dataset huấn luyện ShoeBot từ knowledge base")
    ap.add_argument("--out", default="dataset", help="thư mục xuất train/val")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--val-ratio", type=float, default=0.05)
    ap.add_argument("--handcrafted", default=os.path.join(_HERE, "handcrafted_qa.jsonl"))
    args = ap.parse_args()

    global rng
    rng = random.Random(args.seed)

    data = rows() + load_handcrafted(args.handcrafted)

    seen, uniq = set(), []
    for r in data:
        msgs = r['messages']
        key = (msgs[-2]['content'][:150], msgs[-1]['content'][:150], len(msgs))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)

    rng.shuffle(uniq)
    n_val = max(1, int(len(uniq) * args.val_ratio))
    val, train = uniq[:n_val], uniq[n_val:]

    os.makedirs(args.out, exist_ok=True)
    for name, ds in (("train", train), ("val", val)):
        with open(os.path.join(args.out, f"{name}.jsonl"), "w", encoding="utf-8") as f:
            for r in ds:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    from collections import Counter
    cnt = Counter(r['category'] for r in uniq)
    turns = Counter(len(r['messages']) for r in uniq)
    q_len = [len(r['messages'][1]['content']) for r in uniq]
    a_len = [len(r['messages'][-1]['content']) for r in uniq]
    report = ["# Báo cáo dataset ShoeBot", "",
              f"- Tổng mẫu: **{len(uniq)}** (train {len(train)} / val {len(val)})",
              "- Số lượt hội thoại: " + ", ".join(f"{k} lượt: {v}" for k, v in sorted(turns.items())),
              f"- Câu hỏi dài trung bình {sum(q_len)/len(q_len):.0f} ký tự; câu trả lời {sum(a_len)/len(a_len):.0f} ký tự",
              "", "## Số mẫu theo nhóm nội dung", ""]
    for k, v in cnt.most_common():
        report.append(f"- `{k}`: {v}")
    report += ["", "## Nguồn dữ liệu", "",
               f"- {len(ALL_BRANDS)} thương hiệu, {len(MODELS)} mẫu giày, {len(TECHS)} công nghệ, "
               f"{len(GENERAL_FAQ)} FAQ, {len(COMPARISONS)} so sánh, {len(SCENARIOS)} tình huống, {len(NEED_MAP)} nhóm nhu cầu."]
    with open(os.path.join(args.out, "build_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print("\n".join(report[:7]))
    print(f"\nĐã ghi: {os.path.join(args.out,'train.jsonl')} và {os.path.join(args.out,'val.jsonl')}")


if __name__ == "__main__":
    main()
