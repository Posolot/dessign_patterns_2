import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from datetime import datetime
from Src.Logics.factory_entities import factory_entities
from Src.reposity import reposity
from Src.start_service import start_service
from Src.Models.transaction_model import transaction_model
import json
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
    # Проверяем, что ключ есть в репозитории
    if data_type not in start_service_instance.data:
        raise HTTPException(status_code=400, detail=f"Data type '{data_type}' not loaded")

    # Проверяем формат
    if format not in factory.get_all_formats():
        raise HTTPException(status_code=400, detail="Wrong format")

    try:
        data = start_service_instance.data[data_type]
        data = [obj.to_dict() if hasattr(obj, "to_dict") else obj.__dict__ for obj in data]

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

@app.get("/api/report/osv")
async def get_osv_report(
    date_start: str = Query(..., description="Дата начала периода, формат YYYY-MM-DD"),
    date_end: str = Query(..., description="Дата окончания периода, формат YYYY-MM-DD"),
    storage_id: str = Query(..., description="Идентификатор склада (unique_code)")
):
    try:
        date_start_obj = datetime.strptime(date_start, "%Y-%m-%d")
        date_end_obj = datetime.strptime(date_end, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты (нужно YYYY-MM-DD)")

    data = start_service_instance.data

    transactions = data.get("transaction_model", [])
    nomenclatures = data.get("nomenclature_model", [])
    ranges = {r.unique_code: r for r in data.get("range_model", [])}

    result = {}

    for n in nomenclatures:
        n_name = getattr(n, "name", "Неизвестно")
        unit = getattr(ranges.get(getattr(n, "range_id", ""), None), "name", "—")
        key = (n.unique_code, unit)

        result[key] = {
            "nomenclature": n_name,
            "unit": unit,
            "start_balance": 0.0,
            "incoming": 0.0,
            "outgoing": 0.0,
            "end_balance": 0.0
        }

    for t in transactions:
        if not isinstance(t, transaction_model):
            continue
        if not t.storage or getattr(t.storage, "unique_code", None) != storage_id:
            continue
        if not (date_start_obj <= t.date_tr <= date_end_obj):
            continue

        n = t.nomenclature
        r = t.range
        n_name = getattr(n, "name", "Неизвестно")
        unit = getattr(r, "name", "—")
        key = (n.unique_code, unit)

        # Создаем ключ, если его нет
        if key not in result:
            result[key] = {
                "nomenclature": n_name,
                "unit": unit,
                "start_balance": 0.0,
                "incoming": 0.0,
                "outgoing": 0.0,
                "end_balance": 0.0
            }

        qty = t.quantity * (1.0 / (r.value if r and r.value else 1.0))
        if qty > 0:
            result[key]["incoming"] += qty
        else:
            result[key]["outgoing"] += abs(qty)

    # Конечные остатки
    for item in result.values():
        item["end_balance"] = item["start_balance"] + item["incoming"] - item["outgoing"]

    return JSONResponse(content=list(result.values()))

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
