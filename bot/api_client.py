from typing import Optional, Any

from httpx import AsyncClient


class ApiClient:

    def __init__(self, base_url: str, api_key: Optional[str] = None) -> None:
        headers = {"Accept": "application/json"}
        if api_key:
            headers["X-API-Key"] = api_key

        self.client = AsyncClient(
            base_url=base_url,
            timeout=10.0,
            headers=headers,
        )

    async def close(self) -> None:
        await self.client.aclose()

    async def _get(self, url: str, **kwargs) -> Any:
        response = await self.client.get(url, **kwargs)
        response.raise_for_status()
        if response.content:
            return response.json()
        return None

    async def _post(self, url: str, **kwargs) -> Any:
        response = await self.client.post(url, **kwargs)
        response.raise_for_status()
        if response.content:
            return response.json()
        return None

    async def _put(self, url: str, **kwargs) -> Any:
        response = await self.client.put(url, **kwargs)
        response.raise_for_status()
        if response.content:
            return response.json()
        return None

    async def _delete(self, url: str, **kwargs) -> Any:
        response = await self.client.delete(url, **kwargs)
        response.raise_for_status()
        if response.content:
            return response.json()
        return None

    async def get_or_create_user(self, telegram_id: int,
                                 username: str,
                                 phone: str,
                                 role: str = "user",
                                 club_id: Optional[int] = None) -> dict:
        return await self._post(
            "/users/register",
            json={
                "telegram_id": telegram_id,
                "username": username,
                "phone": phone,
                "role": role,
                "club_id": club_id,
            }
        )

    async def get_user(self, telegram_id: int) -> dict:
        return await self._get(
            "/users/me",
            params={"telegram_id": telegram_id},
        )

    async def update_user(
            self,
            telegram_id: int,
            username: Optional[str] = None,
            phone: Optional[str] = None,
            role: Optional[str] = None,
            club_id: Optional[int] = None,
    ) -> dict:
        payload = {}
        if username is not None:
            payload["username"] = username
        if phone is not None:
            payload["phone"] = phone
        if role is not None:
            payload["role"] = role
        if club_id is not None:
            payload["club_id"] = club_id

        return await self._put(
            "/users/me",
            params={"telegram_id": telegram_id},
            json=payload,
        )

    # БИЛЕТЫ

    async def verify_ticket(self, number: int, secret_hash: str, club_id: int, user_id: int, telegram_id: int) -> dict:

        return await self._post("/tickets/verify",
                                json={
                                    "number": number,
                                    "secret_hash": secret_hash,
                                    "club_id": club_id,
                                    "user_id": user_id,
                                    "telegramId": telegram_id,
                                }
        )

    async def get_my_tickets(self, telegram_id: int) -> dict:

        return await self._get(
            "/tickets/my",
            params={"telegram_id": telegram_id}
        )

    # АДМИН

    async def get_stats(self, club_id: int) -> dict:

        return await self._get(
            "/admin/stats",
            params={"club_id": club_id}
        )

    async def get_club_users(self, club_id: int) -> dict:

        return await self._get(
            "/admin/users",
            params={"club_id": club_id}
        )

    async def get_all_users(self) -> list:
        return await self._get("/superadmin/users")


    async def get_club_tickets(self, club_id: int) -> dict:

        return await self._get(
            "/admin/tickets",
            params={"club_id": club_id}
        )

    async def generate_tickets(self, club_id: int, raffle_id: int, count: int) -> dict:

        return await self._post(
            "/admin/tickets/generate",
            json={"club_id": club_id,
                  "raffle_id": raffle_id,
                  "count": count
            }
        )
    async def get_report(self, club_id: int) -> dict:
        return await self._get("/admin/report", params={"club_id": club_id})

    async def get_club_raffles(self, club_id: int) -> dict:
        return await self._get(
            "/admin/raffles",
            params={"club_id": club_id}
        )

    async def create_raffle(
            self,
            user_id: int,
            title: str,
            description: str,
            prizes: list[str], 
            start_date: str,
            end_date: str,
            club_id: int,
    ) -> dict:
        return await self._post(
            "/admin/raffles",
            params={"user_id": user_id},
            json={
                "title": title,
                "description": description,
                "prizes": prizes,
                "start_date": start_date,
                "end_date": end_date,
                "club_id": club_id,
            },
        )

    async def activate_raffle(self, raffle_id: int) -> dict:
        return await self._post(f"/admin/raffles/{raffle_id}/activate")

    async def deactivate_raffle(self, raffle_id: int) -> dict:
        return await self._post(f"/admin/raffles/{raffle_id}/deactivate")

    async def draw_winner(self, raffle_id: int) -> dict:
        return await self._post(f"/admin/raffles/{raffle_id}/draw")

    async def get_raffle_results(self, raffle_id: int) -> dict:
        return await self._get(f"/admin/raffles/{raffle_id}/results")

    async def deactivate_club_tickets(self, club_id: int) -> dict:
        return await self._post(
            "/admin/tickets/deactivate",
            params={"club_id": club_id}
        )

    async def delete_club_tickets(self, club_id: int) -> dict:
        return await self._delete(
            "/admin/tickets",
            params={"club_id": club_id},
        )

    # СУПЕР АДМИН

    async def get_all_clubs(self) -> list:
        return await self._get("/superadmin/clubs")

    async def create_club(self, name: str, address: str, phone: str, is_active: bool = True) -> dict:
        return await self._post(
            "/superadmin/clubs",
            json={
                "name": name,
                "address": address,
                "phone": phone,
                "is_active": is_active
            }
        )

    async def delete_club(self, club_id: int) -> dict:
        return await self._delete(f"/superadmin/clubs/{club_id}")

    async def get_superadmin_stats(self) -> dict:
        return await self._get(
            "/superadmin/stats",
        )

    async def get_tickets_zip(self, club_id: int) -> bytes:
        response = await self.client.get(
            "/admin/tickets/zip",
            params={"club_id": club_id}
        )
        response.raise_for_status()
        return response.content