import pandas as pd
from web3 import Web3
import json
import time

# Устанавливаем соединение с сетью Fantom
fantom_rpc_url = 'https://fantom-rpc.publicnode.com'
w3_fantom = Web3(Web3.HTTPProvider(fantom_rpc_url))
if not w3_fantom.is_connected():
    raise Exception('❌ Не удалось подключиться к Fantom RPC')

# Устанавливаем соединение с сетью Sonic
sonic_rpc_url = 'https://rpc.soniclabs.com'
w3_sonic = Web3(Web3.HTTPProvider(sonic_rpc_url))
if not w3_sonic.is_connected():
    raise Exception('❌ Не удалось подключиться к Sonic RPC')

# Адрес контракта для бриджа FTM → S
contract_address = '0x3561607590e28e0848ba3B67074C676d6d1c9953'

# ABI контракта (предполагается, что оно уже определено, как в твоём коде)
contract = w3_fantom.eth.contract(address=w3_fantom.to_checksum_address(contract_address), abi=contract_abi)

# Функция для проверки баланса FTM
def check_balance_ftm(private_key):
    try:
        account_address = w3_fantom.eth.account.from_key(private_key).address
        balance_wei = w3_fantom.eth.get_balance(account_address)
        balance_ftm = w3_fantom.from_wei(balance_wei, 'ether')
        return balance_ftm
    except Exception as e:
        print(f"❌ Ошибка проверки баланса FTM: {str(e)}")
        return 0

# Функция для проверки баланса S в Sonic
def check_balance_sonic(private_key):
    try:
        account_address = w3_sonic.eth.account.from_key(private_key).address
        balance_wei = w3_sonic.eth.get_balance(account_address)
        balance_s = w3_sonic.from_wei(balance_wei, 'ether')
        return balance_s
    except Exception as e:
        print(f"❌ Ошибка проверки баланса S: {str(e)}")
        return 0

# Функция для бриджа FTM → S
def bridge_ftm_to_sonic(private_key, amount_ftm):
    try:
        account = w3_fantom.eth.account.from_key(private_key)
        wallet_address = account.address

        print(f"ℹ️ Обрабатываем кошелёк: {wallet_address}")

        # Проверка адреса
        if not w3_fantom.is_address(wallet_address):
            raise Exception("Некорректный адрес кошелька")

        # Если amount_ftm = "max", берём весь баланс за вычетом газа
        if amount_ftm == "max":
            balance_wei = w3_fantom.eth.get_balance(wallet_address)
            gas_reserve = w3_fantom.to_wei(0.01, 'ether')  # Резерв для газа
            amount_to_deposit = max(balance_wei - gas_reserve, 0)
            print(f"ℹ️ Режим max: используем {w3_fantom.from_wei(amount_to_deposit, 'ether')} FTM")
        else:
            amount_to_deposit = w3_fantom.to_wei(amount_ftm, 'ether')

        # Проверка баланса FTM
        balance_wei = w3_fantom.eth.get_balance(wallet_address)
        if balance_wei < amount_to_deposit + w3_fantom.to_wei(0.01, 'ether'):
            print(f"❌ Недостаточно FTM для бриджа: {w3_fantom.from_wei(balance_wei, 'ether')} FTM, нужно {w3_fantom.from_wei(amount_to_deposit, 'ether')} FTM + 0.01 FTM для газа")
            return None

        # Проверка состояния контракта
        if contract.functions.paused().call():
            raise Exception("Контракт приостановлен")

        # Проверка лимитов депозита
        min_deposit = contract.functions.minDepositAmount().call()
        max_deposit = contract.functions.maxDepositAmount().call()
        if amount_to_deposit < min_deposit:
            raise Exception(f"Сумма ниже минимальной: {w3_fantom.from_wei(min_deposit, 'ether')} FTM")
        if amount_to_deposit > max_deposit and max_deposit != 0:
            raise Exception(f"Сумма выше максимальной: {w3_fantom.from_wei(max_deposit, 'ether')} FTM")

        # Проверка комиссии депозита
        deposit_fee = contract.functions.depositFee().call()
        print(f"ℹ️ Текущая комиссия контракта: {w3_fantom.from_wei(deposit_fee, 'ether')} FTM")
        if balance_wei < amount_to_deposit + deposit_fee + w3_fantom.to_wei(0.01, 'ether'):
            print(f"❌ Недостаточно FTM для комиссии: {w3_fantom.from_wei(balance_wei, 'ether')} FTM, нужно {w3_fantom.from_wei(amount_to_deposit + deposit_fee, 'ether')} FTM + 0.01 FTM для газа")
            return None

        # Получаем nonce
        nonce = w3_fantom.eth.get_transaction_count(wallet_address)

        # Подготовка транзакции для оценки газа
        tx_estimate = {
            'from': wallet_address,
            'value': amount_to_deposit,
            'nonce': nonce,
            'chainId': 250  # Fantom Opera
        }

        # Оценка газа
        estimated_gas = contract.functions.deposit(deposit_fee).estimate_gas(tx_estimate)
        gas = int(estimated_gas * 1.2)  # Буфер +20%
        print(f"ℹ️ Оценённый газ: {estimated_gas}, используем: {gas}")

        # Создаём транзакцию
        tx = contract.functions.deposit(deposit_fee).build_transaction({
            'from': wallet_address,
            'value': amount_to_deposit,
            'nonce': nonce,
            'gas': gas,
            'gasPrice': w3_fantom.eth.gas_price,
            'chainId': 250
        })

        # Подписываем и отправляем
        signed_tx = w3_fantom.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3_fantom.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"✅ Транзакция бриджа отправлена: {w3_fantom.to_hex(tx_hash)}")

        # Ждём подтверждения
        tx_receipt = w3_fantom.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        if tx_receipt.status == 1:
            print(f"✅ Успех бриджа! Хэш: {w3_fantom.to_hex(tx_hash)}")
            print(f"Fantom: https://explorer.fantom.network/tx/{w3_fantom.to_hex(tx_hash)}")
            return tx_hash
        else:
            raise Exception(f"Провал бриджа: https://explorer.fantom.network/tx/{w3_fantom.to_hex(tx_hash)}")
    except Exception as e:
        print(f"❌ Ошибка бриджа: {str(e)}")
        return None

