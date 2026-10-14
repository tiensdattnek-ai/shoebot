# 👟 ShoeBot – AI tư vấn/bán giày (fine-tune LoRA)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tiensdattnek-ai/shoebot/blob/main/notebooks/colab_train_shoebot.ipynb)
[![validate](https://github.com/tiensdattnek-ai/shoebot/actions/workflows/validate.yml/badge.svg)](https://github.com/tiensdattnek-ai/shoebot/actions/workflows/validate.yml)

### ▶️ [**BẤM VÀO ĐÂY ĐỂ TRAIN TRÊN GOOGLE COLAB**](https://colab.research.google.com/github/tiensdattnek-ai/shoebot/blob/main/notebooks/colab_train_shoebot.ipynb)
> Chỉ cần: mở link → `Runtime → Change runtime type → T4 GPU` → `Runtime → Run all` → chờ ~30–60 phút → tải model về.
> **Không cần cài gì, không cần GPU riêng, không cần upload file** — notebook tự clone code từ GitHub.

Hoặc copy link này: `https://colab.research.google.com/github/tiensdattnek-ai/shoebot/blob/main/notebooks/colab_train_shoebot.ipynb`

---

Bộ kit hoàn chỉnh để **train một AI chuyên hỏi–đáp về các hãng giày** theo giọng nhân viên bán hàng Việt Nam:
nguồn gốc hãng · mẫu giày hot · giá tham khảo · chọn size (US/UK/EU/cm) · phân biệt chính hãng · vệ sinh – bảo quản ·
so sánh · tư vấn theo nhu cầu & ngân sách · xử lý tình huống bán hàng.

> Đã kiểm thử toàn bộ đường ống trên máy này: sinh dataset ✓ · train thử trên CPU ✓ · xuất báo cáo ✓
> (máy chạy thử không có GPU nên phần train thật (1.5B–7B) bạn chạy trên **Google Colab free** hoặc GPU của bạn).

---

## 1. Có gì trong bộ kit

```
shoebot/
├── data/                        # ① KIẾN THỨC + DATASET
│   ├── kb/                      #    knowledge base (43 hãng, 107 mẫu giày, 40 công nghệ…)
│   │   ├── brands_intl.py       #    Nike, Adidas, Puma, New Balance, Asics, Jordan, Vans… (12)
│   │   ├── brands_perf.py       #    Hoka, On, Salomon, Brooks, Saucony, Dr.Martens, Crocs… (13)
│   │   ├── brands_lux.py        #    Gucci, LV, Balenciaga, Dior, Chanel, Prada… (12)
│   │   ├── brands_vn.py         #    Biti's, Thượng Đình, Ananas, Vascara, Juno, Asia Sports (6)
│   │   ├── tech.py              #    công nghệ đệm/đế/thân (Air, Boost, GEL, Wave, LiteFlex…)
│   │   ├── sizing.py            #    bảng size US–UK–EU–cm (nam/nữ/trẻ em) + form từng hãng
│   │   └── support.py           #    FAQ, check chính hãng, vệ sinh, xu hướng 2026, tình huống bán hàng
│   ├── knowledge_base.py        #    gom KB + thống kê + xuất JSON
│   ├── build_dataset.py         #    ★ sinh dataset chat từ KB (chạy lại bất cứ lúc nào sau khi sửa KB)
│   ├── handcrafted_qa.jsonl     #    40 hội thoại viết tay (giọng khách thật, tình huống khó)
│   └── knowledge_base.json      #    KB dạng JSON (nếu bạn muốn dùng cho RAG/app khác)
├── dataset/                     # ② DATASET ĐÃ SINH SẴN
│   ├── train.jsonl              #    1.553 mẫu train
│   ├── val.jsonl                #    81 mẫu validation
│   └── build_report.md          #    thống kê chi tiết
├── train/
│   ├── train_lora.py            # ③ TRAIN THẬT (LoRA/QLoRA) – script chính, ~200 dòng dễ đọc
│   ├── train_unsloth.py         #    bản Unsloth (nhanh ~2x trên Colab, xuất GGUF chạy Ollama)
│   ├── merge_adapter.py         #    gộp adapter vào model để deploy
│   └── smoke_test.py            #    kiểm tra toàn bộ pipeline trên CPU (đã pass ✓)
├── eval/
│   ├── evaluate.py              # ④ CHẤM ĐIỂM model trước/sau khi train
│   └── eval_questions.jsonl     #    (bộ 32 câu, chấm theo nhóm từ khoá)
├── app/
│   ├── chat_cli.py              # ⑤ CHAT thử trên terminal
│   ├── app_gradio.py            #    giao diện web cho nhân viên/nội bộ
│   └── build_offline.py         #    ★ xuất bản HTML tra cứu offline (không cần GPU)
├── app/shoebot_offline.html     # ⑥ BẢN DÙNG NGAY: mở bằng trình duyệt là tra cứu được (556 mục)
├── app/dev_test_search.js       #    script Node tự kiểm tra chất lượng tìm kiếm của bản offline
├── notebooks/colab_train_shoebot.ipynb   # ⑦ ★★ Notebook Colab 1-CLICK: tự clone repo, train, chấm điểm, tải model
├── requirements.txt
└── README.md (file này)
```

**Quy mô kiến thức:** 43 thương hiệu · 107 mẫu giày tiêu biểu · 40 công nghệ · 25 FAQ · 12 cặp so sánh ·
15 tình huống bán hàng · bảng size nam/nữ/trẻ em · 5 nhóm chất liệu vệ sinh · xu hướng 2025–2026.

---

## 2. Ba cách dùng (chọn theo điều kiện của bạn)

### 🅰️ Không có GPU – dùng ngay bản offline
Mở `app/shoebot_offline.html` bằng Chrome/Edge (điện thoại cũng được). Đây là chatbot tra cứu **chạy offline**,
tìm theo từ khoá có xử lý tiếng Việt + quy đổi size theo cm (556 mục dữ liệu, 255 KB). Không cần cài gì, không cần mạng.
Muốn cập nhật nội dung: sửa KB → `python app/build_offline.py` → file HTML mới.

### 🅱️ Train thật trên Google Colab – 1 CLICK (khuyến nghị, miễn phí)

**Bước 1.** Bấm nút này: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tiensdattnek-ai/shoebot/blob/main/notebooks/colab_train_shoebot.ipynb)
→ hoặc mở link: `https://colab.research.google.com/github/tiensdattnek-ai/shoebot/blob/main/notebooks/colab_train_shoebot.ipynb`

**Bước 2.** Trong Colab: `Runtime → Change runtime type → T4 GPU → Save`

**Bước 3.** `Runtime → Run all` (hoặc Ctrl+F9). Notebook tự động:
1. kiểm tra GPU
2. **tự clone toàn bộ code + dataset từ GitHub này** (không cần upload gì)
3. cài thư viện
4. kiểm tra dữ liệu + chạy smoke test
5. **train** Qwen2.5-3B với QLoRA 4-bit (3 epoch)
6. cho bạn hỏi thử ngay trong notebook
7. chấm điểm model gốc vs đã train
8. gộp model + **tải file zip về máy**

**Bước 4.** Chờ ~30–60 phút. Xong thì để nguyên tab, notebook tự tải `shoebot-lora.zip` về máy bạn.

Muốn train 7B cho giọng tự nhiên hơn? Trong notebook sửa `MODEL = "Qwen/Qwen2.5-7B-Instruct"` (T4 free sẽ lâu ~2–3h, nên dùng Colab Pro/A100 hoặc chạy `train/train_unsloth.py`).

**Chạy bằng terminal trong Colab (nếu bạn thích gõ lệnh):**

```python
!git clone https://github.com/tiensdattnek-ai/shoebot.git /content/shoebot
%cd /content/shoebot
!pip -q install transformers peft datasets accelerate bitsandbytes sentencepiece
!python train/train_lora.py --model Qwen/Qwen2.5-3B-Instruct --load_in_4bit \
    --data_dir dataset --output_dir out/shoebot-lora --epochs 3 --batch_size 2 --grad_accum 8 --max_len 1024
```

### 🅲 Máy có GPU riêng (RTX 3060 12GB trở lên là chạy được)

```bash
git clone https://github.com/tiensdattnek-ai/shoebot.git
cd shoebot
pip install -r requirements.txt

# 0) nếu sửa KB thì sinh lại dataset
python data/build_dataset.py --out dataset

# 1) kiểm tra pipeline trước khi train thật (chạy được cả trên CPU)
python train/smoke_test.py

# 2) train (QLoRA 4-bit cho GPU ≤12GB)
python train/train_lora.py --model Qwen/Qwen2.5-3B-Instruct --load_in_4bit \
    --data_dir dataset --output_dir out/shoebot-lora --epochs 3 \
    --batch_size 2 --grad_accum 8 --max_len 1024

# 3) hỏi thử
python app/chat_cli.py --model Qwen/Qwen2.5-3B-Instruct --adapter out/shoebot-lora/final
```

---

## 3. Dữ liệu huấn luyện

Định dạng chuẩn chat (dùng được với mọi model instruct):

```json
{"messages": [
  {"role": "system", "content": "Bạn là ShoeBot – trợ lý bán hàng giày…"},
  {"role": "user", "content": "Chân em 25cm, chân bè, đi Samba size gì ạ?"},
  {"role": "assistant", "content": "Dạ chân 25cm ≈ US 7.5 nam / EU 40.5 …"}
], "category": "size_convert"}
```

- **1.634 mẫu** (1.553 train + 81 val), 29 nhóm nội dung, câu trả lời dài trung bình ~300 ký tự.
- Có **hội thoại nhiều lượt** (5–9 lượt): tư vấn chọn giày, check hàng, chọn size, so sánh, chăm sóc, khiếu nại, hàng hiệu, tư vấn cho người lớn tuổi, mua quà.
- Khi train, script **chỉ tính loss trên phần trả lời của assistant** (prompt bị mask `-100`) → model học cách trả lời, không học thuộc câu hỏi.

**Thêm dữ liệu của shop bạn** (quan trọng nhất nếu dùng thật):
1. Chính sách thật (bảo hành, đổi trả, freeship, trả góp) → sửa `STORE_POLICY` trong `data/kb/support.py`.
2. Giá/mã sản phẩm thật đang bán → sửa `gia` / `mau_icon` trong `data/kb/*.py`.
3. Hội thoại thật giữa nhân viên và khách → thêm vào `data/handcrafted_qa.jsonl` (mỗi dòng 1 JSON).
4. Chạy lại `python data/build_dataset.py --out dataset` rồi train lại. **Không cần sửa code.**

---

## 4. Đánh giá: model có thực sự tốt lên?

```bash
# Model gốc (baseline)
python eval/evaluate.py --model Qwen/Qwen2.5-3B-Instruct --out out/eval_goc.md

# Model sau fine-tune
python eval/evaluate.py --model Qwen/Qwen2.5-3B-Instruct \
    --adapter out/shoebot-lora/final --out out/eval_finetuned.md
```

Kết quả: bảng điểm theo nhóm từ khoá + **toàn bộ câu trả lời** để bạn đọc và chấm bằng mắt.
Kỳ vọng: model gốc trả lời chung chung, hay nhầm giá/size; model fine-tune trả lời đúng dữ liệu shop,
đúng giọng bán hàng, biết hỏi lại khi thiếu thông tin.

---

## 5. Đưa vào sử dụng

| Cách | Lệnh | Ghi chú |
|---|---|---|
| Terminal | `python app/chat_cli.py --model … --adapter …` | test nhanh, xem từng câu |
| Web nội bộ | `python app/app_gradio.py --model … --adapter … --host 0.0.0.0` | mở từ máy khác trong LAN/qua `--share` |
| Gộp model | `python train/merge_adapter.py --model … --adapter out/shoebot-lora/final --out out/shoebot-merged` | chạy nhanh hơn, không cần peft |
| Chạy máy nhẹ / Ollama | Unsloth `--export_gguf` → `ollama create shoebot -f Modelfile` | GGUF q4_k_m ~2GB cho 3B, chạy CPU/máy yếu |
| Tra cứu offline | mở `app/shoebot_offline.html` | không cần GPU; `node app/dev_test_search.js` để tự kiểm tra tìm kiếm |

Gợi ý tích hợp thực tế: dùng model đã merge làm "bộ não" trả lời, còn **giá/tồn kho thật** nên tra từ hệ thống
bán hàng (RAG/database) — bot chỉ tư vấn và xác nhận, không cam kết giá.

---

## 6. Thời gian & chi phí ước tính (dataset 1.634 mẫu, 3 epoch)

| Model | VRAM (QLoRA 4-bit) | Thời gian trên Colab T4 (free) | Chất lượng |
|---|---|---|---|
| Qwen2.5-1.5B-Instruct | ~4 GB | ~25–40 phút | đủ dùng nội bộ, trả lời ngắn gọn |
| **Qwen2.5-3B-Instruct** ⭐ | ~6–7 GB | ~45–75 phút | **cân bằng nhất – khuyến nghị** |
| Qwen2.5-7B-Instruct | ~10–12 GB | ~2–3 giờ (T4) / ~50 phút (A100) | giọng tự nhiên nhất, hiểu ngữ cảnh tốt |
| Vistral-7B / ViGPT (tiếng Việt) | ~10–12 GB | ~2–3 giờ | tiếng Việt thuần, hợp khách lớn tuổi |

Chi phí: Colab free = 0đ (bị ngắt phiên nếu để lâu); thuê GPU A100 ~1–2 USD/giờ trên các dịch vụ thuê GPU.

---

## 7. Tuỳ chỉnh model khi chạy

| Tham số | Ý nghĩa | Gợi ý |
|---|---|---|
| `--lora_r 16` | "độ rộng" của LoRA | 8–16 (nhẹ) · 32–64 (học nhiều hơn, dễ overfit với data nhỏ) |
| `--epochs 3` | số vòng học | 2–4 với ~1,6k mẫu; xem loss val nếu tăng → giảm epoch |
| `--max_len 1024` | độ dài tối đa (token) | 512 cho 1.5B/GPU 8GB; 2048 nếu câu trả lời dài |
| `--lr 2e-4` | learning rate | 1e-4 nếu thấy model "học vẹt"; 3e-4 nếu hội thoại chưa theo |
| `--batch_size/--grad_accum` | batch hiệu dụng | hết VRAM → giảm batch, tăng grad_accum (giữ tổng ~16) |
| `--load_in_4bit` | QLoRA | BẬT trên GPU ≤12GB |

---

## 8. Câu hỏi thường gặp / xử lý lỗi

**1) `CUDA out of memory`** → `--batch_size 1 --grad_accum 16 --max_len 512`, hoặc dùng model 1.5B, hoặc QLoRA `--load_in_4bit`.

