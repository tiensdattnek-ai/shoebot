# -*- coding: utf-8 -*-
"""
support.py – FAQ bán hàng, check chính hãng, chăm sóc giày, xu hướng, so sánh, tình huống tư vấn,
chính sách shop (mẫu) và gợi ý bán kèm.
Đây là "kho vũ khí" giọng sales: nhân viên/bot dùng để tư vấn khách.
LƯU Ý: các con số chính sách (bảo hành, freeship) là MẪU – shop phải sửa theo chính sách thật.
"""

# ================================================================ 1. FAQ chung
GENERAL_FAQ = [
    {"q": "Bên shop có bán hàng chính hãng không?", "a": "Dạ shop cam kết hàng chính hãng 100%, có hóa đơn và tem đầy đủ, sai đền gấp đôi ạ. Anh/chị có thể check mã sản phẩm trên website hãng trước khi mua."},
    {"q": "Giày bên shop có bảo hành không?", "a": "Dạ có ạ: bảo hành keo/đế 6 tháng cho lỗi sản xuất (bong keo, hở đế do nhà sản xuất), hỗ trợ vệ sinh miễn phí 1 lần trong 3 tháng đầu. Riêng hư hại do sử dụng (cắt, cháy, ngâm nước) không thuộc bảo hành."},
    {"q": "Mua xong không vừa size có đổi được không?", "a": "Dạ được ạ – đổi size trong 7 ngày, giày còn nguyên tem/hộp, chưa dùng ngoài trời. Shop hỗ trợ đổi 1 lần miễn phí, từ lần thứ 2 phụ phí ship nhé ạ."},
    {"q": "Shop có ship toàn quốc không? Bao lâu nhận hàng?", "a": "Dạ ship toàn quốc ạ. Nội thành 1–2 ngày, tỉnh 2–4 ngày làm việc. Đơn từ 1 triệu shop freeship, dưới 1 triệu phí 25–35k tùy khu vực ạ."},
    {"q": "Có được kiểm hàng (đồng kiểm) khi nhận không?", "a": "Dạ có ạ, anh/chị được mở hộp kiểm tra trước khi thanh toán. Nhớ quay clip lúc mở hàng để hai bên xử lý nhanh nếu có vấn đề nhé."},
    {"q": "Bên shop thanh toán như thế nào?", "a": "Dạ COD, chuyển khoản, ví điện tử (Momo/ZaloPay), thẻ và trả góp 0% qua thẻ tín dụng cho đơn từ 3 triệu ạ."},
    {"q": "Giày này có phải chính hãng không? Sao rẻ hơn chỗ khác?", "a": "Dạ shop nhập chính ngạch/đại lý ủy quyền nên được giá tốt, có tem và bill đầy đủ. Nếu giá thấp hơn thị trường quá nhiều (dưới 50% giá niêm yết) thì mới đáng nghi ngờ, còn chênh 10–20% là chuyện bình thường do đợt sale/nhập sỉ ạ."},
    {"q": "Làm sao để biết hàng thật – hàng giả?", "a": "Dạ anh/chị check 3 thứ nhanh nhất: (1) tem/mã sản phẩm (Nike: xxxxxx-xxx, Adidas: ART/ID) phải khớp hộp và bill; (2) đường may, keo, mùi vật liệu; (3) mua ở shop có tên, có hóa đơn. Shop nhận check hộ miễn phí nếu anh/chị mua ở nơi khác ạ."},
    {"q": "Có giày cho chân bè không?", "a": "Dạ có ạ. New Balance có size bề ngang 2E/4E (tốt nhất cho chân bè), ngoài ra Asics/Mizuno form châu Á rộng mũi, Air Force 1 cũng rộng. Anh/chị cho em số cm chân, em lọc đúng mẫu luôn nhé."},
    {"q": "Giày thể thao đi làm văn phòng được không?", "a": "Dạ hoàn toàn được, xu hướng 2026 là sneaker tối giản (da trắng, không logo to) đi làm rất lịch sự: kiểu AF1 trắng, NB 550, veja/Stan Smith, loafer-sneaker. Anh/chị muốn em gợi ý 3 mẫu dưới 2 triệu không ạ?"},
    {"q": "Giày bao lâu thì thay mới?", "a": "Dạ tùy cường độ: đi làm hằng ngày 1.5–2 năm; chạy bộ nên thay sau 600–800km (khoảng 1–1.5 năm với 20km/tuần). Dấu hiệu nên thay: đế mòn lệch, foam hết hồi, đau gót/chân khi đi lại mẫu quen thuộc."},
    {"q": "Giày cũ có được thu đổi không?", "a": "Dạ shop có chương trình 'đổi giày cũ – giảm 10%': mang giày cũ (bất kỳ hãng, bất kỳ tình trạng) đến shop để được giảm 10% khi mua đôi mới, giày cũ được trao tặng cho chương trình từ thiện ạ."},
    {"q": "Đặt trước giày hết hàng được không?", "a": "Dạ được ạ, đặt cọc 200k, hàng về trong 7–14 ngày tùy mẫu. Nếu hàng không về được, shop hoàn cọc 100% nhé."},
    {"q": "Shop có bán giày cho size lớn (46–48) không?", "a": "Dạ có ạ nhưng tồn kho ít. Anh/chị cho em biết mẫu + size để em kiểm tra kho, chưa có em đặt nhập về trong 7–10 ngày nhé. New Balance/Asics thường có size lớn tốt hơn Nike."},
    {"q": "Có giày nữ size 39–41 không?", "a": "Dạ có ạ, nhiều mẫu unisex lấy size nam tương ứng (nữ 40 ≈ nam 8.5). Chị cho em số cm chân để em quy đổi chuẩn nhất nhé."},
    {"q": "Giày trắng có dễ bẩn vàng không?", "a": "Dạ giày trắng nên vệ sinh định kỳ 2 tuần/lần và PHƠI TRONG BÓNG MÂT, tránh nắng trực tiếp (nguyên nhân chính gây ố vàng). Dùng dung dịch vệ sinh pha loãng, tráng sạch, lót giấy trắng khi phơi. Shop tặng kèm xịt nano chống bám bẩn cho giày trắng nhé ạ."},
    {"q": "Đi giày mới bị đau gót/chột chân thì sao?", "a": "Dạ giày da (Dr. Martens, boot) thường cần 1–2 tuần 'phá giày'. Mẹo: đi tất dày với máy sấy tóc sấy nhẹ phần da gót, dùng gót dán/silicon dán gót, đến shop để nong miễn phí. Nếu đau kéo dài quá 2 tuần, anh/chị mang qua shop kiểm tra giúp em nhé."},
    {"q": "Giày bị hôi chân xử lý thế nào?", "a": "Dạ anh/chị: (1) lót giày bỏ ra phơi khô; (2) rắc baking soda hoặc gói trà khô/túi than trong giày qua đêm; (3) dùng xịt khử mùi chuyên dụng; (4) luân phiên 2 đôi để giày khô hoàn toàn. Nếu lót cao su bị mùi lâu, thay lót mới (shop có lót than tre 80k)."},
    {"q": "Giày tăng size theo thời gian không?", "a": "Dạ giày da/da lộn sẽ 'giãn' theo chân khoảng 0.25–0.5 size sau vài tuần; vải canvas giãn nhẹ; giày thể thao tổng hợp gần như giãn không đáng kể. Nên mua vừa khít thoải mái, không mua nhỏ để 'nó giãn ra' nhé ạ."},
    {"q": "Hàng thanh lý/outlet có phải hàng giả không?", "a": "Dạ không nhất thiết. Outlet là hàng chính hãng của mùa cũ, hàng lỗi nhẹ hoặc size lẻ → giá rẻ hơn. Nhưng nếu outlet bán giá quá thấp cho mẫu đang hot (ví dụ AF1 800k, Chunky 500k) thì gần như không phải hàng thật ạ."},
    {"q": "Có nhận check giày giúp khách không?", "a": "Dạ có ạ. Anh/chị gửi ảnh: tem/size, lưỡi gà, đế, hộp và bill; em xem và tư vấn các điểm cần lưu ý. Shop nói rõ: check qua ảnh chỉ khoảng 80%, muốn chắc nhất cần cầm trực tiếp ạ."},
    {"q": "Vì sao cùng đôi giày mà mỗi nơi bán giá khác nhau?", "a": "Dạ do nguồn nhập, đợt sale, size hot/chậm và phí vận chuyển khác nhau ạ. Chênh 10–20% là bình thường; chênh 40–50% thì nên xem lại tem/mã sản phẩm."},
    {"q": "Giày nam và nữ có khác nhau về công nghệ không?", "a": "Dạ thường cùng công nghệ, chỉ khác form (nữ thường hẹp hơn, đệm mỏng hơn nhẹ) và size. Một số mẫu nữ dùng đế/foam mỏng hơn bản nam để nhẹ chân. Về unisex, chỉ cần quy đổi size nam ↔ nữ (lệch 1.5) ạ."},
    {"q": "Sản phẩm có phải hàng 1:1, rep không?", "a": "Dạ không ạ. Bên shop chỉ bán hàng chính hãng. Những khái niệm rep/1:1/siêu cấp đều là giày SAO CHÉP, không có nguồn gốc chính hãng; giá rẻ nhưng vật liệu, keo và độ bền kém hơn nhiều và dễ hỏng đế sau 6–12 tháng ạ."},
    {"q": "Vì sao giày chạy bộ đắt hơn giày thường?", "a": "Dạ giày chạy dùng foam công nghệ cao (ZoomX, Lightstrike Pro, FF BLAST), thiết kế cho quãng đường dài, nghiên cứu dáng chạy. Giày chạy race (Vaporfly, Adios Pro) còn có tấm carbon — đó là lý do giá 5–8 triệu. Nếu chỉ đi bộ, không cần mua tầm đó ạ."},
]

