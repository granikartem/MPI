# MPI
Репозиторий для хранения документов, написанных в рамках дисциплины МПИ 

## Генерация картинок из PUML

Требования: установленная Java (JRE/JDK 11+) и скачанный `plantuml.jar`.

Рендер диаграмм из `diagrams/usecases/` в `diagrams/out/`:

```bash
python scripts/render_puml.py --jar "C:\\path\\to\\plantuml.jar" --fmt png
```

Параметры (опционально):

```bash
python scripts/render_puml.py --jar "C:\\path\\to\\plantuml.jar" --src diagrams/usecases --out diagrams/out --fmt svg
```