**2) Model trả lời lan man, không đúng giọng shop** → tăng `--epochs` lên 4–5, thêm 30–100 hội thoại thật vào
`handcrafted_qa.jsonl`, và kiểm tra bạn đang load **đúng adapter** khi chat.

**3) Muốn đổi model nền khác** → chỉ cần đổi `--model`: `Qwen/Qwen2.5-7B-Instruct`, `unsloth/Qwen2.5-3B-Instruct`,
`Viet-Mistral/Vistral-7B-Chat`… script tự dò module để gắn LoRA.

**4) Train trên CPU được không?** → Được nhưng rất chậm (1.5B mất nhiều ngày). Hãy dùng Colab/GPU.
`smoke_test.py` chạy CPU chỉ để kiểm tra code.

**5) Giá trong bot có đúng không?** → Giá là **tham khảo thị trường**, bot được dạy luôn nhắc điều này.
Muốn chính xác: cập nhật `gia` trong `data/kb/` theo bảng giá shop, hoặc nối bot với hệ thống giá thật (RAG).

**6) Số liệu/lịch sử hãng có sai không?** → KB do mình tổng hợp từ nguồn công khai (tính đến 10/2026) và luôn ghi rõ
"giá tham khảo". Nếu bạn phát hiện sai, sửa file KB tương ứng rồi build lại dataset — mọi thứ tự đồng bộ.

