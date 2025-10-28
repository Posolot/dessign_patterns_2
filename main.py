import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from Src.Logics.factory_entities import factory_entities
from Src.reposity import reposity
from Src.start_service import start_service

# Инициализация сервисов
app = FastAPI(title="Recipe API")

start_service_instance = start_service()
start_service_instance.start()

factory = factory_entities()

# Проверка доступности API
@app.get("/api/accessibility")
async def api_accessibility():
    return {"status": "SUCCESS"}

# Получить данные в заданном формате
@app.get("/api/data/{data_type}/{format}")
async def get_data_formatted(data_type: str, format: str):
    if data_type not in reposity.keys():
        raise HTTPException(status_code=400, detail="Wrong data_type")

    if format not in factory.get_all_formats():  # заменил response_formats.get_all_formats()
        raise HTTPException(status_code=400, detail="Wrong format")

    try:
        data = start_service_instance.data[data_type]

        logic_class = factory.create(format)
        logic_instance = logic_class()
        result = logic_instance.build(format, data)

        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Получить список всех рецептов
@app.get("/api/receipts")
async def get_receipts():
    key = "receipt_model"
    if key not in start_service_instance.data:
        raise HTTPException(status_code=404, detail="No receipts found")

    receipts = start_service_instance.data[key]

    response_class = factory.create("json")
    response_instance = response_class()
    result = response_instance.build("json", receipts)

    return {"receipts": result}

# Получить конкретный рецепт по уникальному коду
@app.get("/api/receipts/code/{unique_code}")
async def get_receipt_by_code(unique_code: str):
    key = "receipt_model"
    if key not in start_service_instance.data or len(start_service_instance.data[key]) == 0:
        raise HTTPException(status_code=404, detail="No receipts available")

    receipts = start_service_instance.data[key]
    recipe = next((r for r in receipts if getattr(r, "unique_code", None) == unique_code), None)

    if not recipe:
        raise HTTPException(status_code=404, detail=f"Receipt with code {unique_code} not found")

    response_class = factory.create("json")
    response_instance = response_class()
    result = response_instance.build("json", [recipe])

    return {"receipt": result}


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
