import pandas as pd
import requests
import time
from datetime import datetime


TARGET_WALLETS = [
    "0x1fa63a80d5f3b7b092e6b70dce5beba996a92fa6".lower(),
    "0x90210001ffdc5c90645c347a583922c1b9fe8e44".lower()
]

NETWORKS = {
    "arbitrum": {
        "explorer": "https://api.arbiscan.io/api",
        "api_key": "EGS2QWPD9G4DED41FZDYGP6XW6SI3JSJ5F",
        "native_token": "ARB"
    },
    "optimism": {
        "explorer": "https://api-optimistic.etherscan.io/api",
        "api_key": "TNM2RBE4NAZ3CTFC2NX2U2SEUNQQTXG66R",
        "native_token": "OP"
    },
    "fantom": {
        "explorer": "https://api.ftmscan.com/api",
        "api_key": "YOUR_FTMSCAN_API_KEY",
        "native_token": "FTM"
    },
    "base": {
        "explorer": "https://api.basescan.org/api",
        "api_key": "7K4BV9AUPWX9ZRSDYJ29QNI9MWI3M7PIZI",
        "native_token": "ETH"
    },
    "ethereum": {
        "explorer": "https://api.etherscan.io/api",
        "api_key": "15FYRR5CE2WABHFKIZ4VSEZCHVZSINDKMZ",
        "native_token": "ETH"
    },
    "polygon": {
        "explorer": "https://api.polygonscan.com/api",
        "api_key": "BMWIQ6ZY1GAW48SV5AX1USGBS1G99JQBXB",
        "native_token": "MATIC"
    },
    "bnb": {
        "explorer": "https://api.bscscan.com/api",
        "api_key": "ZUSGFQDS9D9FF26Q2YAD356BKS3T24PES2",
        "native_token": "BNB"
    }
}


# Проверка транзакций в сети
def check_transactions(network, wallet_address):
    interactions = []
    base_url = NETWORKS[network]["explorer"]
    api_key = NETWORKS[network]["api_key"]
    native_token = NETWORKS[network]["native_token"]

    # Параметры для запросов
    params = {
        "module": "",
        "action": "",
        "address": wallet_address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": api_key
    }

    # Обычные транзакции
    try:
        params["module"] = "account"
        params["action"] = "txlist"
        print(f"ℹ️ Запрашиваем обычные транзакции для {wallet_address} в {network.capitalize()}")
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data["status"] != "1":
            print(f"⚠️ Ошибка API {network.capitalize()}: {data.get('message', 'Неизвестная ошибка')}")
            return interactions

        for tx in data["result"]:
            tx_from = tx["from"].lower()
            tx_to = tx["to"].lower() if tx["to"] else ""
            if tx_from in TARGET_WALLETS or tx_to in TARGET_WALLETS:
                value = int(tx["value"]) / 1e18
                interactions.append({
                    "hash": tx["hash"],
                    "from": tx_from,
                    "to": tx_to,
                    "value": value,
                    "timestamp": datetime.fromtimestamp(int(tx["timeStamp"])),
                    "network": network,
                    "type": "transaction",
                    "token": native_token
                })
    except Exception as e:
        print(f"⚠️ Ошибка проверки обычных транзакций в {network.capitalize()}: {str(e)}")

    # ERC-20 трансферы
    try:
        params["module"] = "account"
        params["action"] = "tokentx"
        print(f"ℹ️ Запрашиваем ERC-20 трансферы для {wallet_address} в {network.capitalize()}")
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data["status"] != "1":
            print(f"⚠️ Ошибка API {network.capitalize()}: {data.get('message', 'Неизвестная ошибка')}")
            return interactions

        for tx in data["result"]:
            tx_from = tx["from"].lower()
            tx_to = tx["to"].lower()
            if tx_from in TARGET_WALLETS or tx_to in TARGET_WALLETS:
                interactions.append({
                    "hash": tx["hash"],
                    "from": tx_from,
                    "to": tx_to,
                    "value": float(tx["value"]) / (10 ** int(tx["tokenDecimal"])),
                    "timestamp": datetime.fromtimestamp(int(tx["timeStamp"])),
                    "network": network,
                    "type": "erc20",
                    "token": tx["tokenSymbol"]
                })
    except Exception as e:
        print(f"⚠️ Ошибка проверки ERC-20 в {network.capitalize()}: {str(e)}")

    # ERC-721 трансферы
    try:
        params["module"] = "account"
        params["action"] = "tokennfttx"
        print(f"ℹ️ Запрашиваем ERC-721 трансферы для {wallet_address} в {network.capitalize()}")
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data["status"] != "1":
            print(f"⚠️ Ошибка API {network.capitalize()}: {data.get('message', 'Неизвестная ошибка')}")
            return interactions

        for tx in data["result"]:
            tx_from = tx["from"].lower()
            tx_to = tx["to"].lower()
            if tx_from in TARGET_WALLETS or tx_to in TARGET_WALLETS:
                interactions.append({
                    "hash": tx["hash"],
                    "from": tx_from,
                    "to": tx_to,
                    "token_id": tx["tokenID"],
                    "timestamp": datetime.fromtimestamp(int(tx["timeStamp"])),
                    "network": network,
                    "type": "nft",
                    "token": tx["tokenName"]
                })
    except Exception as e:
        print(f"⚠️ Ошибка проверки ERC-721 в {network.capitalize()}: {str(e)}")

    return interactions


