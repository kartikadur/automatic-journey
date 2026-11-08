from pathlib import Path

import yaml

SKILL_DIRS = [
    Path.cwd() / ".agent" / "skills",
    Path.home() / ".agent" / "skills",
]


def find_skills():
    """Find and map available skills."""
    skills = {}

    for directory in SKILL_DIRS:
        if not directory.exists():
            continue

        for path in sorted(directory.glob("*/SKILL.md")):
            try:
                raw_text = path.read_text(encoding="utf-8")
                parts = raw_text.split("---", 2)
                if len(parts) < 3:
                    continue
                _, frontmatter, _ = parts
                skill_info = yaml.safe_load(frontmatter) or {}
            except (OSError, ValueError, yaml.YAMLError):
                continue

            skill_name = skill_info.get("name")
            if skill_name:
                skills[skill_name] = {
                    "path": str(path),
                    "description": skill_info.get("description", ""),
                }

    return skills


SKILLS = find_skills()


def skills_prompt():
    """Generate a prompt string listing available skills."""
    if not SKILLS:
        return "No skills available."

    prompt_lines = ["Available skills:"]
    prompt_lines.extend(
        f"- {skill_name}: {skill_info.get('description')}"
        for skill_name, skill_info in SKILLS.items()
    )

    return "\n".join(prompt_lines)


def read_skill(skill_name):
    """Read the content of a skill's SKILL.md file."""
    skill_info = SKILLS.get(skill_name)
    if not skill_info:
        return f"Skill '{skill_name}' not found."

    skill_path = Path(skill_info.get("path"))
    if not skill_path.exists():
        return f"Skill file for '{skill_name}' does not exist."

    try:
        return skill_path.read_text(encoding="utf-8")
    except OSError as exc:
        return f"Could not read skill '{skill_name}': {exc}"


if __name__ == "__main__":
    print(skills_prompt())