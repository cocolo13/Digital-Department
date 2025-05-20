from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import os

options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

os.makedirs('cian_results', exist_ok=True)


def parse_address(soup):
    try:
        address_div = soup.find("div", class_="a10a3f92e9--address--SMU25") or \
                      soup.find("div", {"data-name": "AddressContainer"})
        if address_div:
            address = address_div.get_text(" ", strip=True)
            return address.split("На карте")[0].strip()
        return None
    except Exception as e:
        print(f"Ошибка парсинга адреса: {e}")
        return None


def extract_detail(soup, label):
    try:
        for item in soup.find_all("div", {"data-name": "ObjectFactoidsItem"}):
            text = item.get_text(" ", strip=True)
            if label in text:
                return text.split(label)[-1].strip()
        return None
    except:
        return None


def parse_apartment(detail_url):
    driver.get(detail_url)
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-name='ObjectFactoids']")))
        soup = BeautifulSoup(driver.page_source, "html.parser")

        basic_fields = {
            "address": parse_address(soup),
            "total_area": extract_detail(soup, "Общая площадь"),
            "living_area": extract_detail(soup, "Жилая площадь"),
            "kitchen_area": extract_detail(soup, "Площадь кухни"),
            "floor": extract_detail(soup, "Этаж"),
            "house_type": extract_detail(soup, "Тип дома"),
            "built_year": extract_detail(soup, "Год постройки")
        }

        additional_fields = {
            "bathroom": extract_detail(soup, "Санузел"),
            "balcony": extract_detail(soup, "Балкон"),
            "renovation": extract_detail(soup, "Ремонт"),
            "ceiling_height": extract_detail(soup, "Высота потолков"),
            "price_per_m2": extract_detail(soup, "Цена за м²"),
            "building_series": extract_detail(soup, "Серия дома"),
            "elevator": extract_detail(soup, "Лифт"),
            "parking": extract_detail(soup, "Парковка"),
            "description": soup.find("div", class_="_93444fe79c--description--").get_text(strip=True)
            if soup.find("div", class_="_93444fe79c--description--") else None
        }
        return {**basic_fields, **additional_fields}
    except Exception as e:
        print(f"Ошибка парсинга квартиры: {e}")
        return None


def parse_page(page_url, page_num):
    driver.get(page_url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    apartments = []

    for card in soup.find_all("div", {"data-testid": "offer-card"}):
        try:
            link = card.find("a", class_="_93444fe79c--media--9P6wN")["href"]
            title = card.find("span", {"data-mark": "OfferTitle"}).get_text(strip=True)
            price = card.find("span", {"data-mark": "MainPrice"}).get_text(strip=True)

            apartment_data = {
                "title": title,
                "price": price,
                "link": link,
                **(parse_apartment(link) or {})
            }

            apartments.append(apartment_data)
            print(f"Страница {page_num}: обработано {len(apartments)}")

            driver.back()
            time.sleep(1)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='offer-card']")))

        except Exception as e:
            print(f"Ошибка карточки: {e}")
            continue

    with open(f'cian_results/page_{page_num}.json', 'w', encoding='utf-8') as f:
        json.dump(apartments, f, ensure_ascii=False, indent=4)

    return apartments


def main():
    all_apartments = []
    base_url = "https://krasnoyarsk.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&region=4827"

    for i in range(1, 54):
        print(f"\n=== Обработка страницы {i} ===")
        page_url = f"{base_url}&p={i}" if i > 1 else "https://krasnoyarsk.cian.ru/kupit-kvartiru/"

        page_apartments = parse_page(page_url, i)
        if page_apartments:
            all_apartments.extend(page_apartments)
            print(f"Найдено на странице: {len(page_apartments)}")
            print(f"Всего собрано: {len(all_apartments)}")

    with open('cian_results/all_apartments.json', 'w', encoding='utf-8') as f:
        json.dump(all_apartments, f, ensure_ascii=False, indent=4)

    print(f"\nЗавершено! Всего собрано: {len(all_apartments)} объявлений")
    print(f"Результаты сохранены в папке 'cian_results'")


if __name__ == "__main__":
    try:
        main()
    finally:
        driver.quit()