# ================================================================ 2. Check chính hãng (chung)
FAKE_CHECK_GENERAL = [
    "Nguyên tắc 1: HÀNG RẺ BẤT THƯỜNG = RỦI RO CAO. Giá dưới 50% giá niêm yết của mẫu mới đang hot gần như chắc chắn không phải hàng thật.",
    "Nguyên tắc 2: Mua nơi có tên tuổi, hóa đơn, chính sách đổi trả. Không mua trôi nổi chỉ có 1–2 ảnh và giá 'sập sàn'.",
    "Check tem & mã: mã sản phẩm trên tem (Nike: xxxxxx-xxx; Adidas: ART/ID; NB: Mxxxx) phải KHỚP giữa tem, hộp và hóa đơn.",
    "Check đường may: hàng thật chỉ đều, mũi ngắn, không xộc xệch, không chỉ thừa kéo dài.",
    "Check keo: viền keo thật mỏng, gọn, không tràn ra thành vệt vàng dày.",
    "Check mùi & vật liệu: hàng thật ít mùi keo công nghiệp; da có vân tự nhiên, lưới dệt chắc.",
    "Check đế: đế khối lượng khớp mô tả (Balenciaga to nặng, ZoomX nhẹ tênh), lót in size chuẩn, không lệch chữ.",
    "Check hộp & phụ kiện: hộp/hộp dày chuẩn, giấy gói, túi bụi, thẻ hãng — nhiều fake bỏ qua phần này.",
    "Dùng app/website: tra mã sản phẩm trên web hãng để so ảnh và ngày ra mắt; một số hãng có check serial.",
    "Yếu tố cuối: NHỜ CHECK 3 NGUỒN. Đến shop có kinh nghiệm cầm thử, so với đôi thật — 'cảm giác cầm trên tay' quan trọng không kém thông tin.",
]

