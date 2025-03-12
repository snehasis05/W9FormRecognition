import os
import base64
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")

if not AZURE_ENDPOINT or not AZURE_API_KEY:
    raise ValueError("Azure endpoint or key is missing. Check your .env file.")

document_analysis_client = DocumentAnalysisClient(AZURE_ENDPOINT, AzureKeyCredential(AZURE_API_KEY))

@app.get("/")
def read_root():
    return {"message": "W-9 API is running!"}

@app.post("/extract_w9")
async def extract_w9_data(file: UploadFile = File(...)):
    """Extracts key information from a W-9 form PDF."""
    try:
        contents = await file.read()
        poller = document_analysis_client.begin_analyze_document("prebuilt-document", document=contents)
        result = poller.result()
        extracted_data = {}
        
        for kv_pair in result.key_value_pairs:
            key = kv_pair.key.content.strip() if kv_pair.key else None
            value = kv_pair.value.content.strip() if kv_pair.value else None
            if key and value:
                extracted_data[key] = value
        
        return JSONResponse(content={"extracted_data": extracted_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
