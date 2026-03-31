"""Concepto 01 — BaseModel y Field: estructura + constraints declarativos.

Pydantic valida los datos en el momento de creacion del objeto.
Los constraints se declaran en la definicion del modelo — no en codigo disperso.

Ejecutar:
    # Windows (PowerShell)
    uv run scripts/clase_09/conceptos/01_pydantic_basico.py

    # Linux
    uv run scripts/clase_09/conceptos/01_pydantic_basico.py
"""

from pydantic import BaseModel, Field, ValidationError


class Producto(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    precio: float = Field(gt=0, description="Precio en euros")
    stock: int = Field(ge=0, default=0)
    activo: bool = True


# --- Creacion valida ---
print("=== Creacion valida ===")
p = Producto(nombre="Laptop", precio=999.99, stock=5)
print(f"Producto: {p}")
print(f"dict:     {p.model_dump()}")
print(f"JSON:     {p.model_dump_json()}")

# --- Coercion automatica de tipos ---
print()
print("=== Coercion de tipos ===")
p2 = Producto(nombre="Mouse", precio="15.99", stock="10")
print(f"precio recibido como str, almacenado como: {type(p2.precio).__name__} = {p2.precio}")
print(f"stock  recibido como str, almacenado como: {type(p2.stock).__name__}  = {p2.stock}")

# --- ValidationError con detalles ---
print()
print("=== Validaciones fallidas ===")
casos_invalidos = [
    {"nombre": "", "precio": 10.0},            # nombre vacio
    {"nombre": "TV", "precio": -100.0},         # precio negativo
    {"nombre": "Silla", "precio": 50.0, "stock": -1},  # stock negativo
]
for caso in casos_invalidos:
    try:
        Producto(**caso)
    except ValidationError as e:
        for error in e.errors():
            print(f"  Campo '{error['loc'][0]}': {error['msg']}")

# --- model_validate desde dict ---
print()
print("=== model_validate (desde dict) ===")
datos = {"nombre": "Teclado", "precio": 45.0, "stock": 3}
p3 = Producto.model_validate(datos)
print(f"Validado: {p3}")

print()
print("Clave: los constraints estan en el modelo, no dispersos en el codigo.")
print("Si Producto cambia sus reglas, cambia en un solo lugar.")
