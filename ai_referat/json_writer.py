import json
from typing import Union, Optional
from ai_referat.models import Essay

def save_json(
    essay: Union[Essay, dict],
    json_path: Optional[str] = None,
    return_json: bool = False
) -> Optional[str]:
    """
    Сохраняет объект Essay или словарь в JSON.

    :param essay: экземпляр Essay или dict
    :param json_path: путь для сохранения файла JSON
    :param return_json: если True, возвращает строку JSON
    :return: JSON строка (если return_json=True) или None
    """
    # Преобразуем Pydantic модель в dict
    data: dict = essay.dict() if isinstance(essay, Essay) else essay

    # Сериализация в JSON
    json_str: str = json.dumps(data, ensure_ascii=False, indent=4)

    # Сохраняем в файл, если указан путь
    if json_path:
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json_str)

    if return_json:
        return json_str

    return None
