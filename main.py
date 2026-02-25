from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import base64
import binascii
from io import BytesIO

import numpy as np
from PIL import Image, ImageSequence
import cv2

app = FastAPI() 
 
@app.get("/")
def root():
    return FileResponse("templates/index.html")

 
@app.get("/about")
def about():
    html_content = "<h2>My name is Konstantin</h2>"
    return HTMLResponse(content=html_content)

 
@app.get("/getdatatest/{id}")
def getdatatest(id):
    return {"id": id}

@app.post("/user")
def user(data = Body()):
    name = data["name"]
    age = data["age"]
    return {"message": f"{name}, ваш возраст - {age}!!!"}


class GetDataRequest(BaseModel):
    gif_base64: str  # base64 GIF (можно с префиксом data:image/gif;base64,)

class GetDataResponse(BaseModel):
    qrcodes: List[str]

def _strip_data_url_prefix(s: str) -> str:
    # поддержка "data:image/gif;base64,AAAA..."
    if "," in s and s.strip().lower().startswith("data:"):
        return s.split(",", 1)[1]
    return s

def _decode_gif_frames(gif_bytes: bytes) -> List[np.ndarray]:
    try:
        im = Image.open(BytesIO(gif_bytes))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid GIF: {e}")

    if (im.format or "").upper() != "GIF":
        raise HTTPException(status_code=400, detail="Uploaded data is not a GIF")

    frames = []
    for frame in ImageSequence.Iterator(im):
        rgb = frame.convert("RGB")
        frames.append(np.array(rgb))  # HxWx3 RGB
    return frames

def _decode_qr_from_frame_rgb(rgb: np.ndarray) -> List[str]:
    # OpenCV ожидает BGR
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    det = cv2.QRCodeDetector()

    # пытаемся найти несколько QR
    ok, decoded_info, _, _ = det.detectAndDecodeMulti(bgr)
    if ok:
        return [s for s in decoded_info if s]  # отфильтровать пустые

    # fallback на одиночный QR
    single, _, _ = det.detectAndDecode(bgr)
    return [single] if single else []

@app.post("/getdata", response_model=GetDataResponse)
def getdata(payload: GetDataRequest = Body(...)):
    b64 = _strip_data_url_prefix(payload.gif_base64).strip()
    try:
        gif_bytes = base64.b64decode(b64, validate=True)
    except (binascii.Error, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64: {e}")

    frames = _decode_gif_frames(gif_bytes)

    qrcodes: List[str] = []
    for rgb in frames:
        qrcodes.extend(_decode_qr_from_frame_rgb(rgb))

    return GetDataResponse(qrcodes=qrcodes)
    