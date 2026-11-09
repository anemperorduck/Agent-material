# =============================================================================
#  main.py — 入口文件
#
#  运行方式：
#    cd 01-small-llm-function-call-project
#    python main.py
#
#  依赖：pip install openai python-dotenv
#  环境变量：DEEPSEEK_API_KEY（配置在同目录 .env 文件中）
# =============================================================================

import os
import sys

from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

sys.stdout.reconfigure(encoding="utf-8")


class _Tee:
    """把写入内容同时复制到多个流（终端 + 日志文件），类似 Unix tee 命令。"""

    def __init__(self, *streams):
        self._streams = streams

    def write(self, data):
        for stream in self._streams:
            stream.write(data)
        return len(data)

    def flush(self):
        for stream in self._streams:
            stream.flush()


# .env 查找顺序：项目目录优先，仓库根目录兜底（load_dotenv 默认不覆盖已加载的键）
_BASE_DIR = Path(__file__).resolve().parent      # 01-small-llm-function-call-project/
_ROOT_DIR = _BASE_DIR.parents[1]                 # Agent-material/（仓库根目录）
load_dotenv(dotenv_path=_BASE_DIR / ".env")
load_dotenv(dotenv_path=_ROOT_DIR / ".env")

# 同时输出到终端和 log.txt（追加模式；log.txt 位于项目目录下）
_LOG_FILE = open(_BASE_DIR / "log.txt", "a", encoding="utf-8")
sys.stdout = _Tee(sys.stdout, _LOG_FILE)
sys.stderr = _Tee(sys.stderr, _LOG_FILE)

from agent.agent import chat_with_tools  # noqa: E402（需在 load_dotenv 之后导入）


def main() -> None:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("未找到 DEEPSEEK_API_KEY，请在 .env 文件中配置。")

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    print("=" * 60)
    print("LLM Function Calling 小工程")
    print("可用工具：reverse_string / basic_calculator")
    print("输入 'exit' 或 'quit' 退出")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n[你] ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("再见！")
            break
        print("\n\n")
        print("*" * 60)
        print(f"User>\t {user_input}")
        print("*" * 60)
        answer = chat_with_tools(client, user_input)
        print("\n\n")
        print("=" * 60)
        print(f"Assistant>\t {answer}")
        print("*" * 60)
        print(f"\n[助手] {answer}\n{'─' * 60}\n")


if __name__ == "__main__":
    main()
