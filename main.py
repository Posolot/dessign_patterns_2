import uvicorn
import json
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from Src.Logics.factory_entities import factory_entities
from Src.start_service import start_service
from Src.Logics.osv_service import OSVReportService
from Src.Dtos.filter_dto import filter_dto
from Src.Logics.factory_convertor import factory_convertor
# Инициализация сервисов
app = FastAPI(title="Recipe API")

start_service_instance = start_service()
start_service_instance.start()

factory = factory_entities()
converter = factory_convertor()

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
        result = logic_instance.build(format, data)

        return JSONResponse(content={"result": result})

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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

    service = OSVReportService(start_service_instance)
    report_data = service.generate(date_start, date_end, storage_id)
    return JSONResponse(content=report_data)

@app.post("/api/filter_by_model/{domain_type}")
async def filter_by_model(
    domain_type: str,
    filters: str = Query("", description="JSON-массив filters для filter_dto")
):
    domain_type = domain_type.lower()

    if domain_type not in start_service_instance.data:
        raise HTTPException(status_code=400, detail=f"Domain type '{domain_type}' not loaded")

    data_list = start_service_instance.data[domain_type]

    try:
        if filters:
            parsed = json.loads(filters)
            if isinstance(parsed, list):
                parsed = {"filters": parsed}
            elif not isinstance(parsed, dict):
                raise HTTPException(status_code=400, detail="filters должен быть списком или объектом")

            if "model" not in parsed or not parsed["model"]:
                parsed["model"] = domain_type

            dto = filter_dto.from_dict(parsed)
        else:
            dto = filter_dto()
            dto.model = domain_type
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка построения filter_dto: {e}")

    try:
        filtered = dto.apply(data_list)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка применения фильтров: {e}")

    filtered_dicts = [converter.create(x) for x in filtered]

    return JSONResponse(content={"result": filtered_dicts})


@app.post("/api/report/osv")
async def osv_report(
    date_start: str = Query(..., description="Дата начала периода YYYY-MM-DD"),
    date_end: str = Query(..., description="Дата окончания периода YYYY-MM-DD"),
    storage_id: str = Query(..., description="Unique_code склада"),
    filters: str = Query("", description="JSON-словарь filters для filter_dto")
):
    """
    filters должен быть строкой, содержащей JSON:
    {
        "filters": [
            {"field_name": "name", "value": "Мука", "type": "LIKE"},
            {"field_name": "range_name", "value": "кг", "type": "EQUALS"}
        ]
    }
    """

    try:
        dto = None

        if filters:
            try:
                filters_dict = json.loads(filters)
            except json.JSONDecodeError:
                raise HTTPException(400, "filters должен быть корректным JSON")

            # Собираем filter_dto из JSON
            if isinstance(filters_dict, list):
                filters_dict = {"filters": filters_dict}
            dto = filter_dto.from_dict(filters_dict)

        service = OSVReportService(start_service_instance)
        result = service.generate(
            date_start=date_start,
            date_end=date_end,
            storage_id=storage_id,
            dto=dto
        )
        return result

    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