# ================================================================ 3. So sánh nhanh các cặp giày hay được hỏi
COMPARISONS = [
    {"a": "Nike Air Force 1", "b": "Nike Dunk Low",
     "text": "Cùng tầm giá 2–3 triệu, đều là sneaker biểu tượng. AF1: đế Air êm hơn, form rộng rãi thích hợp chân bè, 'bền hơn' khi đi nhiều; hơi nặng. Dunk: gọn gàng hơn, form hẹp ngang và mũi thấp → chân bè nên +0.5 size, phù hợp phối đồ slim/skate. Cần êm + bền → AF1; cần form gọn trendy → Dunk."},
    {"a": "Adidas Samba OG", "b": "Adidas Gazelle",
     "text": "Samba (1950) đế gum mỏng, mũi dài, hơi hẹp ngang; Gazelle đế gum nhưng thân da lộn mềm hơn, form rộng hơn Samba một chút. Cùng 2–2.8 triệu. Samba hợp phối âu phục/skool; Gazelle hợp chân bè hơn và mềm chân hơn."},
    {"a": "Adidas Ultraboost", "b": "Nike Pegasus",
     "text": "Khác mục đích: Ultraboost (3.5–5 triệu) là giày đi bộ/đứng nhiều với Boost cực êm, thân Primeknit ôm như tất — hợp đi làm, đi chơi. Pegasus (3.1–4.5 triệu) là giày chạy bộ: nhẹ hơn, đệm Zoom Air đàn hồi, thoáng hơn. Đi bộ êm → Ultraboost; chạy thật sự → Pegasus."},
    {"a": "Converse Chuck 70", "b": "Vans Old Skool",
     "text": "Chuck 70: canvas dày, đế cao su dày êm hơn All Star, cổ cao, retro. Old Skool: da lộn + đế waffle bám hơn, form ôm và thấp hơn. Cùng 1.6–2.5 triệu. Đi bộ nhiều: Chuck 70 êm hơn chút; bám tốt/cân bằng: Old Skool. Cả hai đều đi dài 0.5 size — nên chọn nhỏ hơn nửa size."},
    {"a": "Asics Gel-Kayano", "b": "Asics Gel-Nimbus",
     "text": "Cùng đệm GEL và giá 3.8–5 triệu. Kayano: dòng ỔN ĐỊNH (hỗ trợ chân bẹt/lật vào, có 4D Guidance). Nimbus: dòng ÊM TỐI ĐA cho chân bình thường/vòm cao. Chọn theo chân: bẹt/đau gối → Kayano; vòm cao/cần êm → Nimbus."},
    {"a": "Hoka Clifton", "b": "Hoka Bondi",
     "text": "Bondi: đệm dày nhất nhóm, êm tối đa, hơi nặng — hợp đứng lâu, đi bộ nhiều, khớp nhạy cảm. Clifton: nhẹ hơn, đệm vẫn êm nhưng 'sống động' hơn, hợp chạy hàng ngày. Cùng 3.9–5.5 triệu. Chỉ đi bộ/đứng → Bondi; vừa đi vừa chạy → Clifton."},
    {"a": "Biti's Hunter X", "b": "Skechers GOwalk",
     "text": "Cùng nhóm đi bộ êm giá rẻ. Hunter X: nhẹ (~204g), đế Phylon đàn hồi, giá 700k–1.1 triệu, form trẻ. GOwalk: đệm Memory Foam mềm, giá 1.2–2 triệu, hợp người lớn tuổi, đứng nhiều. Ngân sách <1 triệu → Hunter X; cần êm tối đa cho chân nhạy → GOwalk."},
    {"a": "Ananas Basas", "b": "Converse Chuck Taylor All Star",
     "text": "Cùng form canvas retro. Basas: đế lưu hoá dày, êm hơn, giá 500–800k, đế không dễ bong keo. Chuck: nhận diện quốc tế, đế mỏng hơn (bản All Star thường), giá 1.2–1.8 triệu. Muốn tiết kiệm + đi bộ ổn → Basas; cần thương hiệu quốc tế → Chuck."},
    {"a": "New Balance 530", "b": "New Balance 574",
     "text": "Đều là 'giày quốc dân' NB. 530: form 'dad shoes' ôm vừa, đế ABZORB êm, màu sáng, hợp phối đồ năng động. 574: cổ điển hơn, đế ENCAP bền, form tròn, hợp đi làm. Cùng 1.8–2.5 triệu. Trẻ/casual → 530; chín/công sở → 574."},
    {"a": "Crocs Classic", "b": "Birkenstock Arizona",
     "text": "Crocs: EVA nhẹ 1–1.6 triệu, đi mưa/đi biển tốt, rửa nước được, êm nhẹ. Arizona: đế cork định hình vòm (2–4 triệu), hỗ trợ chân tốt hơn nhiều, cần 1–2 tuần làm quen, không ngâm nước. Cần nhẹ-rẻ-trời mưa → Crocs; cần nâng vòm/đau gót → Arizona."},
    {"a": "Dr. Martens 1460", "b": "Timberland 6-inch",
     "text": "Cùng boot da nổi. 1460: cổ cao 8 lỗ, đế AirWair, phong cách rock/punk, đi mưa được, giá 3.5–5 triệu, đau gót tuần đầu. Timberland: nubuck chống nước, đế lug bám địa hình, ấm, giá 3.5–5 triệu. Đi phố/style → 1460; đi rừng/mùa lạnh/địa hình → Timberland."},
    {"a": "Alexander McQueen Oversized", "b": "Golden Goose Super-Star",
     "text": "Cùng nhóm luxury sneaker 12–18 triệu. McQueen: đế platform dày, tôn chiều cao, da trắng tinh khôi, hợp chụp ảnh. Golden Goose: đế 'bẩn' cố ý, mềm chân hơn, phong cách lived-in. Thích nổi bật/cao ráo → McQueen; thích 'cũ nhưng sang' → Golden Goose."},
]

