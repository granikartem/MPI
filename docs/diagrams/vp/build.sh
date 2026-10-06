#!/usr/bin/env bash
# Сборка диаграмм Visual Paradigm: XML -> .vpp -> PNG, с обязательной проверкой.
#
# Использование:
#   ./build.sh SM_UC2_UseCaseView [ещё имена...]
#   ./build.sh --all                 # всё, что лежит в out/*.xml
#
# Учтены грабли, описанные в docs/VisualParadigm.md §4–5:
#   * запускать утилиты можно только из каталога scripts: внутри они делают pushd ..\bin;
#   * ImportXML дописывает в существующий .vpp — проект удаляется перед прогоном;
#   * ExportDiagramImage не перезаписывает каталог -out, а кладёт файл с суффиксом «2» —
#     выгрузка идёт во временный каталог, готовые PNG переносятся поверх;
#   * -diagram "*" разворачивается слоем MSYS в список файлов каталога — имя передаём явно;
#   * импорт печатает «Saved project» даже после исключения — ищем java.lang./java.io./at v.
#
# Аргументы .bat передаются раздельно, а не одной строкой, и под MSYS_NO_PATHCONV=1.
# Иначе Git Bash подменяет одиночный /c на путь C:\, а //c cmd уже не понимает и открывает
# интерактивную сессию: прогон виснет молча, без единого сообщения об ошибке.
#
# Сам .bat вызывается по полному пути, хотя рабочий каталог и так scripts: в системе выставлена
# NoDefaultCurrentDirectoryInExePath=1, из-за чего cmd не ищет программы в текущем каталоге.
# Путь берётся в формате 8.3: cmd /c обрезает кавычки у строки целиком, и полный путь
# с пробелами («Visual Paradigm CE 18.1») разваливается на первом же пробеле.
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VP="${VP:-/c/Users/a.granik/tools/Visual Paradigm CE 18.1}"
SCRIPTS="$VP/Application/scripts"
WORK="$HERE/.build"
PNG="$HERE/out/png"

[ -d "$SCRIPTS" ] || { echo "нет каталога скриптов Visual Paradigm: $SCRIPTS" >&2; exit 2; }

names=("$@")
if [ "${1:-}" = "--all" ]; then
    names=()
    for f in "$HERE"/out/*.xml; do names+=("$(basename "$f" .xml)"); done
fi
[ "${#names[@]}" -gt 0 ] || { echo "нечего собирать" >&2; exit 2; }

mkdir -p "$WORK" "$PNG"
export HEADLESS=true
export MSYS_NO_PATHCONV=1
rc=0

bat() { cygpath -d "$(cygpath -w "$SCRIPTS/$1.bat")"; }   # 8.3: путь без пробелов
win() { printf '%s' "$(cd "$(dirname "$1")" && pwd -W)/$(basename "$1")" | tr '/' '\\'; }

for n in "${names[@]}"; do
    xml="$HERE/out/$n.xml"
    [ -f "$xml" ] || { echo "ПРОПУСК $n: нет $xml" >&2; rc=1; continue; }
    rm -rf "$WORK/$n.vpp" "$WORK/$n.vpp.bak_"* "$WORK/img_$n"
    log="$WORK/$n.log"

    ( cd "$SCRIPTS" && cmd /c "$(bat ImportXML)" \
        -project "$(win "$WORK/$n.vpp")" -file "$(win "$xml")" ) >"$log" 2>&1

    # «Saved project» печатается и после исключения, поэтому смотрим на трассировки
    if grep -qE 'java\.lang\.|java\.io\.|^[[:space:]]+at v\.' "$log"; then
        echo "ОШИБКА $n: импорт упал, см. $log" >&2
        grep -E 'java\.lang\.|java\.io\.' "$log" | head -3 >&2
        rc=1
        continue
    fi
    [ -f "$WORK/$n.vpp" ] || { echo "ОШИБКА $n: проект не создан, см. $log" >&2; rc=1; continue; }

    ( cd "$SCRIPTS" && cmd /c "$(bat ExportDiagramImage)" \
        -project "$(win "$WORK/$n.vpp")" -out "$(win "$WORK/img_$n")" \
        -diagram "$n" -type png_with_background ) >>"$log" 2>&1

    # при одной диаграмме -out понимается как путь к файлу, при нескольких — как каталог
    if [ -f "$WORK/img_$n" ]; then
        found="$WORK/img_$n"
    else
        found=$(find "$WORK/img_$n" -name '*.png' 2>/dev/null | head -1)
    fi
    if [ -z "$found" ]; then
        echo "ОШИБКА $n: картинка не выгружена, см. $log" >&2
        rc=1
        continue
    fi
    mv -f "$found" "$PNG/$n.png"
    size=$(python -c "import sys;from PIL import Image;print('%dx%d'%Image.open(sys.argv[1]).size)" "$PNG/$n.png" 2>/dev/null || echo '?')
    echo "$n -> out/png/$n.png  ($size)"
done

exit $rc
