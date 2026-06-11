import json
import os
import uuid

import requests
import uvicorn
from fastapi import FastAPI
from structlog import get_logger

logger = get_logger()

app = FastAPI()

cir_host = os.environ.get("CIR_HOST", f"http://0.0.0.0:3030")


@app.get("/republishschema/{questionnaireVersionId}/cirversion/{cirVersion}")
async def root(questionnaireVersionId: str, cirVersion: int):
    url = f"{cir_host}/collection-instruments/schema?guid={questionnaireVersionId}"
    response = requests.get(url, timeout=10000)
    if response.status_code == 200:
        logger.info("OK: status 200")
        schema = response.json()
        form_type = schema["form_type"]
        survey_id = schema["survey_id"]
        language = schema["language"]
        list_ci = requests.get(
            f"{cir_host}/collection-instruments/metadata?classifier_type=form_type&classifier_value={form_type}&language={language}&survey_id={survey_id}",
            timeout=10000,
        )
        current_validator_version = list_ci.json()[0]["validator_version"]
        new_ci_version = cirVersion + 1
        new_validator_version = current_validator_version
        new_guid = str(uuid.uuid4())
        url = f"{cir_host}/collection-instruments?guid={new_guid}&validator_version={new_validator_version}&ci_version={new_ci_version}"
        post_response = requests.post(url, json=schema, timeout=10000)
        object_id = str(uuid.uuid4())
        response_json = post_response.json()
        if post_response.status_code == 200:
            logger.info("OK: status 200")
            return_object = json.dumps(
                {
                    "id": object_id,
                    "cirId": new_guid,
                    "cirVersion": new_ci_version,
                    "surveyId": survey_id,
                    "formType": form_type,
                    "publishDate": response_json["published_at"],
                    "success": True,
                    "errorMessage": None,
                    "displayErrorMessage": None,
                    "__typename": "PublishHistoryEvent",
                }
            )
            return return_object
        else:
            logger.error(
                f"Failed to post new schema, status code: {post_response.status_code}"
            )
            message = response_json["message"]
            return_object = json.dumps(
                {
                    "id": object_id,
                    "cirId": questionnaireVersionId,
                    "cirVersion": cirVersion,
                    "surveyId": survey_id,
                    "formType": form_type,
                    "publishDate": None,
                    "success": False,
                    "errorMessage": message,
                    "displayErrorMessage": message,
                    "__typename": "PublishHistoryEvent",
                }
            )
            return return_object
    return None


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8081))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