# ================================================================ 4. Chăm sóc – vệ sinh theo chất liệu
CARE = {
    "da_thật": [
        "Lau bằng khăn ẩm mềm, KHÔNG ngâm nước; dùng dung dịch vệ sinh da chuyên dụng, tránh cồn/acetone.",
        "Vết bẩn mới: tẩy ngay bằng khăn ẩm + chút dầu gội em bé pha nước.",
        "Dưỡng da (conditioner) mỗi 2–3 tháng để da không khô nứt; đánh xi giữ màu với giày tối màu.",
        "Phơi trong bóng mát, nhồi giấy báo/cây giữ form; tránh nắng trực tiếp và máy sấy.",
    ],
    "da_lộn_suede": [
        "KHÔNG dùng nước/nước rửa phổ thông; dùng bàn chải cao su chuyên da lộn để hết bụi (chải theo 1 chiều).",
        "Vết bẩn: cục tẩy da lộn hoặc hỗn hợp giấm trắng + nước (1:1) chấm nhẹ, để khô tự nhiên rồi chải lại.",
        "Phủ xịt nano/protector ngay khi mua mới và phủ lại 1–2 tháng/lần — giảm 80% vấn đề.",
        "Gặp mưa: để khô tự nhiên (không sấy), nhồi giấy giữ form, chải lại khi khô.",
    ],
    "canvas_vải": [
        "Có thể giặt tay nhẹ với bột giặt pha loãng + bàn chải mềm; KHÔNG vắt xoắn, không máy giặt.",
        "Vết bẩn cứng đầu: baking soda + nước chấm lên, để 10 phút rồi chải.",
        "Vải trắng: sau khi giặt, tráng sạch hết xà phòng (cặn xà phòng chính là thứ gây ố vàng), bọc giấy trắng kín mặt vải khi phơi.",
        "Phơi nơi thoáng mát; nhét giấy báo giữ form. Tránh phơi nắng gắt làm vải cứng và ngả vàng.",
    ],
    "luoi_mesh_knit": [
        "Dùng bàn chải mềm + nước ấm pha xà phòng nhẹ, lau cục bộ rồi thấm khô; không chà mạnh vì dễ xước sợi.",
        "Máy giặt: KHÔNG khuyến khích; nếu bắt buộc thì cho vào túi lưới, nước lạnh, chu trình nhẹ — sẽ giảm tuổi thọ keo.",
        "Khử mùi: phơi thoáng + gói than/trà; thay lót giày định kỳ 6–12 tháng.",
    ],
    "cao_su_eva": [
        "Rửa nước trực tiếp được: xà phòng nhẹ + bàn chải, sau đó lau khô, tránh phơi nắng lâu (EVA biến dạng/ngả vàng).",
        "Vết bẩn bám: cục tẩy hoặc cồn lau nhẹ với đế cao su trắng.",
        "Đế bị vàng: dùng kem đánh răng trắng/whitening hoặc gel tẩy trắng đế — hạn chế nắng để không vàng thêm.",
    ],
}

