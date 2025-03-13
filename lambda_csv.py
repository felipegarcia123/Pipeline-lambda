"""Módulo para procesar archivos HTML de S3 y generar un CSV."""

import datetime
import csv
import boto3
from bs4 import BeautifulSoup

INPUT_BUCKET = "landing-casas-juan123"  # Coincide con zappa_settings.json
OUTPUT_BUCKET = "casas-final-lambda2"

s3 = boto3.client("s3")


def process_html():
    """Procesa archivos HTML de S3 y genera un CSV con datos de propiedades.

    Retorna un diccionario con el estado y mensaje de la ejecución.
    """
    today = datetime.date.today().strftime("%Y-%m-%d")
    output_file = f"/tmp/casas_data_{today}.csv"
    csv_data = []

    try:
        response = s3.list_objects_v2(Bucket=INPUT_BUCKET)
        if "Contents" in response:
            page_number = 0
            for obj in sorted(response["Contents"], key=lambda x: x["Key"]):
                file_name = obj["Key"]
                if (file_name.endswith(".html") and
                        today in file_name):
                    page_number += 1
                    html_obj = s3.get_object(
                        Bucket=INPUT_BUCKET,
                        Key=file_name
                    )
                    html_content = html_obj["Body"].read().decode("utf-8")
                    soup = BeautifulSoup(html_content, "html.parser")
                    listings_container = soup.find(
                        "div",
                        class_="listings__cards"
                    )
                    print("Listings container:", listings_container)
                    if listings_container:
                        listings = listings_container.find_all(
                            "a",
                            class_="listing listing-card"
                        )
                    else:
                        listings = []
                    print("Listings:", listings)
                    for listing in listings:
                        barrio = listing.get("data-location", "N/A")
                        valor = listing.get("data-price", "N/A")
                        habitaciones = listing.get("data-rooms", "N/A")
                        banos_tag = listing.find(
                            "p",
                            {"data-test": "bathrooms"}
                        )
                        banos = banos_tag.text.strip() if banos_tag else "N/A"
                        metros = listing.get("data-floorarea", "N/A")
                        csv_data.append([
                            today,
                            page_number,
                            barrio,
                            valor,
                            habitaciones,
                            banos,
                            metros,
                        ])

        if csv_data:
            with open(
                output_file,
                "w",
                newline="",
                encoding="utf-8"
            ) as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    "FechaDescarga",
                    "Pagina",
                    "Barrio",
                    "Valor",
                    "NumHabitaciones",
                    "NumBanos",
                    "mts2",
                ])
                writer.writerows(csv_data)
            s3.upload_file(
                output_file,
                OUTPUT_BUCKET,
                f"casas_data_{today}.csv"
            )
            print(
                f"CSV guardado en s3://{OUTPUT_BUCKET}/"
                f"casas_data_{today}.csv"
            )

    except Exception as e:
        print(f"Error en process_html: {e}")
        return {"status": "error", "message": str(e)}

    return {"statusCode": 200, "body": "Proceso completado"}


def lambda_handler(event, context):
    """Punto de entrada de Lambda que invoca process_html.

    Args:
        event: Diccionario con datos del evento.
        context: Objeto de contexto de AWS Lambda.

    Returns:
        Diccionario con el resultado de la ejecución.
    """
    return process_html()


if __name__ == "__main__":
    process_html()

# Nueva línea al final del archivo
