import os
# import random
import time
import uuid

import requests
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from structlog import get_logger
import semver

PROCESSING_TIME = 3

logger = get_logger()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5100"],  # Management UI origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["*", "Access-Control-Allow-Origin"],
)

cir_host = os.environ.get("CIR_HOST", "http://api-cir:3030")


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

        target_index = next(
            (
                i
                for i, d in enumerate(list_ci.json())
                if d["guid"] == questionnaireVersionId
            ),
            None,
        )
        old_validator_version = list_ci.json()[target_index]["validator_version"]
        next_validator_version = str(
            semver.VersionInfo.parse(old_validator_version).bump_patch()
        )
        url = f"{cir_host}/collection-instruments/validator-version?guid={questionnaireVersionId}&validator_version={next_validator_version}"
        put_response = requests.put(
            url,
            json=schema,
            timeout=10000,
            headers={"Access-Control-Allow-Origin": "*"},
        )
        object_id = str(uuid.uuid4())
        response_json = put_response.json()
        time.sleep(PROCESSING_TIME)
        # roll = random.randint(1, 100)
        # if roll <= 20:
        #     logger.info("RANDOM FAIL")
        #     return_object = {
        #         "id": object_id,
        #         "cirId": questionnaireVersionId,
        #         "cirVersion": cirVersion,
        #         "surveyId": survey_id,
        #         "formType": form_type,
        #         "publishDate": response_json["published_at"],
        #         "success": False,
        #         "errorMessage": None,
        #         "displayErrorMessage": None,
        #         "__typename": "PublishHistoryEvent",
        #     }
        #     headers = {"Access-Control-Allow-Origin": "*"}
        #     return JSONResponse(content=return_object, headers=headers)

        if put_response.status_code == 200:
            logger.info("OK: status 200")
            return_object = {
                "id": object_id,
                "cirId": questionnaireVersionId,
                "cirVersion": cirVersion,
                "surveyId": survey_id,
                "formType": form_type,
                "publishDate": response_json["published_at"],
                "success": True,
                "errorMessage": None,
                "displayErrorMessage": None,
                "__typename": "PublishHistoryEvent",
            }
            headers = {"Access-Control-Allow-Origin": "*"}
            return JSONResponse(content=return_object, headers=headers)
        else:
            logger.error(
                f"Failed to post new schema, status code: {put_response.status_code}"
            )
            message = response_json["message"]
            return_object = {
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

            headers = {"Access-Control-Allow-Origin": "*"}
            return JSONResponse(content=return_object, headers=headers)
    return None


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8081))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
