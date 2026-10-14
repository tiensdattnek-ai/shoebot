# -*- coding: utf-8 -*-
"""
sizing.py – Bảng size, cách đo chân, form (phom) từng hãng, quy tắc chọn size.
Dùng cho dataset: câu hỏi size là nhóm khách hỏi nhiều NHẤT ở shop giày → phải trả lời được
"chân 25,5cm đi size nào?", "Nike vs Adidas có cùng size không?", "chân bè tăng size không?"...

Lưu ý: size giữa các hãng lệch nhau. Dữ liệu dưới đây là mốc tham khảo phổ biến cho giày NIKE
(kèm cột US nữ tương đương). Adidas dùng hệ size 1/3 nên cần bảng riêng (ADIDAS_*).
"""

# ---------------------------------------------------------------- Bảng chính (quy đổi phổ biến, chuẩn Nike-like)
SIZE_TABLE = {
    "nam": [
        # (cm, US nam, US nữ tương đương, UK, EU)
        (22.5, "5", "6.5", "4.5", "37.5"),
        (23.0, "5.5", "7", "5", "38"),
        (23.5, "6", "7.5", "5.5", "38.5"),
        (24.0, "6.5", "8", "6", "39"),
        (24.5, "7", "8.5", "6.5", "40"),
        (25.0, "7.5", "9", "7", "40.5"),
        (25.5, "8", "9.5", "7.5", "41"),
        (26.0, "8.5", "10", "8", "42"),
        (26.5, "9", "10.5", "8.5", "42.5"),
        (27.0, "9.5", "11", "9", "43"),
        (27.5, "10", "11.5", "9.5", "44"),
        (28.0, "10.5", "12", "10", "44.5"),
        (28.5, "11", "12.5", "10.5", "45"),
        (29.0, "11.5", "13", "11", "45.5"),
        (29.5, "12", "13.5", "11.5", "46"),
        (30.0, "12.5", "14", "12", "47"),
    ],
    "nu": [
        # (cm, US nữ, US nam tương đương, UK, EU)
        (21.5, "5", "3.5", "2.5", "35"),
        (22.0, "5.5", "4", "3", "35.5"),
        (22.5, "6", "4.5", "3.5", "36"),
        (23.0, "6.5", "5", "4", "36.5"),
        (23.5, "7", "5.5", "4.5", "37.5"),
        (24.0, "7.5", "6", "5", "38"),
        (24.5, "8", "6.5", "5.5", "38.5"),
        (25.0, "8.5", "7", "6", "39"),
        (25.5, "9", "7.5", "6.5", "40"),
        (26.0, "9.5", "8", "7", "40.5"),
        (26.5, "10", "8.5", "7.5", "41"),
        (27.0, "10.5", "9", "8", "42"),
        (28.0, "11.5", "10", "9", "43"),
        (28.5, "12", "10.5", "9.5", "44"),
    ],
}

# ---------------------------------------------------------------- Adidas (hệ size 1/3)
ADIDAS_TABLE = {
    "nam": [
        (24.2, "6", "5.5", "39 1/3"),
        (24.6, "6.5", "6", "40"),
        (25.0, "7", "6.5", "40 2/3"),
        (25.4, "7.5", "7", "41 1/3"),
        (25.8, "8", "7.5", "42"),
        (26.2, "8.5", "8", "42 2/3"),
        (26.7, "9", "8.5", "43 1/3"),
        (27.1, "9.5", "9", "44"),
        (27.5, "10", "9.5", "44 2/3"),
        (27.9, "10.5", "10", "45 1/3"),
        (28.3, "11", "10.5", "46"),
        (28.8, "11.5", "11", "46 2/3"),
        (29.2, "12", "11.5", "47 1/3"),
    ],
    "nu": [
        (21.6, "5", "4.5", "36"),
        (22.1, "5.5", "5", "36 2/3"),
        (22.5, "6", "5.5", "37 1/3"),
        (22.9, "6.5", "6", "38"),
        (23.3, "7", "6.5", "38 2/3"),
        (23.8, "7.5", "7", "39 1/3"),
        (24.2, "8", "7.5", "40"),
        (24.6, "8.5", "8", "40 2/3"),
        (25.0, "9", "8.5", "41 1/3"),
        (25.5, "9.5", "9", "42"),
        (25.9, "10", "9.5", "42 2/3"),
        (26.3, "10.5", "10", "43 1/3"),
        (26.7, "11", "10.5", "44"),
    ],
}
ADIDAS_NOTE = ("Adidas không có size 41, 42, 43... liền mạch mà dùng bước 1/3 (41 1/3, 42, 42 2/3). "
               "Vì vậy đừng so 'cùng EU' giữa Adidas và Nike — hãy so theo cm.")

