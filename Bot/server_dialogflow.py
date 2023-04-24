from fastapi import FastAPI, UploadFile, File
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.cloud.dialogflowcx_v3 import AgentsAsyncClient, IntentsAsyncClient, FlowsAsyncClient, SessionsAsyncClient
from google.cloud.dialogflowcx_v3 import TextInput, QueryInput, QueryParameters, TransitionRoute, UpdateFlowRequest, Fulfillment
from google.api_core.client_options import ClientOptions
from google.cloud.dialogflowcx_v3.types.intent import Intent
from google.protobuf.field_mask_pb2 import FieldMask

import fastapi
import json
import os

app = FastAPI()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./credential.json"

def get_client_options(location):
    api_endpoint = "dialogflow.googleapis.com"
    if location is not None:
        api_endpoint = f"{location}-dialogflow.googleapis.com"
    return ClientOptions(api_endpoint=api_endpoint)

def get_code_ex(ex):
    if "400" in str(ex):
        return 400
    elif "409" in str(ex):
        return 409
    else:
        return 500
    
async def update_flow_agent(project_id: str, location: str, agent_id: str, intent_name: str):
    client_options = get_client_options(location)
    flows_client = FlowsAsyncClient(client_options=client_options)
    flow_name = flows_client.flow_path(project_id, location, agent_id, "00000000-0000-0000-0000-000000000000")
    
    flow = await flows_client.get_flow(name=flow_name)
    start_flow_transition = TransitionRoute(intent=intent_name, trigger_fulfillment=Fulfillment(messages=[]), name="")
    flow.transition_routes.append(start_flow_transition)

    update_request = UpdateFlowRequest(flow=flow, update_mask=FieldMask(paths=["transition_routes"]))

    try:
        updated_flow = await flows_client.update_flow(update_request)
        print("Flow updated: {}".format(updated_flow.name))
    except Exception as ex:
        print("Error updating flow: {}".format(ex)) 

@app.post("/get-token")
async def get_token(file: UploadFile = File(...)):
    SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
    contents = await file.read()
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(contents), scopes=SCOPES)
    credentials.refresh(Request())
    return {"access_token": credentials.token}

@app.post("/create-intent/projects/{project_id}/locations/{location}/agents/{agent_id}")
async def get_token(project_id: str, location: str, agent_id: str, request: fastapi.Request, response: fastapi.Response):
    intent_info = await request.json()
    client_options = get_client_options(location)

    agents_client = AgentsAsyncClient()
    intents_client = IntentsAsyncClient(client_options=client_options)
    project_location_parent_intent = agents_client.agent_path(project_id, location, agent_id)

    intent = Intent()
    intent.display_name = intent_info.get("display_name")
    intent.description = intent_info.get("description")
    intent.priority = intent_info.get("priority")
    intent.is_fallback = intent_info.get("is_fallback") 

    for phrase in intent_info.get("training_phrase", []):
        training_phrase = Intent.TrainingPhrase()
        for part in phrase.get("parts", []):
            training_phrase.parts.append(Intent.TrainingPhrase.Part(text=part.get("text"), parameter_id=part.get("parameter_id")))
        training_phrase.repeat_count = phrase.get("repeat_count")
        intent.training_phrases.append(phrase)

    # parameter = Intent.Parameter()
    # parameter.entity_type = "@sys.any"
    # parameter.is_list = False
    # parameter.redact = False
    # intent.parameters.append(parameter)

    try:
        new_intent = await intents_client.create_intent(parent=project_location_parent_intent, intent=intent)
        await update_flow_agent(project_id, location, agent_id, new_intent.name)
        print("Intent created: {}".format(new_intent.name))
        return {"message": "Intent created: {}".format(new_intent.name)}
    except Exception as ex:
        response.status_code = get_code_ex(ex)
        print("Error creating intent: {}".format(ex)) 
        return {"message": "Error creating intent: {}".format(ex)}


@app.post("/detect-intent/projects/{project_id}/locations/{location}/agents/{agent_id}/sessions/{session_id}")
async def get_token(project_id: str, location: str, agent_id: str, session_id: str, request: fastapi.Request, response: fastapi.Response):   
    message_info = await request.json()
    client_options = get_client_options(location)

    sessions_client = SessionsAsyncClient(client_options=client_options)
    session_name = sessions_client.session_path(project_id, location, agent_id, session_id)
    language_code = message_info.get("language_code") or "en"
    query_input = QueryInput(text=TextInput(text=message_info.get("text")), language_code=language_code)
    query_params = QueryParameters(time_zone='America/New_York', analyze_query_text_sentiment=True)

    try:
        deteced_intent = await sessions_client.detect_intent(request={"session": session_name, "query_input": query_input, "query_params": query_params})
        print('Intent detected')
        query_result = deteced_intent.query_result
        result = {
            "text": query_result.text,
            "language_code": query_result.language_code,
            "intent": query_result.intent.display_name,
            "intent_detection_confidence": query_result.intent_detection_confidence,
            "sentiment_score": query_result.sentiment_analysis_result.score,
            "sentiment_magnitude": query_result.sentiment_analysis_result.magnitude,
        }
        if deteced_intent is not None:
            return result
    except Exception as ex:        
        response.status_code = get_code_ex(ex)
        print('Error detecting intent: {}'.format(ex)) 
        return {"message": "Error detecting intent: {}".format(ex)}