**7) Ngắt phiên Colab giữa chừng** → adapter được lưu mỗi epoch ở `out/shoebot-lora/checkpoint-*`;
train lại với `--resume` hoặc giảm `--epochs`.

**8) Có vi phạm bản quyền thương hiệu không?** → Nội dung chỉ mô tả khách quan để tư vấn; không dùng logo/hình ảnh
thương hiệu trong sản phẩm thương mại khi chưa được phép. Nên ghi "giá mang tính tham khảo, không phải báo giá chính thức".

---

## 9. Việc nên làm tiếp (để bot "chuẩn shop" hơn)

- [ ] Thay `STORE_POLICY` bằng chính sách thật (bảo hành, đổi trả, freeship, trả góp).
- [ ] Cập nhật `gia` theo bảng giá hiện hành và thêm mã sản phẩm (SKU) đang bán.
- [ ] Bổ sung 50–200 hội thoại thật khách–nhân viên (cả câu khó: mặc cả, đổi trả, so sánh hàng fake).
- [ ] Thêm ảnh/feedback từ khách để mở rộng mục "phối đồ".
- [ ] Khi catalogue > 300 mẫu hoặc giá đổi liên tục → chuyển sang kiến trúc **RAG + fine-tune** (bot giữ giọng nói,
      dữ liệu giá/tồn tra từ database).
- [ ] Đo lại bằng `eval/evaluate.py` sau mỗi lần cập nhật dữ liệu (bộ 32 câu này đủ để phát hiện tụt chất lượng).

---

*Repo: https://github.com/tiensdattnek-ai/shoebot · Sinh tự động kèm kiểm thử ngày 14/10/2026. Toàn bộ code chạy được offline; các bước train thật cần GPU (Colab/GPU của bạn).*
