from fastapi import FastAPI, HTTPException
from Src.Logics.factory_entities import factory_entities
from Src.Core.response_format import response_formats
from Src.reposity import reposity
from Src.start_service import start_service
import uvicorn

# Инициализация FastAPI
app = FastAPI(
    title="My Service API",
    description="REST API service rewritten from Flask to FastAPI",
    version="1.0.1"
)

# Инициализация логики приложения
start_service_instance = start_service()
start_service_instance.start()
factory = factory_entities()


@app.get("/api/accessibility")
def accessibility_check():
    """
    Проверить доступность REST API
    """
    return {"status": "SUCCESS"}


@app.get("/api/data/{data_type}/{format}")
def get_data_formatted(data_type: str, format: str):
    """
    Получить данные из репозитория в указанном формате
    """
    if data_type not in reposity.keys():
        raise HTTPException(status_code=400, detail="Wrong data_type")

    if format not in response_formats.get_all_formats():
        raise HTTPException(status_code=400, detail="Wrong format")

    try:
        data = start_service_instance.data[data_type]

        # Создаём экземпляр класса для указанного формата
        logic = factory.create(format)()
        result = logic.build(format, data)

        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/models")
def get_all_models():
    """
    Получить список всех типов моделей, поддерживаемых системой
    """
    try:
        models = reposity.keys()
        return {"available_models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while fetching models: {e}")


# Для локального запуска
if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
