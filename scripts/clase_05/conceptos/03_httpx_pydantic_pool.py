import anyio
import httpx
from pydantic import BaseModel, ValidationError
from loguru import logger


class Post(BaseModel):
    id: int
    title: str


async def fetch_post(client: httpx.AsyncClient, post_id: int):
    url = f"https://jsonplaceholder.typicode.com/posts/{post_id}"
    try:
        response = await client.get(url)
        response.raise_for_status()

        # Parseo y validación estricta con Pydantic V2
        post = Post.model_validate(response.json())
        logger.success(f"Post {post.id} descargado: {post.title[:15]}...")
    except ValidationError as e:
        logger.error(f"Contrato roto en post {post_id}: {e}")
    except httpx.HTTPError as e:
        logger.error(f"Error de red: {e}")


async def main():
    # Un único cliente para mantener viva la conexión (Keep-Alive)
    async with httpx.AsyncClient(timeout=10.0) as client:
        async with anyio.create_task_group() as tg:
            for i in range(1, 6):
                tg.start_soon(fetch_post, client, i)

if __name__ == "__main__":
    anyio.run(main)
