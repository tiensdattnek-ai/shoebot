# -*- coding: utf-8 -*-
"""
knowledge_base.py – GOM TẤT CẢ kiến thức giày về một mối.
Cách dùng:
    python data/knowledge_base.py            # in thống kê + xuất knowledge_base.json (tùy chọn)
    python -c "from data.knowledge_base import ALL_BRANDS; print(len(ALL_BRANDS))"

Thêm hãng/công nghệ mới → chỉ cần thêm dict trong file kb tương ứng, mọi script khác tự có.
"""

import os
import sys
import json

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

try:
    from kb.brands_intl import INTL_BRANDS
    from kb.brands_perf import PERF_BRANDS
    from kb.brands_lux import LUX_BRANDS
    from kb.brands_vn import VN_BRANDS
    from kb.tech import TECHS
    from kb.sizing import (SIZE_TABLE, ADIDAS_TABLE, ADIDAS_NOTE, KID_TABLE, KID_NOTE,
                           FIT_NOTES, HOW_TO_MEASURE, SIZE_FAQ)
    from kb.support import (GENERAL_FAQ, FAKE_CHECK_GENERAL, COMPARISONS, CARE, CARE_FAQ,
                            TRENDS_2026, SCENARIOS, STORE_POLICY, CROSS_SELL)
except ImportError:  # khi chạy từ thư mục shoebot/
    from data.kb.brands_intl import INTL_BRANDS
    from data.kb.brands_perf import PERF_BRANDS
    from data.kb.brands_lux import LUX_BRANDS
    from data.kb.brands_vn import VN_BRANDS
    from data.kb.tech import TECHS
    from data.kb.sizing import (SIZE_TABLE, ADIDAS_TABLE, ADIDAS_NOTE, KID_TABLE, KID_NOTE,
                                FIT_NOTES, HOW_TO_MEASURE, SIZE_FAQ)
    from data.kb.support import (GENERAL_FAQ, FAKE_CHECK_GENERAL, COMPARISONS, CARE, CARE_FAQ,
                                 TRENDS_2026, SCENARIOS, STORE_POLICY, CROSS_SELL)

# ------------------------------------------------------------------ Tập hợp
GROUPS = {
    "the_thao_quoc_te": INTL_BRANDS,
    "hieu_nang_outdoor": PERF_BRANDS,
    "hang_hieu_luxury": LUX_BRANDS,
    "viet_nam": VN_BRANDS,
}
ALL_BRANDS = INTL_BRANDS + PERF_BRANDS + LUX_BRANDS + VN_BRANDS
BRAND_BY_ID = {b["id"]: b for b in ALL_BRANDS}

# nhóm chuyên môn – dùng để chọn câu hỏi phù hợp
RUNNING_BRANDS = {"nike", "adidas", "asics", "hoka", "brooks", "saucony", "mizuno", "newbalance",
                  "puma", "underarmour", "reebok", "on", "salomon"}
LUXURY_IDS = {b["id"] for b in LUX_BRANDS}
VN_IDS = {b["id"] for b in VN_BRANDS}
THOI_TRANG_LIFESTYLE = {"nike", "adidas", "puma", "newbalance", "converse", "vans", "fila",
                        "jordan", "reebok", "skechers", "mlb", "palladium"}
BOOT_SANDAL = {"drmartens", "timberland", "clarks", "crocs", "birkenstock", "salomon", "merrell"}


def get_brand(brand_id: str) -> dict:
    return BRAND_BY_ID[brand_id]


def all_models():
    """Trả về [(brand_dict, model_dict), ...] cho mọi mẫu giày có trong KB."""
    out = []
    for b in ALL_BRANDS:
        for m in b.get("mau_icon", []) or b.get("models", []):
            out.append((b, m))
    return out


def stats() -> dict:
    models = all_models()
    return {
        "so_hang": len(ALL_BRANDS),
        "so_hang_theo_nhom": {k: len(v) for k, v in GROUPS.items()},
        "so_mau": len(models),
        "so_cong_nghe": len(TECHS),
        "so_faq": len(GENERAL_FAQ),
        "so_tinh_huong": len(SCENARIOS),
        "so_so_sanh": len(COMPARISONS),
        "so_chu_de_cham_soc": len(CARE),
        "so_cau_hoi_size": len(SIZE_FAQ),
        "so_buoc_do_chan": len(HOW_TO_MEASURE),
        "so_chinh_sach": len(STORE_POLICY),
        "so_ban_kem": len(CROSS_SELL),
    }


def dump_json(path: str = "knowledge_base.json"):
    data = {
        "brands": ALL_BRANDS,
        "groups": {k: [b["id"] for b in v] for k, v in GROUPS.items()},
        "techs": TECHS,
        "size_table": SIZE_TABLE,
        "adidas_table": ADIDAS_TABLE,
        "adidas_note": ADIDAS_NOTE,
        "kid_table": KID_TABLE,
        "kid_note": KID_NOTE,
        "fit_notes": FIT_NOTES,
        "how_to_measure": HOW_TO_MEASURE,
        "size_faq": SIZE_FAQ,
        "general_faq": GENERAL_FAQ,
        "fake_check_general": FAKE_CHECK_GENERAL,
        "comparisons": COMPARISONS,
        "care": CARE,
        "care_faq": CARE_FAQ,
        "trends_2026": TRENDS_2026,
        "scenarios": SCENARIOS,
        "store_policy": STORE_POLICY,
        "cross_sell": CROSS_SELL,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return os.path.abspath(path)


if __name__ == "__main__":
    s = stats()
    print("=" * 60)
    print("KNOWLEDGE BASE – GIÀY / SNEAKER")
    print("=" * 60)
    for k, v in s.items():
        print(f"  {k}: {v}")
    print("-" * 60)
    print("Hãng theo nhóm:")
    for k, v in GROUPS.items():
        print(f"  • {k} ({len(v)}): {', '.join(b['ten'] for b in v)}")
    p = dump_json(os.path.join(_HERE, "knowledge_base.json"))
    print(f"\nĐã xuất: {p}")
