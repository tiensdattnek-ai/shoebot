#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chat_cli.py – Chat với ShoeBot trên terminal.

    python app/chat_cli.py --model Qwen/Qwen2.5-3B-Instruct                     # model gốc
    python app/chat_cli.py --model Qwen/Qwen2.5-3B-Instruct --adapter out/shoebot-lora/final
    python app/chat_cli.py --model out/shoebot-merged                            # model đã merge
    python app/chat_cli.py --model Qwen/Qwen2.5-3B-Instruct --adapter out/shoebot-lora/final --load_in_4bit

Gõ /reset để xoá ngữ cảnh, /exit để thoát.
"""

import argparse
import os
import sys

import torch

SYSTEM = ("Bạn là ShoeBot – trợ lý bán hàng của một chuỗi bán lẻ giày/sneaker tại Việt Nam. "
          "Trả lời ngắn gọn, thân thiện, xưng 'em', gọi khách là 'anh/chị', thông tin thực tế, "
          "gợi ý bước tiếp theo để chốt đơn.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct")
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--load_in_4bit", action="store_true")
    ap.add_argument("--max_new_tokens", type=int, default=400)
    ap.add_argument("--temperature", type=float, default=0.3)
    ap.add_argument("--top_p", type=float, default=0.9)
    ap.add_argument("--system", default=SYSTEM)
    args = ap.parse_args()

    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "train"))
    from train_lora import make_tokenizer, load_model
    from transformers import TextStreamer

    print("Đang nạp model… (lần đầu sẽ tải vài GB, các lần sau lấy từ cache)")
    tok = make_tokenizer(args.model)
    model = load_model(args.model, args.load_in_4bit, for_training=False)
    if args.adapter:
        from peft import PeftModel
        print(f"→ Gắn LoRA adapter: {args.adapter}")
        model = PeftModel.from_pretrained(model, args.adapter)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.eval()
    try:
        model.to(device)
    except Exception:
        pass
    print(f"✓ Sẵn sàng trên {device}. Gõ câu hỏi (ví dụ: 'Chân em 25cm, chân bè, đi Samba size gì?').")
    print("   /reset = xoá hội thoại, /exit = thoát.\n")

    history = [{"role": "system", "content": args.system}]
    streamer = TextStreamer(tok, skip_prompt=True, skip_special_tokens=True)

    while True:
        try:
            user = input("🧑 Khách: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if not user:
            continue
        if user == "/exit":
            break
        if user == "/reset":
            history = [{"role": "system", "content": args.system}]
            print("(đã xoá ngữ cảnh)\n")
            continue

        history.append({"role": "user", "content": user})
        enc = tok.apply_chat_template(history, add_generation_prompt=True, return_tensors="pt")
        ids = enc["input_ids"] if hasattr(enc, "input_ids") else enc
        ids = ids.to(device)
        gen_kwargs = dict(max_new_tokens=args.max_new_tokens, pad_token_id=tok.pad_token_id,
                          eos_token_id=tok.eos_token_id, streamer=streamer)
        if args.temperature and args.temperature > 0:
            gen_kwargs.update(do_sample=True, temperature=args.temperature, top_p=args.top_p)
        else:
            gen_kwargs.update(do_sample=False)

        print("👟 ShoeBot: ", end="", flush=True)
        with torch.no_grad():
            out = model.generate(ids, **gen_kwargs)
        answer = tok.decode(out[0][ids.shape[-1]:], skip_special_tokens=True).strip()
        history.append({"role": "assistant", "content": answer})
        print("\n")

        # giữ ngữ cảnh gọn (10 lượt gần nhất)
        if len(history) > 21:
            history = [history[0]] + history[-20:]


if __name__ == "__main__":
    main()
