from fastapi import FastAPI, Response, HTTPException, Header, UploadFile, File
import qrcode
import requests
from io import BytesIO
from PIL import Image

app = FastAPI()

RAPIDAPI_SECRET = "eb03b0c0-da81-11f1-99c9-110b92c3f9d6"

@app.api_route("/generate", methods=["GET", "POST"])
async def generate_qr(
    data: str = None, 
    fill_color: str = "black", 
    back_color: str = "white", 
    logo_url: str = None,
    logo_file: UploadFile = File(None),
    x_rapidapi_proxy_secret: str = Header(None)
):
    if data == "ping":
        return Response(content="pong", media_type="text/plain")
        
    if x_rapidapi_proxy_secret != RAPIDAPI_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized. Please use the RapidAPI hub to access this service.")

    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color=fill_color, back_color=back_color)

        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return Response(content=img_io.getvalue(), media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating QR code: {str(e)}")
