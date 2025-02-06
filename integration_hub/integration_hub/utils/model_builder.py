from pydantic import BaseModel, Field
from typing import Dict, Type, Any, Optional
from uuid import UUID
from datetime import datetime
from OData1C.models import ODataModel  # Наследуем от ODataModel

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
    "Edm.Guid": UUID,  # Поддержка GUID
}


class ModelBuilder:
    """
    Динамически создает Pydantic-модель на основе полей из Integration Flow.
    """

    @staticmethod
    def create_model(flow_name: str, fields: list[Dict[str, str]]) -> Type[ODataModel]:
        """
        Генерирует Pydantic-модель на основе списка полей.

        :param flow_name: Название интеграционного потока.
        :param fields: Список полей с их именами и типами.
        :return: Сгенерированная Pydantic-модель.
        """
        annotations = {}
        model_fields = {}

        for field in fields:
            field_name = field["fieldname"]  # Оригинальное название из OData
            field_type_1c = field["fieldtype"]
            python_type = ODATA_TYPE_MAPPING.get(field_type_1c, str)  # По умолчанию str

            # Добавляем аннотацию типа
            annotations[field_name] = Optional[python_type]

            # Добавляем Field(alias=...) для сохранения оригинального названия
            model_fields[field_name] = Field(alias=field_name)

        # Создаем динамический класс Pydantic-модели, наследуем от ODataModel
        model_class = type(
            f"{flow_name}Model",
            (ODataModel,),
            {
                "__annotations__": annotations,
                **model_fields,
                "model_config": {"populate_by_name": True, "from_attributes": True},
            },
        )

        return model_class
