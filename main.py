from fastapi import FastAPI, Response, HTTPException, Header, UploadFile, File, Form
import qrcode
from qrcode.image.styledpil import StyledPilImage
import requests
from io import BytesIO
from PIL import Image

app = FastAPI()

RAPIDAPI_SECRET = "eb03b0c0-da81-11f1-99c9-110b92c3f9d6"

@app.post("/generate")
async def generate_qr(
    data: str = Form(...), 
    fill_color: str = Form("black"), 
    back_color: str = Form("white"), 
    logo_url: str = Form(None),
    logo_file: UploadFile = File(None),
    x_rapidapi_proxy_secret: str = Header(None)
):
    if data == "ping":
        pass
    elif x_rapidapi_proxy_secret != RAPIDAPI_SECRET:
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

        # Handle logo upload (either file upload or public URL)
        if logo_file:
            logo_bytes = await logo_file.read()
            logo = Image.open(BytesIO(logo_bytes))
            # Save temporary path or process directly
            # For qrcode styledpil, we pass the image object directly if supported, or save to buffer
        elif logo_url:
            response = requests.get(logo_url)
            response.raise_for_status()
            logo = Image.open(BytesIO(response.content))

        # Generate QR image
        img = qr.make_image(fill_color=fill_color, back_color=back_color)

        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return Response(content=img_io.getvalue(), media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating QR code: {str(e)}")