CARE_FAQ = [
    {"q": "Bao lâu nên vệ sinh giày một lần?", "a": "Dạ với giày đi hằng ngày: lau khô 2–3 ngày/lần, vệ sinh sâu 2-4 tuần/lần; giày trắng nên vệ sinh 2 tuần/lần. Giày da thì lau + dưỡng mỗi tháng là đủ ạ."},
    {"q": "Giày bị ố vàng ở đế thì xử lý sao?", "a": "Dạ do oxy hóa foam/cao su. Anh/chị dùng kem đánh răng trắng + bàn chải đánh nhẹ; nặng hơn thì dùng gel tẩy trắng chuyên dụng, phơi trong bóng mát. Quan trọng là PHÒNG trước: tránh nắng trực tiếp, lau khô ngay sau khi dính nước bẩn ạ."},
    {"q": "Giày bị bong keo thì dán lại được không?", "a": "Dạ được ạ. Bên shop dán keo miễn phí trong 6 tháng bảo hành; nếu do dùng quá lâu, anh/chị có thể dùng keo dính giày chuyên dụng (Barge/Đức-keo 502 loại dẻo) — nhớ làm sạch bề mặt, ép chặt 12 giờ. Không dùng keo 502 thường vì giòn, sẽ bong lại ạ."},
    {"q": "Giày đi mưa về thì xử lý thế nào?", "a": "Dạ: (1) nhét giấy báo/khăn vào trong giày để hút ẩm và giữ form; (2) để khô tự nhiên nơi thoáng mát, KHÔNG hơ máy sấy/nắng nóng (da sẽ nứt, keo bong); (3) khi khô thì vệ sinh, xịt nano/chống thấm; (4) nếu ngâm nước lâu, sau khi khô xử lý khử mùi."},
    {"q": "Giày bị mốc thì làm sao?", "a": "Dạ dùng khăn ẩm pha giấm trắng lau sạch mốc (làm ngoài trời), rồi bôi chút dầu/miếng dưỡng da; phơi nơi khô thoáng có nắng nhẹ sớm. Mốc quay lại nếu để ẩm — cho túi hút ẩm vào tủ giày nhé ạ."},
    {"q": "Giữ form giày như thế nào?", "a": "Dạ: nhét cây giữ form (shoe tree) hoặc giấy báo khi không dùng; không chồng giày lên nhau; tủ thoáng, có gói hút ẩm. Giày da nên kê cây nắp ngang để form không bẹp ạ."},
    {"q": "Dây giày trắng bị bẩn giặt thế nào?", "a": "Dạ tháo dây, ngâm nước ấm + bột giặt 15 phút, chà nhẹ, có thể ngâm thêm với baking soda; không dùng thuốc tẩy mạnh với dây màu. Dây trắng bẩn cứng đầu thì thay dây mới — shop có dây các màu 30–50k ạ."},
    {"q": "Lót giày (insole) có nên giặt không?", "a": "Dạ lót bẩn/mùi thì GIẶT TAY nhẹ với xà phòng, không máy giặt; phơi khô hoàn toàn mới lắp lại. Lót cao su nhanh mùi thì nên thay mới mỗi 6–12 tháng — shop có lót than tre/orthopedic 80–150k ạ."},
    {"q": "Có nên dùng xịt nano/phủ chống thấm không?", "a": "Dạ CÓ, hiệu quả rõ nhất với da lộn, canvas và giày trắng. Cách dùng: xịt khi giày sạch, khô, cách 20cm, xịt 2 lớp mỏng đều, để khô 24 giờ; phủ lại sau 4–6 tuần (tùy tần suất đi). Lưu ý: xịt nano không thay thế vệ sinh định kỳ ạ."},
    {"q": "Đế giày bị mòn lệch thì xử lý sao?", "a": "Dạ mòn lệch (đặc biệt mép ngoài gót) là dấu hiệu nên thay giày nếu là giày chạy (trên 600–800km). Với giày thời trang, có thể dán đế/gò lại gót ở tiệm sửa giày (30–80k) để đi thêm 6–12 tháng ạ."},
]

