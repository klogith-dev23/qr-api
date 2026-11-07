from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import qrcode
from PIL import Image
import requests
import io

app = FastAPI(title="Premium Custom QR Code API")

@app.get("/generate")
def generate_qr(data: str, fill_color: str = "black", back_color: str = "white", logo_url: str = None):
    try:
        qr = qrcode.QRCode(version=4, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGB")
        
        if logo_url:
            try:
                response = requests.get(logo_url, stream=True)
                response.raise_for_status()
                logo = Image.open(response.raw).convert("RGBA")
                basewidth = int(float(img.size[0]) * 0.25)
                wpercent = (basewidth / float(logo.size[0]))
                hsize = int((float(logo.size[1]) * float(wpercent)))
                logo = logo.resize((basewidth, hsize), Image.LANCZOS)
                pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
                img.paste(logo, pos, logo)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Logo error: {str(e)}")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
