# 🚀 Python Pro — Ingeniería de Software con PyCommute

> **De programador intermedio a ingeniero senior moderno**
> 13 clases · 120 min c/u · Online en vivo

---

## 🎯 ¿De qué trata este curso?

No es un curso de sintaxis. Es una **aceleradora de ingeniería**.

Construís un único proyecto real durante las 13 clases — **PyCommute**, un asesor de movilidad inteligente que consume APIs de clima y tráfico, procesa datos con algoritmos de prioridad y genera recomendaciones con IA híbrida.

Al final del curso no solo dominás Python — dominás el **ciclo de vida completo** de un proyecto profesional.

---

## 🗺️ El proyecto: PyCommute

Un sistema real, no un ejercicio de juguete:

| Funcionalidad | Tecnología |
|---------------|------------|
| Clima en tiempo real | OpenWeather API |
| Rutas y tráfico | OpenRouteService API |
| Recomendaciones IA cloud | Google Gemini |
| Fallback IA local | Ollama (Llama / Gemma) |
| API REST productiva | FastAPI |
| Interfaz de demo | Gradio |
| Deploy | Docker Compose |

---

## 📚 Estructura del Curso

### 🛠️ Fase 1 — Ingeniería de Software (Clases 1–4)
| Clase | Tema | Hito |
|-------|------|------|
| 01 | Setup profesional: UV, Docker, Git | Primera llamada real a OpenWeather |
| 02 | Parsing moderno con `match/case` | JSON de APIs procesado con Pattern Matching |
| 03 | Resiliencia: Loguru, Pydantic-Settings, @retry | App que no rompe ante fallos de red |
| 04 | Testing con pytest y mocks | Suite de tests que no consume cuota de APIs |

### ⚡ Fase 2 — Alto Rendimiento (Clases 5–7)
| Clase | Tema | Hito |
|-------|------|------|
| 05 | Concurrencia con anyio + httpx | Llamadas paralelas — 3x más rápido |
| 06 | Profiling y optimización de memoria | Sin cuellos de botella identificados |
| 07 | Algoritmia: heapq y deque | Ranking de rutas en tiempo real |

### 🏛️ Fase 3 — Arquitectura e IA (Clases 8–11)
| Clase | Tema | Hito |
|-------|------|------|
| 08 | Arquitectura hexagonal con Protocol | Lógica de negocio desacoplada de APIs |
| 09 | Contratos con Pydantic V2 | Datos validados entre todas las capas |
| 10 | IA Cloud — Gemini API | Recomendaciones en lenguaje natural |
| 11 | IA Local — Ollama + fallback | App funciona offline con modelo local |

### 🚀 Fase 4 — Producto y Deploy (Clases 12–13)
| Clase | Tema | Hito |
|-------|------|------|
| 12 | FastAPI con inyección de dependencias | API REST lista para producción |
| 13 | Docker Compose + Gradio + GitHub Actions | Deploy completo con CI/CD automático |

---

## 🗂️ Estructura del Repositorio

```
pycommute-elite/
│
├── src/pycommute/        ← el proyecto — versión final
├── tests/                ← suite de tests completa
│
├── snapshots/            ← historial pedagógico clase a clase
│   ├── clase_01/         ← cómo era el código al terminar Clase 1
│   ├── clase_02/         ← con Pattern Matching agregado
│   └── ...               ← cada clase documenta su evolución
│
├── scripts/              ← scripts de demo y ejemplos por clase
│   └── clase_XX/
│       ├── conceptos/    ← un script ejecutable por concepto
│       └── demo_*.py     ← demo del hito del proyecto
│
└── docs/                 ← material del alumno por clase
    └── clase_XX/
        ├── 01_conceptos.md   ← teoría con ejemplos ejecutables
        └── 02_lab_guide.md   ← práctica paso a paso
```

> 💡 **¿Cómo estudiar?** Empezá por `docs/clase_XX/01_conceptos.md`,
> ejecutá los scripts en `scripts/clase_XX/conceptos/`,
> luego seguí el `02_lab_guide.md` para construir en el proyecto.

---

## 🛠️ Stack Técnico

```
Entorno      uv · Docker · Git + GitHub
Calidad      loguru · pydantic-settings · tenacity · pytest · ruff
HTTP         httpx · anyio
Arquitectura typing.Protocol · pydantic v2
IA           google-generativeai · ollama
Producto     fastapi · uvicorn · gradio · docker compose
CI/CD        GitHub Actions
```

---

## ⚡ Requisitos Previos

**Conocimientos:**
- Python básico — funciones, clases, listas, dicts
- Haber consumido alguna API con `requests`
- Git básico — add, commit, push

**Setup (se prepara en Clase 1):**
- Cuenta en GitHub
- VS Code
- VM Ubuntu provista por el curso

---

## 🚀 Inicio Rápido

```bash
# Clonar el repo
git clone https://github.com/franxiscodev/curso-python-avanzado.git
cd pycommute-elite

# Instalar dependencias
uv sync

# Configurar variables de entorno
cp .env.example .env
# → editar .env con tus API keys

# Verificar que todo funciona
uv run python scripts/clase_01/demo_weather.py
# [INFO] PyCommute v0.1.0 iniciado
# [INFO] Clima en Valencia: 24°C, clear sky

# Correr los tests
uv run pytest tests/ -v
```

---

## 📈 Perfil de Salida

Al terminar este curso sabés:

- ✅ Estructurar proyectos Python que escalen
- ✅ Escribir código mantenible con tipado estricto
- ✅ Integrar APIs externas con resiliencia real
- ✅ Diseñar arquitecturas hexagonales desacopladas
- ✅ Conectar modelos de IA cloud y local con fallback automático
- ✅ Automatizar calidad con GitHub Actions
- ✅ Desplegar sistemas con Docker Compose

---

*"El código que funciona es el mínimo.*
*El código bien diseñado, trazable y automatizado*
*es el que construye una carrera senior."*