# ================================================================ 5. Xu hướng 2026 (dùng để tư vấn mở rộng)
TRENDS_2026 = [
    "Sneaker tối giản 'quiet luxury' lên ngôi: ton-sur-ton trắng/kem/xám, ít logo to, da mịn — đi làm và đi tiệc nhẹ đều được.",
    "Trào lưu Retro/Nostalgia 80s–90s tiếp tục: Samba, Gazelle, Campus 00s, NB 550/530, Dunk tái sinh mạnh ở Gen Z; sneaker 'dày cổ điển' như 9060, Vomero 5 cũng hot.",
    "Y2K chunky vẫn sống nhưng 'mềm hơn': Hoka Clifton/Bondi, On Cloudmonster, NB 9060 — đế dày nhưng nhẹ, thay vì cứng kiểu Triple S.",
    "Giày đế cao/đế bệ nữ (platform) tăng: Converse Run Star Motion, New Balance CT302, giày bệt đế dày phối jeans ống rộng.",
    "Xu hướng bền vững: vật liệu tái chế (Primeblue, Re-Nylon, adidas Terrex), khách trẻ hỏi rõ nguồn gốc — nên nhấn mạnh khi tư vấn.",
    "Da lộn (suede) và houndstooth/denim texture 'lên ngôi' mùa lạnh; giày lông/lined (giày lông) bán rất chạy cuối năm.",
    "Loafer & Mary Jane 'jelly' cho nữ, sneaker nam mũi gọn (low-profile) cho dân văn phòng trẻ.",
    "Xu hướng 'giày cũ giá mới': các bản 'vintage wash' — Golden Goose, Nike 'vintage' Dunk low — khách trẻ chuộng.",
]

