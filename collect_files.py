import os, sys
from pathlib import Path


# Глубина по умолчанию
max_depth = 1

# Вернём 1, если будет хоть одна неудача
result_code = 0


def correct_path(path):

    if not path.exists():
        return path

    # Разделяем на имя и расширение
    stem = path.stem
    suffix = path.suffix

    # Проверяем наличие номера в конце имени
    parts = stem.split("-")
    last_part = parts[-1]
    new_stem = stem

    if last_part.isdigit():
        # Если последняя часть - это число, увеличиваем его
        number = int(last_part) + 1
        # Удаляем последнюю часть и добавляем новое число
        new_stem = "-".join(parts[:-1] + [str(number)])
    else:
        # Если числа нет, добавляем -1
        new_stem = f"{stem}-1"

    # Создаем новый путь
    new_path = path.parent / f"{new_stem}{suffix}"

    # Рекурсивно повторяем это же к новому пути, пока не станет уникальным
    return correct_path(new_path)


def copy_file(source, destination):
    global result_code

    try:
        source_path = Path(source)
        destination_path = Path(destination)
        destination_path.write_bytes(source_path.read_bytes())
    except Exception:
        result_code = 1


def main():
    global max_depth, result_code

    try:
        argv = sys.argv
        argc = len(argv)

        if argc < 3:
            print("Не хватает аргументов")
            sys.exit(1)

        if argc > 5:
            print("Слишком много аргументов")
            sys.exit(1)

        source_dir = argv[1]
        dest_dir = argv[2]

        if argc == 5 and argv[3] != "--max_depth":
            print("Неизвестный ключ")
            sys.exit(1)

        if argc == 5 and argv[3] == "--max_depth":
            max_depth_arg = int(argv[4])
            max_depth = max(max_depth_arg, 1)

        if not os.path.isdir(source_dir) or os.path.isfile(dest_dir):
            print("Путь к исходному каталогу не правильный")
            sys.exit(1)

        if os.path.isfile(dest_dir):
            print("Путь к целевому каталогу - файл")
            sys.exit(1)

        abs_source_dir = Path(source_dir).resolve()
        abs_dest_dir = Path(dest_dir).resolve()
        abs_source_dir_depth = len(abs_source_dir.parts)

        for root, dirs, files in os.walk(abs_source_dir):

            if len(files):
                try:
                    root = Path(root)
                    root_depth = len(root.parts)
                    depth_limit = root_depth - abs_source_dir_depth
                    depth = min(depth_limit, max_depth - 1)

                    central_tuple = tuple()
                    if depth:
                        central_tuple = root.parts[-depth:]
                    central = Path(*central_tuple)

                    dir = abs_dest_dir / central

                    dir.mkdir(parents=True, exist_ok=True)

                    for file in files:
                        source_file_path = root / file
                        uncorrected_dest_file_path = dir / file
                        corrected_dest_file_path = correct_path(
                            uncorrected_dest_file_path
                        )
                        copy_file(source_file_path, corrected_dest_file_path)

                except Exception:
                    result_code = 1

    except Exception:
        result_code = 1

    sys.exit(result_code)


if __name__ == "__main__":
    main()
