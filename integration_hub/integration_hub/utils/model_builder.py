from pydantic import BaseModel, Field
from typing import Dict, Type, Any, Optional, List
from uuid import UUID
from datetime import datetime
from OData1C.models import ODataModel

# Словарь соответствия типов данных 1С → Python
ODATA_TYPE_MAPPING: Dict[str, Type[Any]] = {
    "Edm.String": str,
    "Edm.Boolean": bool,
    "Edm.Int32": int,
    "Edm.Int16": int,
    "Edm.Decimal": float,
    "Edm.Date": datetime,
    "Edm.Byte": int,
    "Edm.Binary": bytes,
    "Edm.Stream": bytes,
    "Edm.Guid": UUID,
}


class ModelBuilder:
    """
    Динамически создает Pydantic-модель на основе полей из Integration Flow.
    Обрабатывает как простые поля, так и вложенные коллекции.
    """

    @staticmethod
    def create_model(flow_name: str, fields: list[Dict[str, str]]) -> Type[ODataModel]:
        """
        Генерирует Pydantic-модель на основе списка полей, включая вложенные модели.

        :param flow_name: Название интеграционного потока.
        :param fields: Список полей с их именами и типами.
        :return: Сгенерированная Pydantic-модель.
        """
        annotations = {}
        model_fields = {}
        nested_models = {}  # Словарь вложенных моделей (будет пустым, если вложенных нет)

        # Проходим по полям и генерируем аннотации и поля для модели
        for field in fields:
            field_name = field["name"]
            field_type_1c = field["type"]
            python_type = ODATA_TYPE_MAPPING.get(field_type_1c, str)  # По умолчанию str

            # Если поле является коллекцией (Collection), обрабатываем его как вложенную модель
            if "Collection" in field_type_1c and "fields" in field:
                nested_model_name = f"{field_name}Model"
                nested_model = ModelBuilder.create_model(nested_model_name, field["fields"])

                # Добавляем вложенную модель в nested_models
                nested_models[field_name] = nested_model
                annotations[field_name] = List[nested_model]  # Поле будет списком вложенных объектов
                model_fields[field_name] = Field(alias=field_name, default=[])
            else:
                annotations[field_name] = Optional[python_type]
                model_fields[field_name] = Field(alias=field_name)

        # Если вложенные модели есть, добавляем их в структуру
        model_config = {
            "populate_by_name": True,
            "from_attributes": True,
        }

        # Создаем динамический класс Pydantic-модели
        model_class = type(
            f"{flow_name}Model",
            (ODataModel,),
            {
                "__annotations__": annotations,
                **model_fields,
                **({"nested_models": nested_models} if nested_models else {}),
                "model_config": model_config,
            },
        )

        return model_class