# Основная функция
def process_wallets(excel_file="wallets.xlsx"):
    try:
        df = pd.read_excel(excel_file)
        print(f"✅ Загружен файл {excel_file}")
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {str(e)}")
        return

    required_columns = ["Address"]
    if not all(col in df.columns for col in required_columns):
        print(f"❌ Отсутствуют столбцы: {required_columns}")
        return

    # Список для кошельков с совпадениями
    matched_wallets = []

    for index, row in df.iterrows():
        wallet_address = str(row["Address"]).strip().lower()
        print(f"\n=== Обработка кошелька {index + 1} ===")
        print(f"Адрес кошелька: {wallet_address}")

        # Проверяем, что адрес валидный
        if not wallet_address.startswith("0x") or len(wallet_address) != 42:
            print(f"❌ Некорректный адрес: {wallet_address}")
            continue

        # Проверяем взаимодействия
        total_interactions = 0
        for network in NETWORKS.keys():
            print(f"\nℹ️ Проверка {network.capitalize()}...")
            interactions = check_transactions(network, wallet_address)

            if interactions:
                print(f"✅ Найдено {len(interactions)} взаимодействий:")
                for i, interaction in enumerate(interactions, 1):
                    print(f"  {i}. Хэш: {interaction['hash']}")
                    print(f"     От: {interaction['from']}")
                    print(f"     Кому: {interaction['to']}")
                    if interaction["type"] == "transaction":
                        print(f"     Значение: {interaction['value']} {interaction['token']}")
                    elif interaction["type"] == "erc20":
                        print(f"     Токен: {interaction['token']} ({interaction['value']})")
                    elif interaction["type"] == "nft":
                        print(f"     NFT: {interaction['token']} (ID: {interaction['token_id']})")
                    print(f"     Время: {interaction['timestamp']}")
                total_interactions += len(interactions)
            else:
                print(f"ℹ️ Взаимодействий не найдено")

            # Задержка для лимитов API
            time.sleep(0.2)

        print(f"\n📊 Итог для {wallet_address}: {total_interactions} взаимодействий")

        # Если есть взаимодействия, добавляем кошелёк в список
        if total_interactions > 0:
            matched_wallets.append({
                "Address": wallet_address,
                "InteractionCount": total_interactions
            })

    # Сохраняем совпадающие кошельки в файл
    if matched_wallets:
        matched_df = pd.DataFrame(matched_wallets)
        output_file = "matched_wallets.xlsx"
        matched_df.to_excel(output_file, index=False)
        print(f"\n✅ Совпадающие кошельки сохранены в {output_file}")
    else:
        print("\nℹ️ Совпадающих кошельков не найдено")

    print("\n=== Обработка завершена ===")


if __name__ == "__main__":
    process_wallets("wallets.xlsx")
