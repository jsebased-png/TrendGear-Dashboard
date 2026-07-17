"""
TrendGear - Generador de Dataset Sintético
============================================
Sigue la metodología de 4 pasos de la Fase I de la guía:
  1. Crear muestra       -> SEED_SAMPLE (8 registros hechos a mano)
  2. Limpiar muestra      -> clean_row() normaliza categorías y formatos
  3. One-shot prompting   -> expand_dataset() aprende el patrón de la muestra
                             y lo replica/escala controlando distribuciones
  4. Revisión             -> validate_dataset() aplica el checklist de
                             integridad y reporta hallazgos

Salidas: dataset.csv, dataset.psv, dataset.json (este último actúa como el
"nodo" de Firebase Realtime Database que consumirá el frontend).
"""

import csv
import json
import random
from datetime import date, timedelta

random.seed(42)

# ---------------------------------------------------------------------------
# PASO 1: Crear muestra (8 registros de referencia, escritos a mano)
# ---------------------------------------------------------------------------
SEED_SAMPLE = [
    {"Name": "Laura Gómez", "Product Purchased": "Laptop Gamer",
     "Age": 27, "City": "Bogotá", "Payment Method": "credit card",
     "Membership Status": "gold"},
    {"Name": "Andrés Pardo", "Product Purchased": "Auriculares Bluetooth",
     "Age": 34, "City": "Medellín", "Payment Method": "PayPal",
     "Membership Status": "silver"},
    {"Name": "Camila Ríos", "Product Purchased": "Smartwatch",
     "Age": 22, "City": "Cali", "Payment Method": "debit card",
     "Membership Status": "bronze"},
    {"Name": "Julián Torres", "Product Purchased": "Monitor 27''",
     "Age": 41, "City": "Cúcuta", "Payment Method": "credit card",
     "Membership Status": "gold"},
    {"Name": "Valentina Ortiz", "Product Purchased": "Teclado Mecánico",
     "Age": 19, "City": "Barranquilla", "Payment Method": "PayPal",
     "Membership Status": "bronze"},
    {"Name": "Santiago Vélez", "Product Purchased": "Mouse Inalámbrico",
     "Age": 29, "City": "Bucaramanga", "Payment Method": "debit card",
     "Membership Status": "silver"},
    {"Name": "Mariana Rojas", "Product Purchased": "Tablet 10''",
     "Age": 55, "City": "Pereira", "Payment Method": "credit card",
     "Membership Status": "gold"},
    {"Name": "Esteban Cárdenas", "Product Purchased": "Impresora 3D",
     "Age": 38, "City": "Cartagena", "Payment Method": "PayPal",
     "Membership Status": "silver"},
]

# Vocabulario controlado (evita valores "sucios" o inconsistentes)
PRODUCTS = ["Laptop Gamer", "Auriculares Bluetooth", "Smartwatch",
            "Monitor 27''", "Teclado Mecánico", "Mouse Inalámbrico",
            "Tablet 10''", "Impresora 3D", "Cámara Web 4K",
            "Parlante Portátil", "SSD Externo 1TB", "Silla Gamer"]
CITIES = ["Bogotá", "Medellín", "Cali", "Cúcuta", "Barranquilla",
          "Bucaramanga", "Pereira", "Cartagena", "Manizales", "Santa Marta"]
PAYMENT_METHODS = ["Credit Card", "Debit Card", "PayPal"]  # forma normalizada
MEMBERSHIP = ["Bronze", "Silver", "Gold"]
FIRST_NAMES = ["Laura", "Andrés", "Camila", "Julián", "Valentina", "Santiago",
               "Mariana", "Esteban", "Daniela", "Felipe", "Isabella", "Mateo",
               "Sara", "Nicolás", "Paula", "Diego", "Lucía", "Tomás"]
LAST_NAMES = ["Gómez", "Pardo", "Ríos", "Torres", "Ortiz", "Vélez", "Rojas",
              "Cárdenas", "Suárez", "Molina", "Herrera", "Castro", "Ramírez"]

SAFE_EMAIL_DOMAIN = "example.com"  # dominio seguro, sin datos reales


# ---------------------------------------------------------------------------
# PASO 2: Limpiar muestra (normalización de categorías y formatos)
# ---------------------------------------------------------------------------
def normalize_payment(value: str) -> str:
    # .title() rompería "PayPal" -> "Paypal", así que se resuelve por
    # coincidencia contra el catálogo normalizado en lugar de una regla ciega.
    cleaned = value.strip().lower()
    for canonical in PAYMENT_METHODS:
        if cleaned == canonical.lower():
            return canonical
    return value.strip().title()


def normalize_membership(value: str) -> str:
    return value.strip().capitalize()


def clean_row(row: dict) -> dict:
    row["Payment Method"] = normalize_payment(row["Payment Method"])
    row["Membership Status"] = normalize_membership(row["Membership Status"])
    return row


