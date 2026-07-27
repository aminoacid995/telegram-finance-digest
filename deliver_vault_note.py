"""Кладёт заметку с дайджестом в Obsidian vault-репозиторий (git push)."""

import datetime
import os
import subprocess
import tempfile

NOTE_DIR = "Resources/finance"


def _run(*args: str, cwd: str) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def write_note_to_vault(text: str) -> None:
    repo_url = os.environ["VAULT_REPO_URL"]
    today = datetime.date.today().isoformat()
    filename = f"life notes финансовый дайджест – {today}.md"

    with tempfile.TemporaryDirectory() as workdir:
        _run("git", "clone", "--depth", "1", repo_url, workdir, cwd=".")

        note_dir = os.path.join(workdir, NOTE_DIR)
        os.makedirs(note_dir, exist_ok=True)
        note_path = os.path.join(note_dir, filename)
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(f"# Финансовый дайджест — {today}\n\n{text}\n")

        _run("git", "config", "user.email", "digest-bot@users.noreply.github.com", cwd=workdir)
        _run("git", "config", "user.name", "Finance Digest Bot", cwd=workdir)
        _run("git", "add", os.path.join(NOTE_DIR, filename), cwd=workdir)

        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"], cwd=workdir
        )
        if result.returncode == 0:
            print("[vault] изменений нет, коммит не нужен")
            return

        _run("git", "commit", "-m", f"finance digest: {today}", cwd=workdir)
        _run("git", "push", cwd=workdir)
