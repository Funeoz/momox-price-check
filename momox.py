from time import sleep
from pyzbar import pyzbar
from glob import glob
import cv2
import requests


def get_momox_price(ean: str):
    headers = {
        "Host": "api.momox.fr",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "*/*",
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.momox.fr/",
        "X-CLIENT-VERSION": "r5417-21d471",
        "X-API-TOKEN": "2231443b8fb511c7b6a0eb25a62577320bac69b6",
        "X-MARKETPLACE-ID": "momox_fr",
        "Content-Type": "application/json",
        "Origin": "https://www.momox.fr",
        "Connection": "keep-alive",
    }
    print(ean)
    r = requests.get(
        f"https://api.momox.fr/api/v4/offer/?ean={ean}", headers=headers
    ).json()
    if r["status"] == "no_offer":
        with open("not_bought_books.txt", "a+", encoding="utf-8") as f:
            f.write(f"{r['product']['title']}, {r['product']['ean']}\n")
    elif r["status"] == "offer":
        with open("bought_books.txt", "a+", encoding="utf-8") as f:
            f.write(f"{r['product']['title']}, {r['product']['ean']}, {r['price']}\n")
    elif r["status"] == "unknown":
        with open("unknown.txt", "a+", encoding="utf-8") as f:
            f.write(ean + "\n")

def decode(image):
    # decodes all barcodes from an image
    decoded_objects = pyzbar.decode(image)
    for obj in decoded_objects:
        image = draw_barcode(obj, image)
        # Append barcode data in books.txt
        with open("books.txt", "a+") as f:
            f.write(f.read() + f"\n{int(obj.data)}")
    return image


def draw_barcode(decoded, image):
    image = cv2.rectangle(image, (decoded.rect.left, decoded.rect.top), 
                            (decoded.rect.left + decoded.rect.width, decoded.rect.top + decoded.rect.height),
                            color=(0, 255, 0),
                            thickness=5)
    return image


if __name__ == "__main__":
    # Get every barcode image from the Barcodes folder
    barcodes = glob("Barcodes/*.png") + glob("Barcodes/*.jpeg")
    for barcode_file in barcodes:
        # load the image to opencv
        img = cv2.imread(barcode_file)
        # decode detected barcodes & get the image
        # that is drawn
        img = decode(img)

    # Read barcodes from books.txt
    with open("books.txt", "r") as f:
        for line in f:
            get_momox_price(line.strip())
            sleep(0.5)