# ---------------------------------------------------------------- Trẻ em
KID_TABLE = [
    # (cm, US kid, EU, tuổi tham khảo)
    (12.0, "5C",  "21", "9–15 tháng"),
    (13.0, "6C",  "22", "1–1.5 tuổi"),
    (14.0, "7C",  "23", "1.5–2 tuổi"),
    (15.0, "8C",  "24", "2–2.5 tuổi"),
    (16.0, "9C",  "25", "2.5–3 tuổi"),
    (17.0, "10C", "27", "3–3.5 tuổi"),
    (18.0, "11C", "28", "4 tuổi"),
    (19.0, "12C", "30", "5 tuổi"),
    (20.0, "13C", "31", "5–6 tuổi"),
    (21.0, "1Y",  "32", "6–7 tuổi"),
    (22.0, "2Y",  "34", "7–8 tuổi"),
]
KID_NOTE = ("Trẻ nhỏ nên chọn giày dư 0.5–1cm (khoảng 1 ngón út) để chân phát triển; "
            "trẻ 5–10 tuổi đo lại chân mỗi 3–6 tháng; đế mềm, gập được ở 1/3 trước bàn chân là phù hợp.")

# ---------------------------------------------------------------- Phom / form từng hãng (rất cần cho tư vấn)
FIT_NOTES = [
    ("Nike", "Dòng thời trang (Dunk, Air Max 97/90, Jordan 1) hơi HẸP MŨI và hẹp ngang; "
             "Air Force 1 và Air Max 1 RỘNG rãi hơn. Chân bè nên tăng 0.5 size với Dunk/Air Max. "
             "Giày chạy Pegasus/Vomero thường đúng size (true to size)."),
    ("Adidas", "Đúng size (TTS) nhưng Samba/Gazelle/Spezial/Country hẹp ngang — chân bè lên 0.5 size. "
               "Ultraboost/Primeknit ôm như tất, nên lên 0.5 nếu chân dày. Đế Boost cao nên khách hay thấy 'khoẻ chân' hơn."),
    ("New Balance", "Rộng rãi hơn Nike ~0.5 size (dòng 574/530/9060). Là hãng DUY NHẤT ở phân khúc phổ thông "
                    "bán bề ngang 2E/4E cho chân bè — cực kỳ phù hợp chân châu Á. 990/993 made in USA form thoải mái."),
    ("Asics", "Form hợp chân châu Á, mũi rộng vừa. Gel-Nimbus/Kayano/Cumulus đúng size; chân bè có thể giữ nguyên. "
              "Gel-1130/1090 retro đúng size."),
    ("Mizuno", "Form châu Á, hợp chân bè; Wave Rider/Horizon đúng size, không cần lên size."),
    ("Puma", "Đúng size; Suede/Palermo/Speedcat hơi hẹp ngang nhẹ → chân bè +0.5."),
    ("Hoka", "Đúng size (TTS) theo số người dùng phản hồi; Clifton/Bondi có mũi rộng, gót ôm. "
             "Chân bè thường giữ đúng size."),
    ("On (On Running)", "Hơi NHỎ và hẹp — nên tăng 0.5 size so với giày thường, đặc biệt Cloud 5/Cloudswift."),
    ("Salomon", "Đúng size nhưng XT-6/XT-4 ôm ngang; chân dày nên +0.5. Dòng GORE-TEX cần chỗ cho tất dày."),
    ("Brooks", "Đúng size, form Mỹ hơi rộng; chân nhỏ/thon có thể giảm 0.5 với Ghost/Adrenaline."),
    ("Saucony", "Đúng size, hơi hẹp nhẹ với một số dòng (Endorphin); chân bè +0.5."),
    ("Converse", "Chuck Taylor All Star CHẠY DÀI — thường giảm 0.5 so với size thật (nếu đi Nike 42 thì Chuck lấy 41.5/US 9). "
                 "Chuck 70 đế dày, form ôm hơn bản thường. Run Star Motion cũng dài."),
    ("Vans", "Classic (Old Skool, Authentic, Era) đi DÀI và HƠI ÔM NGANG → nhiều người giảm 0.5. "
             "Bản Knu Skool/với PopCush mềm hơn. Sk8-Hi: chân bè nên giữ đúng size hoặc +0.5."),
    ("Dr. Martens", "Size đúng nhưng da Smooth CỨNG khi mới → chân bè hoặc đi tất dày nên +0.5 size; "
                    "dòng Nappa/Pascal mềm hơn. Đóng giày 1–2 tuần đầu là bình thường."),
    ("Crocs", "Không dùng size US chung: chọn theo cm, nên còn dư ~0.5–1cm sau gót khi đứng (không dư quá để khỏi tuột). "
              "Classic Clog đúng size cm; Sandal/giày trẻ em chọn theo cm."),
    ("Birkenstock", "Chọn theo cm: gót và mũi nằm GỌN trong lòng đế (không dư nhiều) vì lót cork định hình vòm. "
                    "Bản Narrow hợp chân thon; Regular hợp chân bè."),
    ("Timberland", "Boot 6-inch: đúng size với tất mỏng, +0.5 với tất dày (mùa đông). Hơi nặng, cần 'phá đế' 1 tuần."),
    ("Clarks", "Đúng size; dòng Desert Boot/Wallabee rộng rãi hơn sneaker thường một chút — chân thon có thể giảm 0.5."),
    ("Biti's", "Đúng size VN (theo cm); Hunter X dạng đế dày nhẹ nên +0.5 nếu chân bè. Dép Biti's đúng size."),
    ("Ananas", "Form chuẩn (đúng size); chân bè +0.5. Vải canvas sẽ giãn nhẹ sau 2–3 tuần."),
    ("Gucci / LV / Dior / Chanel / Prada", "Hàng hiệu thường đúng size với da; nhưng Balenciaga Triple S nên GIẢM 0.5–1 (đế to, form 'trông to'), "
                                          "McQueen Oversized giảm 0.5, Off-White OOO giảm 0.5 nếu chân thon."),
]