# Функция для перевода S в Sonic
def transfer_sonic_tokens(private_key, destination_address):
    try:
        account = w3_sonic.eth.account.from_key(private_key)
        wallet_address = account.address

        print(f"ℹ️ Перевод S на {destination_address}")

        # Проверка адреса
        if not w3_sonic.is_address(destination_address):
            raise Exception("Некорректный адрес назначения")

        # Проверка баланса S
        balance_s_wei = w3_sonic.eth.get_balance(wallet_address)
        balance_s = w3_sonic.from_wei(balance_s_wei, 'ether')
        print(f"ℹ️ Баланс S: {balance_s} S")

        # Определяем сумму для перевода: весь баланс минус резерв для газа
        gas_reserve_s = w3_sonic.to_wei(0.001, 'ether')  # 0.001 S для газа
        transfer_amount = max(balance_s_wei - gas_reserve_s, 0)
        if transfer_amount <= 0:
            print(f"❌ Недостаточно S для перевода: {balance_s} S, нужно больше 0.001 S")
            return None

        print(f"ℹ️ Отправляем весь доступный баланс: {w3_sonic.from_wei(transfer_amount, 'ether')} S")

        # Получаем chainId динамически
        sonic_chain_id = w3_sonic.eth.chain_id
        print(f"ℹ️ Используем chainId для Sonic: {sonic_chain_id}")

        # Создаём транзакцию
        nonce = w3_sonic.eth.get_transaction_count(wallet_address)
        sonic_tx = {
            'from': wallet_address,
            'to': w3_sonic.to_checksum_address(destination_address),
            'value': transfer_amount,
            'nonce': nonce,
            'chainId': sonic_chain_id,
            'gasPrice': w3_sonic.eth.gas_price
        }

        # Оценка газа
        sonic_gas = w3_sonic.eth.estimate_gas(sonic_tx)
        sonic_tx['gas'] = int(sonic_gas * 1.5)  # Буфер +50%
        print(f"ℹ️ Оценённый газ для Sonic: {sonic_gas}, используем: {sonic_tx['gas']}")

        # Подписываем и отправляем
        signed_sonic_tx = w3_sonic.eth.account.sign_transaction(sonic_tx, private_key)
        sonic_tx_hash = w3_sonic.eth.send_raw_transaction(signed_sonic_tx.raw_transaction)
        print(f"✅ Перевод S отправлен: {w3_sonic.to_hex(sonic_tx_hash)}")

        # Ждём подтверждения
        sonic_receipt = w3_sonic.eth.wait_for_transaction_receipt(sonic_tx_hash, timeout=120)
        if sonic_receipt.status == 1:
            print(f"✅ Успех! S переведены на {destination_address}")
            print(f"Sonic: https://sonicscan.org/tx/{w3_sonic.to_hex(sonic_tx_hash)}")
            return sonic_tx_hash
        else:
            raise Exception(f"Провал перевода S: https://sonicscan.org/tx/{w3_sonic.to_hex(sonic_tx_hash)}")
    except Exception as e:
        print(f"❌ Ошибка перевода S: {str(e)}")
        return None