# ================================================================ 6. Tình huống tư vấn bán hàng (nhân viên dùng để xử lý khách)
SCENARIOS = [
    {
        "ten": "Khách hỏi mua giày dưới 1 triệu",
        "xu_ly": "Đừng đẩy mẫu đắt ngay. Gợi ý trong tầm: Biti's Hunter (~700k–1.1 triệu), dép Biti's, giày vải Thượng Đình/Ananas sale, giày basic nữ Juno. Nhấn: 'Trong tầm này Biti's Hunter là êm nhất, đế đàn hồi, phù hợp đi học cả ngày.' Nếu khách mặc đẹp hơn, mở comment 'chỉ thêm 300k là có Ananas đế lưu hoá bền hơn hẳn' để nâng nhẹ giá trị đơn.",
    },
    {
        "ten": "Khách phân vân giữa hai mẫu cùng tầm giá",
        "xu_ly": "Hỏi đúng 3 câu: đi hàng ngày hay dịp gì? chân có bè/đau gót không? phối đồ gì nhiều? Rồi tư vấn theo ma trận: êm+bền→A, form gọn+trend→B. Cho khách thử cả hai cùng lúc và so sánh trực tiếp, đó là cách chốt nhanh nhất.",
    },
    {
        "ten": "Khách chê 'đắt quá, shop khác rẻ hơn'",
        "xu_ly": "Xác nhận cảm nhận ('Dạ em hiểu, giá cũng là chuyện lớn ạ'), rồi mở giá trị: chính hãng có bill/check mã, bảo hành keo-đế 6 tháng, đổi size miễn phí, hỗ trợ vệ sinh. Nếu vẫn còn chênh lệch nhỏ, mời khách nhận quà nhỏ (xịt nano/dây giày) để chốt. Không hạ giá bằng mọi giá — giữ mặt bằng chung.",
    },
    {
        "ten": "Khách hỏi giày cho người đứng nhiều (bảo vệ, phục vụ, bệnh viện)",
        "xu_ly": "Ưu tiên đệm êm + nhẹ + thoáng: Skechers GOwalk/Arch Fit, Nike Air Force 1 React, Hoka Bondi/Clifton, Biti's Hunter X nhẹ. Khuyến nghị: chọn size dư nửa size, thêm lót than tre, và mua 2 đôi luân phiên để giày khô. Đừng bán giày đế cứng chỉ vì đẹp.",
    },
    {
        "ten": "Khách hỏi giày chạy bộ lần đầu, ngân sách 2–3 triệu",
        "xu_ly": "Đừng dọa khách bằng thuật ngữ. Hỏi: chạy 3–5km hay 10km+, chạy đường nhựa hay công viên, có đau gối không? Gợi ý: Nike Revolution 7/Pegasus 40 sale, Puma Velocity Nitro, Asics GT-2000/Cumulus. Nhấn: giày chạy quan trọng đúng size (dư 1–1.5cm) + đệm theo cân nặng.",
    },
    {
        "ten": "Khách nữ hỏi giày đi làm văn phòng, hạn chế giày thể thao cục súc",
        "xu_ly": "Gợi ý: sneaker da trắng form gọn (NB 574, Superstar, Chuck 70 low), loafer sneaker, giày bệt đế dày Vascara. Màu trắng/kem/đen dễ phối. Nhấn đế cao 2–3cm tôn dáng nhưng đi êm cả ngày.",
    },
    {
        "ten": "Khách mua giày tặng bạn gái/người thân nhưng không rõ size",
        "xu_ly": "Hỏi size giày hiện tại của người nhận, quy đổi theo cm, và nói rõ chính sách đổi size 7 ngày. An toàn nhất: mua tại shop có đổi, giữ bill + hộp nguyên. Gợi ý mẫu 'khó chọn sai' (form chuẩn, màu trung tính) như NB 550 trắng, AF1 trắng, Chuck 70.",
    },
    {
        "ten": "Khách mang giày mua 3 tuần trước quay lại chê bung keo",
        "xu_ly": "Xin lỗi trước ('Dạ em rất tiếc vì trải nghiệm này ạ'), kiểm tra lỗi thuộc sản xuất hay do sử dụng, chụp ảnh lưu lại. Trong 6 tháng bảo hành keo/đế do NSX → dán keo chuyên dụng miễn phí hoặc đổi đôi nếu lỗi nặng. Ghi nhận vào sổ để báo hãng. Luôn giữ thái độ tích cực — khách quay lại đòi bảo hành là khách còn quay lại.",
    },
    {
        "ten": "Khách hỏi hàng 'siêu cấp/1:1' có bán không",
        "xu_ly": "Trả lời dứt khoát nhưng không phán xét: 'Dạ em chỉ bán hàng chính hãng ạ'. Giải thích ngắn gọn vì sao nên mua thật: bảo hành, độ bền, an toàn chân. Nếu khách tò mò về cách phân biệt, đưa 2–3 tips check (tem, đường may) để tạo niềm tin chuyên môn.",
    },
    {
        "ten": "Khách hỏi size hot (41–42 nam, 37–38 nữ) nhưng hết hàng",
        "xu_ly": "Đừng trả lời 'hết' rồi im. Đưa 3 hành động: (1) kiểm tra hàng ở chi nhánh khác trong 2 phút; (2) đặt trước 7–14 ngày (cọc 200k); (3) gợi ý mẫu tương tự đang có đủ size, mời khách thử để so sánh. Luôn ghi lại số điện thoại để báo khi hàng về.",
    },
    {
        "ten": "Khách lớn tuổi cần giày đi bộ nhẹ nhàng, chân bè, thích chắc chắn",
        "xu_ly": "Ưu tiên: gót mềm dễ xỏ (Skechers Slip-ins, GOwalk), form bè (NB 2E/4E, Asics), lót chống trượt, đế bám. Tránh đế quá cao/cứng, tránh giày buộc dây phức tạp. Đo chân tại shop vì chân người lớn tuổi có thể tăng size.",
    },
    {
        "ten": "Khách hỏi về mẫu 'đang trend trên TikTok' mà shop không có",
        "xu_ly": "Không dìm mẫu đó ('Dạ mẫu đó đẹp thật ạ'), nhưng lái sang tương đương đang có: ví dụ khách hỏi Adidas Samba → gợi ý Gazelle/Ananas 'samba-like'; hỏi Jumpman → gợi ý NB 550/Dunk; hỏi On Cloud → gợi ý Cloudtilt/Cloud 5 tùy kho. Chụp ảnh mẫu trend để đặt về nếu khách chốt cọc.",
    },
    {
        "ten": "Khách chốt 2 đôi trở lên / mua cả gia đình",
        "xu_ly": "Chào giá combo: giảm 5% đôi thứ 2 cùng bill hoặc tặng phụ kiện (xịt nano + dây giày + tất). Nhấn tiết kiệm ship và thời gian. Giữ khách bằng cách xin Zalo để thông báo sale — dùng 'bán nối' hợp lý, không hối thúc lộ liễu.",
    },
    {
        "ten": "Khách hỏi giày đi mưa Sài Gòn",
        "xu_ly": "Đừng bán canvas/da lộn nếu khách đi mưa hằng ngày. Gợi ý: Crocs Classic, sandal, boot Dr. Martens/Timberland (đế kín), giày GORE-TEX/giả da bền nước. Kèm mẹo: xịt chống thấm + mang tất dự phòng; dạy khách cách sấy gián tiếp bằng giấy báo.",
    },
    {
        "ten": "Khách mua giày cho con nhỏ",
        "xu_ly": "Đo chân bé bằng giấy; chọn dư 0.5–1cm; ưu tiên đế mềm gập được, quai dính dễ mang, vật liệu thoáng. Nhắc bố mẹ đo lại mỗi 3–6 tháng. Nếu bé còn nhỏ, chọn cùng 1 đôi 2 màu — trẻ con thích và khách dễ chốt.",
    },
]

