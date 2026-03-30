#!/usr/bin/env python3
"""
诊断当前API调用环境（安全脱敏输出）

- 合并当前进程环境变量与项目 .env（不修改进程环境）
- 给出实际会使用的 base_url 与默认模型推断
- 检查反审查与图片生成功能相关配置
"""
import os
import json
import pathlib
import importlib.util


def load_env_file(path: pathlib.Path) -> dict:
    data = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip().strip('"').strip("'")
        data[k.strip()] = v
    return data


from typing import Optional


def mask(val: Optional[str]) -> Optional[str]:
    if not val:
        return None
    if len(val) <= 6:
        return "*" * len(val)
    return f"{val[:4]}...{val[-2:]}"


def has_module(mod: str) -> bool:
    return importlib.util.find_spec(mod) is not None


def main() -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    env_path = root / ".env"
    file_kv = load_env_file(env_path)

    # Gather keys of interest
    keys = [
        "OPENAI_API_KEY", "OPENAI_API_BASE", "OPENAI_BASE_URL", "OPENAI_MODEL",
        "YUNWU_API_KEY", "YUNWU_API_BASE", "YUNWU_BASE_URL",
        "OPENROUTER_API_KEY", "OPENROUTER_BASE_URL", "OPENROUTER_MODEL",
        "CLAUDE_API_KEY", "CLAUDE_API_BASE",
        "MODEL_NAME", "BACKUP_MODEL_NAME",
        "WRITER_MODEL", "RESEARCH_MODEL", "SCORER_MODEL",
    ]

    merged = {}
    for k in keys:
        v_env = os.getenv(k)
        v_file = file_kv.get(k)
        v = v_env if v_env is not None else v_file
        src = "env" if v_env is not None else (".env" if v_file is not None else None)
        merged[k] = {
            "present": v is not None,
            "value_preview": mask(v),
            "source": src,
        }

    # openai_client.get_openai_client selection logic
    openai_api_key = os.getenv("OPENAI_API_KEY") or file_kv.get("OPENAI_API_KEY")
    yunwu_api_key = os.getenv("YUNWU_API_KEY") or file_kv.get("YUNWU_API_KEY")
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY") or file_kv.get("OPENROUTER_API_KEY")

    selected_api_key_name = None
    selected_api_key_val = None
    for name, val in (
        ("OPENAI_API_KEY", openai_api_key),
        ("YUNWU_API_KEY", yunwu_api_key),
        ("OPENROUTER_API_KEY", openrouter_api_key),
    ):
        if val:
            selected_api_key_name = name
            selected_api_key_val = val
            break

    base_url = (
        os.getenv("OPENAI_API_BASE")
        or os.getenv("OPENAI_BASE_URL")
        or os.getenv("YUNWU_BASE_URL")
        or os.getenv("OPENROUTER_BASE_URL")
        or file_kv.get("OPENAI_API_BASE")
        or file_kv.get("OPENAI_BASE_URL")
        or file_kv.get("YUNWU_BASE_URL")
        or file_kv.get("OPENROUTER_BASE_URL")
    )

    if not base_url and selected_api_key_val:
        if selected_api_key_val.lower().find("yunwu") != -1 or selected_api_key_val.startswith("sk-6MT0V7g6"):
            base_url = "https://yunwu.ai/v1"
        elif openrouter_api_key:
            base_url = "https://openrouter.ai/api/v1"

    # Default model (from code logic)
    openai_model_env = os.getenv("OPENAI_MODEL") or file_kv.get("OPENAI_MODEL")
    if openai_model_env:
        default_model = openai_model_env
    else:
        if base_url and "yunwu.ai" in base_url:
            default_model = "qwen3-235b-a22b-think"
        elif (os.getenv("OPENROUTER_API_KEY") or file_kv.get("OPENROUTER_API_KEY")):
            default_model = (
                os.getenv("OPENROUTER_MODEL")
                or file_kv.get("OPENROUTER_MODEL")
                or "anthropic/claude-3.5-sonnet"
            )
        else:
            default_model = "gpt-4o-mini"

    # Anti-censorship models
    primary_model = (
        os.getenv("MODEL_NAME") or file_kv.get("MODEL_NAME") or "qwen3-235b-a22b-think"
    )
    backup_model = (
        os.getenv("BACKUP_MODEL_NAME")
        or file_kv.get("BACKUP_MODEL_NAME")
        or "claude-sonnet-4-20250514-thinking"
    )
    claude_api_key = os.getenv("CLAUDE_API_KEY") or file_kv.get("CLAUDE_API_KEY")
    claude_base = (
        os.getenv("CLAUDE_API_BASE")
        or file_kv.get("CLAUDE_API_BASE")
        or "https://api.anthropic.com"
    )

    # Image generation expectation (ImageGenerationAgent uses yunwu gpt-image-1)
    image_ok = bool(
        base_url and "yunwu.ai" in base_url and selected_api_key_name in ("OPENAI_API_KEY", "YUNWU_API_KEY")
    )

    libs = {
        "openai": has_module("openai"),
        "tavily": has_module("tavily"),
        "dotenv": has_module("dotenv"),
    }

    result = {
        "cwd": str(pathlib.Path().resolve()),
        "project_env_file": str(env_path) if env_path.exists() else None,
        "keys": merged,
        "selection": {
            "selected_api_key_name": selected_api_key_name,
            "selected_api_key_preview": mask(selected_api_key_val) if selected_api_key_val else None,
            "effective_base_url": base_url,
            "default_text_model": default_model,
            "writer_model": os.getenv("WRITER_MODEL") or file_kv.get("WRITER_MODEL") or default_model,
            "research_model": os.getenv("RESEARCH_MODEL") or file_kv.get("RESEARCH_MODEL") or "gpt-3.5-turbo",
            "scorer_model": os.getenv("SCORER_MODEL") or file_kv.get("SCORER_MODEL") or "gpt-4o-mini",
            "anti_censorship_primary": primary_model,
            "anti_censorship_backup": backup_model,
            "claude_key_present": bool(claude_api_key),
            "claude_base": claude_base,
            "image_model": "gpt-image-1",
            "image_env_sane_for_yunwu": image_ok,
        },
        "libs_available": libs,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