# ---------------------------------------------------------------- Các bước đo chân
HOW_TO_MEASURE = [
    "1) Đo vào CUỐI NGÀY (chiều tối chân to nhất do đi lại cả ngày).",
    "2) Đứng tựa tường, đặt tờ giấy A4 dưới chân, đánh dấu gót và đầu ngón dài NHẤT.",
    "3) Đo khoảng cách giữa 2 điểm (cm). Đo CẢ HAI CHÂN rồi lấy chân DÀI HƠN làm chuẩn.",
    "4) Cộng thêm: giày văn phòng/hằng ngày +0.5–1cm; giày chạy bộ +1–1.5cm (chân nở khi chạy dài); "
    "giày trẻ em +0.5–1cm.",
    "5) So với bảng: ví dụ chân 25.4cm → US nam 8 = UK 7.5 = EU 41 (Nike). Adidas dùng bảng riêng (41 1/3).",
    "6) Mẹo thử nhanh khi mua tại shop: đứng lên, gót sát gót giày, ngón cái để phía mũi — còn nửa ngón tay là vừa; "
    "cảm nhận hai bên KHÔNG bị kích; đi thử 5–10 phút ở cả hai chân, đi không chỉ thử ngồi.",
    "7) Chân bè (bè ngang, bàn chân dày): ưu tiên hãng có bề ngang rộng (New Balance 2E/4E, Asics/Mizuno form châu Á); "
    "nếu mẫu hẹp ngang → +0.5 size, KHÔNG tăng quá 1 size vì sẽ bị nhấc gót.",
]

