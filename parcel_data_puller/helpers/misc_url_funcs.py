from typing import Dict


def generate_direct_url(template: str, data: Dict[str, str]) -> str:
    for key, value in data.items():
        placeholder = f"[{key}]"
        template = template.replace(placeholder, str(value))
    return template