# ================================================================ 7. Chính sách shop (MẪU – cần sửa theo shop thật)
STORE_POLICY = [
    "Chính sách bảo hành: 6 tháng cho lỗi keo/đế do nhà sản xuất; hỗ trợ vệ sinh miễn phí 1 lần trong 3 tháng đầu; không bảo hành hư hại do sử dụng.",
    "Đổi trả: đổi size/mẫu trong 7 ngày với giày chưa sử dụng ngoài trời, còn hộp/tem; đổi 1 lần miễn phí.",
    "Vận chuyển: nội thành 1–2 ngày; toàn quốc 2–4 ngày; freeship cho đơn từ 1 triệu; được đồng kiểm.",
    "Thanh toán: COD, chuyển khoản, Momo/ZaloPay, thẻ; trả góp 0% qua thẻ tín dụng từ 3 triệu.",
    "Xuất hóa đơn VAT cho công ty theo yêu cầu.",
]

# ================================================================ 8. Gợi ý bán kèm (cross-sell)
CROSS_SELL = [
    ("Với giày trắng/vải sáng", "Xịt nano chống bám bẩn + bàn chải chuyên dụng + dung dịch vệ sinh (combo 150k)."),
    ("Với giày da lộn", "Bàn chải cao su + xịt protector (combo 180k); nói rõ 'bắt buộc phủ khi mới mua'."),
    ("Với giày phải đi cả ngày", "Lót than tre/orthopedic 80–150k; lót hỗ trợ vòm cho chân bè 120k."),
    ("Với giày da/boot mới", "Gót dán silicon chống chột + kem dưỡng da (combo 120k)."),
    ("Với giày chạy bộ", "Tất chạy chuyên dụng 60–120k (giảm chai chân, chống mùi) + túi đựng giày thoáng."),
    ("Với khách mua đôi vai", "Cây giữ form (shoe tree) 90k; túi hút ẩm 20k/gói cho tủ giày."),
    ("Với trẻ em", "Dán gót chống tuột + tất họa tiết; nhắc phụ huynh đo lại chân 3–6 tháng/lần."),
    ("Với khách mua quà", "Túi giấy đẹp + thiệp miễn phí + gói xịt/khăn bọc giày để quà 'đủ vị' hơn."),
]