SEED_SAMPLE = [clean_row(r) for r in SEED_SAMPLE]


# ---------------------------------------------------------------------------
# PASO 3: One-shot prompting (escalado del patrón aprendido de la muestra)
# ---------------------------------------------------------------------------
def make_email(name: str, customer_id: str) -> str:
    slug = name.lower().replace(" ", ".")
    slug = (slug.replace("é", "e").replace("í", "i").replace("á", "a")
                .replace("ó", "o").replace("ú", "u"))
    return f"{slug}.{customer_id.lower()}@{SAFE_EMAIL_DOMAIN}"


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def generate_record(idx: int) -> dict:
    customer_id = f"TG-{idx:04d}"
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    age = max(13, min(100, int(random.gauss(32, 12))))  # distribución realista

    purchase_date = random_date(date(2024, 1, 1), date(2026, 6, 30))
    # el último login siempre es >= fecha de compra (coherencia cruzada)
    last_login = random_date(purchase_date, date(2026, 7, 16))

    amount = round(abs(random.gauss(320, 260)) + 15, 2)  # siempre >= 0

    return clean_row({
        "Customer ID": customer_id,
        "Name": name,
        "Email": make_email(name, customer_id),
        "Product Purchased": random.choice(PRODUCTS),
        "Purchase Date": purchase_date.isoformat(),
        "Amount Spent ($)": amount,
        "Age": age,
        "City": random.choice(CITIES),
        "Payment Method": random.choice(PAYMENT_METHODS),
        "Last Login Date": last_login.isoformat(),
        "Membership Status": random.choice(MEMBERSHIP),
    })


def expand_dataset(n: int = 60) -> list:
    return [generate_record(i) for i in range(1, n + 1)]


# ---------------------------------------------------------------------------
# PASO 4: Revisión (checklist de validación de integridad)
# ---------------------------------------------------------------------------
def validate_dataset(rows: list) -> list:
    issues = []
    seen_ids = set()

    for r in rows:
        # Números
        if not (13 <= r["Age"] <= 100):
            issues.append(f"Edad fuera de rango: {r['Customer ID']}")
        if r["Amount Spent ($)"] < 0:
            issues.append(f"Monto negativo: {r['Customer ID']}")

        # Fechas (formato ISO + coherencia compra <= último login, sin futuro)
        p_date = date.fromisoformat(r["Purchase Date"])
        l_date = date.fromisoformat(r["Last Login Date"])
        if p_date > l_date:
            issues.append(f"Fecha de compra posterior al último login: {r['Customer ID']}")
        if p_date > date.today() or l_date > date.today():
            issues.append(f"Fecha futura detectada: {r['Customer ID']}")

        # Categorías normalizadas
        if r["Payment Method"] not in PAYMENT_METHODS:
            issues.append(f"Método de pago no normalizado: {r['Customer ID']}")
        if r["Membership Status"] not in MEMBERSHIP:
            issues.append(f"Membresía no normalizada: {r['Customer ID']}")

        # Unicidad
        if r["Customer ID"] in seen_ids:
            issues.append(f"ID duplicado: {r['Customer ID']}")
        seen_ids.add(r["Customer ID"])

        # Coherencia cruzada de correo y ciudad
        if not r["Email"].endswith(f"@{SAFE_EMAIL_DOMAIN}"):
            issues.append(f"Dominio de correo no seguro: {r['Customer ID']}")
        if r["City"] not in CITIES:
            issues.append(f"Ciudad fuera de catálogo: {r['Customer ID']}")

    return issues


def main():
    dataset = expand_dataset(60)
    issues = validate_dataset(dataset)

    print(f"Registros generados: {len(dataset)}")
    if issues:
        print(f"Hallazgos en validación ({len(issues)}):")
        for i in issues:
            print(" -", i)
    else:
        print("Validación superada: 0 inconsistencias detectadas.")

    fieldnames = list(dataset[0].keys())

    with open("/home/claude/trendgear/data/dataset.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dataset)

    with open("/home/claude/trendgear/data/dataset.psv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
        writer.writeheader()
        writer.writerows(dataset)

    # Estructura tipo Firebase Realtime Database: nodo "customers" con IDs como claves
    firebase_like = {row["Customer ID"]: row for row in dataset}
    with open("/home/claude/trendgear/data/dataset.json", "w", encoding="utf-8") as f:
        json.dump(firebase_like, f, ensure_ascii=False, indent=2)

    # Estadísticas rápidas para el checklist de coherencia cruzada
    amounts = [r["Amount Spent ($)"] for r in dataset]
    ages = [r["Age"] for r in dataset]
    print(f"\nAmount Spent -> media: {sum(amounts)/len(amounts):.2f}, "
          f"min: {min(amounts):.2f}, max: {max(amounts):.2f}")
    print(f"Age -> media: {sum(ages)/len(ages):.2f}, "
          f"min: {min(ages)}, max: {max(ages)}")


if __name__ == "__main__":
    main()
