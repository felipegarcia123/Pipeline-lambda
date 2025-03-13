"""Módulo para descargar páginas HTML y subirlas a S3."""

import datetime
import time
import boto3
import requests

S3_BUCKET = "landing-casas-juan123"  # Coincide con zappa_settings.json
s3_client = boto3.client("s3")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.google.com/",
}


def download_pages():
    """Descarga páginas HTML desde Mitula y las sube a S3.

    Retorna un diccionario con el estado y mensaje de la ejecución.
    """
    url_base = (
        "https://casas.mitula.com.co/find?operationType=sell"
        "&propertyType=mitula_studio_apartment"
        "&geoId=mitula-CO-poblacion-0000014156"
        "&text=Bogot%C3%A1%2C++%28Cundinamarca%29&page="
    )
    today = datetime.date.today().strftime("%Y-%m-%d")

    for i in range(1, 11):
        url = url_base + str(i)
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            if response.status_code == 200:
                file_name = f"{today}-page-{i}.html"
                file_path = f"/tmp/{file_name}"
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(response.text)
                s3_client.upload_file(file_path, S3_BUCKET, file_name)
                print(f"Guardado en S3: s3://{S3_BUCKET}/{file_name}")
        except Exception as e:
            print(f"Error al descargar {url}: {e}")
            continue
        time.sleep(3)

    print("Descarga completada.")
    return {"statusCode": 200, "body": "Descarga completada"}


def lambda_handler(event, context):
    """Punto de entrada de Lambda que invoca download_pages.

    Args:
        event: Diccionario con datos del evento.
        context: Objeto de contexto de AWS Lambda.

    Returns:
        Diccionario con el resultado de la ejecución.
    """
    return download_pages()


if __name__ == "__main__":
    download_pages()

# Nueva línea al final del archivo
