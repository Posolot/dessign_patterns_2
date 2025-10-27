import connexion
from flask import request
from Src.Logics.factory_entities import factory_entities
from Src.settings_manager import settings_manager
from Src.Core.response_format import response_formats
from flask import Flask, request
from Src.reposity import reposity
from Src.start_service import start_service

app = connexion.FlaskApp(__name__)
app = Flask(__name__)

start_service = start_service()
start_service.start()
factory = factory_entities()

formats = {}

"""
Проверить доступность REST API
"""


@app.route("/api/accessibility", methods=['GET'])
def formats():
    return "SUCCESS"


@app.route("/api/data/<data_type>/<format>", methods=['GET'])
def get_data_formatted(data_type: str, format: str):
    if data_type not in reposity.keys():
        return {"error": "Wrong data_type"}, 400

    if format not in response_formats.get_all_formats():
        return {"error": "Wrong format"}, 400

    try:
        data = start_service.data[data_type]

        # Создаём экземпляр класса ответа
        logic = factory.create(format)()
        result = logic.build(format, data)

        return {"result": result}

    except Exception as e:
        return {"error": str(e)}, 400




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)