# ---------------------------------------------------------------- FAQ về size hay gặp
SIZE_FAQ = [
    {
        "q": "Chân 25cm đi giày size bao nhiêu?",
        "a": ("Chân 25cm: US nam 7.5 = UK 7 = EU 40.5 (chuẩn Nike). Adidas EU 41 1/3 (25.4cm) bảng riêng. "
              "Nếu chân bè hoặc mẫu hẹp ngang (Dunk, Samba), lên nửa size. Giày chạy nên thêm 1–1.5cm."),
    },
    {
        "q": "Chân 26cm đi size mấy?",
        "a": "Chân 26cm: US nam 8.5 = UK 8 = EU 42 (Nike). Nữ thì US nữ ≈ 10. Đo cuối ngày cho chính xác nhất.",
    },
    {
        "q": "Nike và Adidas cùng size không?",
        "a": ("Không hẳn. Nike dùng size liền mạch (41, 42, 43) còn Adidas dùng bước 1/3 (41 1/3, 42, 42 2/3). "
              "Adidas 42 thường nhỏ hơn Nike 42 một chút. Cách chắc nhất: so theo cm (chân dài bao nhiêu cm)."),
    },
    {
        "q": "Size giày nữ và nam khác nhau thế nào?",
        "a": ("Giày UNISEX dùng size nam: size nữ = size nam + 1.5 (ví dụ nữ US 8 ≈ nam US 6.5). "
              "Ở bảng cm: chân 24cm → nam US 6.5 / nữ US 8."),
    },
    {
        "q": "Chân bè có phải tăng size không?",
        "a": ("Tăng 0.5 size nếu mẫu HẸP NGANG (Dunk, Samba, Gazelle, Salomon XT-6, On Cloud). "
              "Không cần tăng với Air Force 1, New Balance 574/530, Asics, Mizuno vì form rộng sẵn. "
              "Nếu tăng quá 1 size sẽ bị nhấc gót, đau gót khi đi."),
    },
    {
        "q": "Giày Converse/Vans có cần giảm size không?",
        "a": "Có. Chuck Taylor All Star và Vans Classic (Old Skool, Authentic) thường chạy dài 0.5 size — "
             "nhiều người giảm 0.5. Riêng Chuck 70 ôm chân hơn, thử trước khi quyết.",
    },
    {
        "q": "Mua online không thử được thì chọn sao cho đúng size?",
        "a": ("Đo chân đúng cách rồi tra bảng cm; ưu tiên shop có đổi size miễn phí; nếu chân ở đúng giữa 2 size "
              "→ chọn size lớn hơn nếu là chân bè, chọn size nhỏ nếu chân thon và mẫu giày rộng."),
    },
    {
        "q": "Đi size 40 mua Converse size 40 có vừa không?",
        "a": "Thường KHÔNG vì Converse (All Star) đi dài hơn; người size 40 thường hợp Chuck size US 8 (≈41). "
             "Tốt nhất thử hoặc đo cm trước: nếu chân 25cm thì Chuck US 8–9 tuỳ form.",
    },
    {
        "q": "Trẻ em mua giày size sao cho phù hợp?",
        "a": "Đo chân bé theo cm, cộng 0.5–1cm; bảng: chân 18cm ≈ US 11C/EU 28 (khoảng 4 tuổi). "
             "Kiểm tra lại mỗi 3–6 tháng vì chân bé lên nhanh; đế mềm gập được ở 1/3 trước bàn chân.",
    },
    {
        "q": "Chân vòm thấp (bẹt) đi giày size thế nào?",
        "a": "Size vẫn theo cm như thường; quan trọng là chọn mẫu CÓ HỖ TRỢ ỔN ĐỊNH (Kayano, Adrenaline GTS, Arahi, NB 860) "
             "và có thể thêm lót hỗ trợ vòm. Đừng mua size lớn hơn chỉ vì vòm thấp.",
    },
]
