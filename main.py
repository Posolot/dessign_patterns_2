import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from datetime import datetime
from Src.Logics.factory_entities import factory_entities
from Src.reposity import reposity
from Src.start_service import start_service
from Src.Models.transaction_model import transaction_model
from Src.Logics.serialize import to_primitive
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
    if data_type not in start_service_instance.data:
        raise HTTPException(status_code=400, detail=f"Data type '{data_type}' not loaded")
    if format not in factory.get_all_formats():
        raise HTTPException(status_code=400, detail="Wrong format")

    try:
        data = start_service_instance.data[data_type]
        logic_class = factory.create(format)
        logic_instance = logic_class()
        result = logic_instance.build(format, data)  # теперь result — list/dict

        # Вернуть как JSON (FastAPI сам сериализует), либо через JSONResponse
        return JSONResponse(content={"result": result})

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

@app.post("/api/repository/save")
async def save_repository():
    """
    Сохраняет репозиторий данных в файл default_data.json
    """
    try:
        start_service_instance.save_data("default_data.json")
        return JSONResponse(
            status_code=200,
            content={"detail": "Repository successfully saved to file"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/report/osv")
async def get_osv_report(
        date_start: str = Query(..., description="Дата начала периода, формат YYYY-MM-DD"),
        date_end: str = Query(..., description="Дата окончания периода, формат YYYY-MM-DD"),
        storage_id: str = Query(..., description="Идентификатор склада (unique_code)")
):
    # Парсинг дат
    try:
        dt_start = datetime.strptime(date_start, "%Y-%m-%d")
        dt_end = datetime.strptime(date_end, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты, нужен YYYY-MM-DD")

    data = start_service_instance.data
    transactions = data.get("transaction_model", [])
    nomenclatures = data.get("nomenclature_model", [])

    report = {}

    # Инициализация отчета по всем номенклатурам
    for n in nomenclatures:
        unit_obj = getattr(n, "range", None)
        key = (n.unique_code, getattr(unit_obj, "unique_code", None))

        report[key] = {
            "start_balance": 0.0,
            "nomenclature": to_primitive(n),
            "unit": to_primitive(unit_obj) if unit_obj else None,
            "incoming": 0.0,
            "outgoing": 0.0,
            "end_balance": 0.0
        }

    # Обработка транзакций
    for t in transactions:
        if not isinstance(t, transaction_model):
            continue
        if not t.storage or getattr(t.storage, "unique_code", None) != storage_id:
            continue
        if not (dt_start <= t.date_tr <= dt_end):
            continue

        n = t.nomenclature
        r = t.range
        key = (n.unique_code, getattr(r, "unique_code", None))

        if key not in report:
            report[key] = {
                "start_balance": 0.0,
                "nomenclature": to_primitive(n),
                "unit": to_primitive(r) if r else None,
                "incoming": 0.0,
                "outgoing": 0.0,
                "end_balance": 0.0
            }

        qty = t.quantity * (1.0 / (getattr(r, "value", 1.0) if r else 1.0))
        if qty > 0:
            report[key]["incoming"] += qty
        else:
            report[key]["outgoing"] += abs(qty)

    for item in report.values():
        item["end_balance"] = item["start_balance"] + item["incoming"] - item["outgoing"]

    return JSONResponse(content=list(report.values()))

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