def process_wallets(excel_file='wallets.xlsx'):
    # Чтение Excel-файла
    try:
        df = pd.read_excel(excel_file)
        print(f"✅ Успешно загружен файл {excel_file}")
    except Exception as e:
        print(f"❌ Ошибка при чтении файла {excel_file}: {str(e)}")
        return

    # Проверка структуры файла
    required_columns = ['PrivateKey', 'Amount', 'Destination']
    if not all(col in df.columns for col in required_columns):
        print(f"❌ В файле {excel_file} отсутствуют необходимые столбцы: {required_columns}")
        return

    # Обработка каждого кошелька
    for index, row in df.iterrows():
        private_key = str(row['PrivateKey']).strip()
        amount_input = str(row['Amount']).strip().lower()
        destination = str(row['Destination']).strip()

        print(f"\n=== Обработка кошелька {index + 1} ===")
        print(f"Приватный ключ: {private_key[:6]}...{private_key[-6:]}")
        print(f"Сумма: {amount_input}")
        print(f"Адрес назначения: {destination}")

        # Проверка валидности приватного ключа
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key
        if not (len(private_key) == 66 and all(c in '0123456789abcdef' for c in private_key[2:])):
            print(f"❌ Неверный формат приватного ключа: должен быть 64-символьной шестнадцатеричной строкой с '0x'")
            continue

        # Проверка адреса назначения
        if not w3_sonic.is_address(destination):
            print(f"❌ Некорректный адрес назначения: {destination}")
            continue

        # Проверка баланса FTM
        balance_ftm = check_balance_ftm(private_key)
        print(f"💰 Баланс FTM: {balance_ftm:.6f} FTM")

        # Определяем сумму для бриджа
        if amount_input == "max":
            amount_ftm = "max"
            if balance_ftm < 0.01:
                print(f"❌ Недостаточно FTM для бриджа (режим max): {balance_ftm:.6f} FTM, нужно минимум 0.01 FTM для газа")
                continue
        else:
            try:
                amount_ftm = float(amount_input)
                if amount_ftm <= 0:
                    raise ValueError("Сумма должна быть положительной")
            except ValueError:
                print(f"❌ Неверный формат суммы: {amount_input}")
                continue

        # Выполняем бридж FTM → S
        bridge_tx = bridge_ftm_to_sonic(private_key, amount_ftm)
        if not bridge_tx:
            print(f"❌ Бридж не выполнен")
            continue

        # Ждём, пока S зачислятся
        print("ℹ️ Ожидаем зачисления S...")
        for attempt in range(3):
            sonic_balance = check_balance_sonic(private_key)
            if sonic_balance >= 0.001:
                break
            print(f"ℹ️ Попытка {attempt + 1}/3: S ещё не зачислены, ждём 60 секунд...")
            time.sleep(60)
        else:
            print(f"❌ Недостаточно S после ожидания: {sonic_balance:.6f} S. Проверьте позже: https://sonicscan.org")
            continue

        # Перевод S на destination в Sonic
        sonic_tx = transfer_sonic_tokens(private_key, destination)
        if not sonic_tx:
            print(f"❌ Перевод S не выполнен")
            continue

    print("\n=== Обработка всех кошельков завершена ===")

if __name__ == "__main__":
    process_wallets('wallets.xlsx')
