"""
Utils package initialization
"""

from .platform_config import (
    PLATFORM_CONFIGS,
    VIDEO_SPECS,
    get_platform_config,
    get_video_spec,
    get_content_prompt_template,
    get_title_generation_prompt,
)

from .quality_metrics import (
    calculate_readability_score,
    calculate_keyword_density,
    calculate_engagement_potential,
    calculate_seo_score,
    calculate_platform_adaptation_score,
    evaluate_content_quality,
)

__all__ = [
    # Platform config
    "PLATFORM_CONFIGS",
    "VIDEO_SPECS", 
    "get_platform_config",
    "get_video_spec",
    "get_content_prompt_template",
    "get_title_generation_prompt",
    # Quality metrics
    "calculate_readability_score",
    "calculate_keyword_density",
    "calculate_engagement_potential",
    "calculate_seo_score",
    "calculate_platform_adaptation_score",
    "evaluate_content_quality",
]
