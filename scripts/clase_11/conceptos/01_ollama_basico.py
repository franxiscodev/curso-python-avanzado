"""
Cliente HTTP directo a Ollama — patrón gateway con httpx.

Demuestra cómo llamar a la API REST de Ollama sin el SDK ollama:
  - OllamaGateway encapsula la URL base y el timeout
  - generate_text envía un POST a /api/generate con stream=False
  - httpx.ConnectError captura el caso de "Ollama no está corriendo"

Ollama expone una REST API en localhost:11434. Llamarla con httpx en lugar
del SDK oficial tiene una ventaja: el mismo cliente httpx que usa PyCommute
para OpenWeather y ORS sirve también para Ollama.

Ejecutar (desde curso/):
    uv run python scripts/clase_11/conceptos/01_ollama_basico.py
"""

import anyio
import httpx
from loguru import logger


class OllamaGateway:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", timeout: float = 30.0):
        self.base_url = base_url
        self.timeout = timeout

    async def generate_text(self, prompt: str, model: str = "gemma3:1b") -> str:
        """Envía un prompt a Ollama y maneja fallos de red de forma proactiva."""
        url = f"{self.base_url}/api/generate"
        # stream=False: esperar la respuesta completa antes de devolver
        payload = {"model": model, "prompt": prompt, "stream": False}

        logger.debug(f"Conectando a Ollama Local ({model})...")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()  # lanza HTTPStatusError si el status no es 2xx
                logger.success("Respuesta generada con éxito por IA Local.")
                # La respuesta JSON de Ollama tiene el texto generado en ["response"]
                return response.json()["response"]
            except httpx.ConnectError:
                # ConnectError: Ollama no está corriendo o el puerto es incorrecto
                logger.critical(
                    "Ollama no está en ejecución. ¿Lanzaste 'ollama serve'?"
                )
                raise


if __name__ == "__main__":

    async def main():
        gateway = OllamaGateway()
        res = await gateway.generate_text(
            "Define 'Arquitectura Hexagonal' en una frase corta."
        )
        print(f"\n[IA]: {res}")

    anyio.run(main)
