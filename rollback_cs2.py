"""Restore the match FPS limit from before.json. Uses only standard Python."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

FPS_LINE = re.compile(rb'(?m)^([ \t]*"fps_max"[ \t]+")([0-9]+)("[ \t]*\r?)$')


def restore(autoexec, machine, original_limit, running):
    current = machine.read_bytes()
    matches = list(FPS_LINE.finditer(current))
    if len(matches) != 1:
        raise ValueError("Не удалось однозначно найти fps_max в профиле CS2.")
    if autoexec.exists():
        config = autoexec.read_bytes()
        if config in (b"fps_max 0\r\n", b"fps_max 0\n"):
            autoexec.unlink()
        elif re.search(rb'(?im)^[ \t]*fps_max[ \t]+"?0"?[ \t]*(?://[^\r\n]*)?\r?$', config):
            raise ValueError("После настройки autoexec.cfg был изменён. Удали в нём только добавленную строку fps_max 0 и повтори откат.")
    if running:
        print(f"Автозапуск команды снят. Для текущего сеанса введи в консоли CS2: fps_max {original_limit}")
        print("Или повтори этот откат после обычного выхода из игры.")
        return
    match = matches[0]
    value = match.group(2)
    if value == b"0":
        restored = current[:match.start(2)] + str(original_limit).encode("ascii") + current[match.end(2):]
        with tempfile.NamedTemporaryFile(dir=machine.parent, delete=False) as temp:
            temp_path = Path(temp.name)
            temp.write(restored)
        try:
            if machine.read_bytes() != current:
                raise ValueError("Профиль успел измениться. Повтори откат после синхронизации Steam.")
            os.replace(temp_path, machine)
        finally:
            temp_path.unlink(missing_ok=True)
    elif value != str(original_limit).encode("ascii"):
        print(f"В профиле уже выбран другой лимит ({int(value)} FPS). Сохранено твоё более позднее значение.")
        return
    print(f"Готово. В профиле CS2 восстановлен исходный лимит {original_limit} FPS.")


if __name__ == "__main__":
    try:
        snapshot = json.loads(Path(__file__).with_name("before.json").read_text(encoding="utf-8-sig"))
        processes = subprocess.check_output(
            [str(Path(os.environ["SystemRoot"]) / "System32" / "tasklist.exe"),
             "/FI", "IMAGENAME eq cs2.exe", "/FO", "CSV", "/NH"])
        restore(Path(snapshot["autoexec"]), Path(snapshot["machine_config"]),
                snapshot["fps_max"], b'"cs2.exe"' in processes.lower())
    except (KeyError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
