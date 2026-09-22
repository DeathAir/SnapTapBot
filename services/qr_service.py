import zipfile
from io import BytesIO
from typing import List, Optional
from urllib.parse import urlparse, parse_qs
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import qrcode
from PIL import Image
from pyzbar.pyzbar import decode

from config import settings
from models import Ticket

BASE_DIR = Path(__file__).resolve().parent.parent
QR_FOLDER = BASE_DIR / "qr_codes"


class QRService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_qr_code(self, ticket_number: int, secret_hash: str, club_id: int) -> str:
        qr_data = f"{settings.base_url}/verify?ticket={ticket_number}&hash={secret_hash}&club={club_id}"
        qr = qrcode.make(qr_data)

        QR_FOLDER.mkdir(exist_ok=True)
        file_path = QR_FOLDER / f"ticket_{club_id}_{ticket_number}.png"

        qr.save(str(file_path))


        return str(file_path)

    async def generate_qr_codes_batch(self, tickets) -> List[str]:
        file_paths = []
        for ticket in tickets:
            path = await self.generate_qr_code(
                ticket_number=ticket.number,
                secret_hash=ticket.secret_hash,
                club_id=ticket.club_id
            )
            file_paths.append(path)
        return file_paths

    async def generate_qr_for_club(self, club_id: int) -> List[str]:
        existing = await self.db.execute(select(Ticket).where(Ticket.club_id == club_id))
        tickets = existing.scalars().all()
        if not tickets:
            raise HTTPException(status_code=404, detail="Ticket on the Club not found")
        return await self.generate_qr_codes_batch(tickets)

    async def generate_qr_zip(self, club_id: int) -> bytes:
        existing = await self.db.execute(
            select(Ticket).where(Ticket.club_id == club_id)
        )
        tickets = existing.scalars().all()
        if not tickets:
            raise HTTPException(status_code=404, detail="Tickets not found")

        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for ticket in tickets:
                qr_data = (
                    f"{settings.base_url}/verify"
                    f"?ticket={ticket.number}"
                    f"&hash={ticket.secret_hash}"
                    f"&club={ticket.club_id}"
                )
                qr = qrcode.make(qr_data)
                img_buffer = BytesIO()
                qr.save(img_buffer, format="PNG")
                img_buffer.seek(0)
                zip_file.writestr(
                    f"ticket_{ticket.number}.png",
                    img_buffer.getvalue()
                )

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    async def read_qr_from_image(self, image_bytes: bytes) -> Optional[str]:
        try:
            image = Image.open(BytesIO(image_bytes))
            decoded = decode(image)
            if not decoded:
                return None
            return decoded[0].data.decode("utf-8")
        except Exception:
            return None

    async def read_qr_from_bytes(self, image_bytes: bytes) -> Optional[str]:
        return await self.read_qr_from_image(image_bytes)

    async def extract_qr_data(self, qr_data: str) -> dict:
        try:
            parsed = urlparse(qr_data)
            params = parse_qs(parsed.query)
            ticket_number = int(params.get("ticket", [None])[0])
            secret_hash = params.get("hash", [None])[0]
            club_id = int(params.get("club", [None])[0])

            if not all([ticket_number, secret_hash, club_id]):
                raise ValueError("Missing data")
            return {
                "ticket_number": ticket_number,
                "secret_hash": secret_hash,
                "club_id": club_id
            }
        except Exception:
            raise HTTPException(400, "Invalid QR data")

    async def get_qr_file_path(self, ticket_number: int, club_id: int) -> str:
        return str(QR_FOLDER / f"ticket_{club_id}_{ticket_number}.png")

    async def delete_qr_file(self, ticket_number: int, club_id: int) -> bool:
        path = QR_FOLDER / f"ticket_{club_id}_{ticket_number}.png"
        if path.exists():
            path.unlink()
            return True
        return False

    async def delete_all_qr_files(self) -> dict:
        if not QR_FOLDER.exists():
            return {"deleted": 0}
        count = 0
        for file in QR_FOLDER.iterdir():
            if file.suffix == ".png":
                file.unlink()
                count += 1
        return {"deleted": count}

    async def get_qr_files_list(self) -> List[str]:
        if not QR_FOLDER.exists():
            return []
        return [f.name for f in QR_FOLDER.iterdir() if f.suffix == ".png"]