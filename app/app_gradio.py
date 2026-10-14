#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app_gradio.py – Giao diện web cho ShoeBot (dùng để demo/nội bộ).

    pip install gradio
    python app/app_gradio.py --model Qwen/Qwen2.5-3B-Instruct --adapter out/shoebot-lora/final
    python app/app_gradio.py --model out/shoebot-merged --share     # tạo link công khai tạm thời

Mẹo: trên máy nhiều người dùng chung, thêm --load_in_4bit để tiết kiệm VRAM.
"""

import argparse
import os
import sys

import torch

SYSTEM = ("Bạn là ShoeBot – trợ lý bán hàng của một chuỗi bán lẻ giày/sneaker tại Việt Nam. "
          "Trả lời ngắn gọn, thân thiện, xưng 'em', gọi khách là 'anh/chị', thông tin thực tế, "
          "gợi ý bước tiếp theo để chốt đơn.")

EXAMPLES = [
    "Chân em 25cm, chân bè, đi Samba size gì ạ?",
    "So sánh Asics Gel-Kayano và Gel-Nimbus giúp em",
    "Ngân sách 2 triệu mua giày đi học thì chọn đôi nào?",
    "Cách check Nike Air Force 1 chính hãng?",
    "Giày da lộn bị dính bùn xử lý thế nào?",
    "Khách đứng nhiều cả ngày nên tư vấn giày gì dưới 3 triệu?",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct")
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--load_in_4bit", action="store_true")
    ap.add_argument("--max_new_tokens", type=int, default=400)
    ap.add_argument("--temperature", type=float, default=0.3)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=7860)
    ap.add_argument("--share", action="store_true")
    args = ap.parse_args()

    try:
        import gradio as gr
    except ImportError:
        sys.exit("Chưa có gradio. Cài trước: pip install gradio")

    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "train"))
    from train_lora import make_tokenizer, load_model

    print("Đang nạp model…")
    tok = make_tokenizer(args.model)
    model = load_model(args.model, args.load_in_4bit, for_training=False)
    if args.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, args.adapter)
        print("→ Đã gắn adapter:", args.adapter)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.eval()
    try:
        model.to(device)
    except Exception:
        pass

    @torch.no_grad()
    def chat_fn(message, history):
        msgs = [{"role": "system", "content": SYSTEM}]
        for h in history or []:
            if isinstance(h, dict):
                msgs.append({"role": h.get("role", "user"), "content": h.get("content", "")})
            else:  # định dạng cũ (tuple)
                u, a = h
                msgs += [{"role": "user", "content": u}, {"role": "assistant", "content": a}]
        msgs.append({"role": "user", "content": message})
        enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt")
        ids = enc["input_ids"] if hasattr(enc, "input_ids") else enc
        ids = ids.to(device)
        out = model.generate(ids, max_new_tokens=args.max_new_tokens, do_sample=args.temperature > 0,
                             temperature=args.temperature, top_p=0.9,
                             pad_token_id=tok.pad_token_id, eos_token_id=tok.eos_token_id)
        return tok.decode(out[0][ids.shape[-1]:], skip_special_tokens=True).strip()

    demo = gr.ChatInterface(
        fn=chat_fn,
        title="👟 ShoeBot – Tư vấn giày",
        description="Hỏi về hãng giày, mẫu hot, size, giá tham khảo, check chính hãng, vệ sinh & bảo quản. "
                    "Bot trả lời theo dữ liệu của shop; giá chỉ mang tính tham khảo.",
        examples=EXAMPLES,
    )
    demo.launch(server_name=args.host, server_port=args.port, share=args.share)


if __name__ == "__main__":
    main()
