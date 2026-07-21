import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qa_server import _ask, _init_engine, _load_dotenv

_load_dotenv()
_init_engine(ROOT / "_scratch/run-ad5s/chroma_captioned", str(ROOT / "_scratch/modelscope/BAAI/bge-m3"))
for q in ["离合打不开", "离合钥匙拧不开", "脱门也打不开离合 伸太过"]:
    hits = (_ask(q, use_llm=False).get("hits") or [])[:3]
    print(f"\n=== {q} ===")
    for i, h in enumerate(hits, 1):
        print(f"  #{i} {h.get('group_id')} {h.get('score', 0):.3f} | {h.get('question', '')[:55]}")
