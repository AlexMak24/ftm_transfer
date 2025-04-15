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

# ABI контракта (без изменений)
contract_abi = json.loads('''[{"inputs":[{"internalType":"address","name":"_cfgAdmin","type":"address"},{"internalType":"uint256","name":"_peerChainID","type":"uint256"},{"internalType":"uint256","name":"_fee","type":"uint256"},{"internalType":"uint256","name":"_minDeposit","type":"uint256"},{"internalType":"uint256","name":"_sigThreshold","type":"uint256"},{"internalType":"uint256","name":"_batchCheckpoint","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"AccessControlBadConfirmation","type":"error"},{"inputs":[{"internalType":"uint48","name":"schedule","type":"uint48"}],"name":"AccessControlEnforcedDefaultAdminDelay","type":"error"},{"inputs":[],"name":"AccessControlEnforcedDefaultAdminRules","type":"error"},{"inputs":[{"internalType":"address","name":"defaultAdmin","type":"address"}],"name":"AccessControlInvalidDefaultAdmin","type":"error"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"bytes32","name":"neededRole","type":"bytes32"}],"name":"AccessControlUnauthorizedAccount","type":"error"},{"inputs":[{"internalType":"uint256","name":"limit","type":"uint256"},{"internalType":"uint256","name":"balance","type":"uint256"}],"name":"BalanceBelowLimit","type":"error"},{"inputs":[{"internalType":"uint256","name":"limit","type":"uint256"},{"internalType":"uint256","name":"balance","type":"uint256"}],"name":"BalanceOverLimit","type":"error"},{"inputs":[{"internalType":"uint256","name":"expected","type":"uint256"},{"internalType":"uint256","name":"received","type":"uint256"}],"name":"DepositAboveLimit","type":"error"},{"inputs":[{"internalType":"uint256","name":"expected","type":"uint256"},{"internalType":"uint256","name":"received","type":"uint256"}],"name":"DepositBelowLimit","type":"error"},{"inputs":[{"internalType":"uint256","name":"depositID","type":"uint256"}],"name":"DepositNotFound","type":"error"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"DepositSettlementFailed","type":"error"},{"inputs":[{"internalType":"address","name":"target","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"DrainFailed","type":"error"},{"inputs":[],"name":"ECDSAInvalidSignature","type":"error"},{"inputs":[{"internalType":"uint256","name":"length","type":"uint256"}],"name":"ECDSAInvalidSignatureLength","type":"error"},{"inputs":[{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"ECDSAInvalidSignatureS","type":"error"},{"inputs":[],"name":"EnforcedPause","type":"error"},{"inputs":[],"name":"ExpectedPause","type":"error"},{"inputs":[{"internalType":"uint256","name":"expected","type":"uint256"},{"internalType":"uint256","name":"received","type":"uint256"}],"name":"FeeChanged","type":"error"},{"inputs":[{"internalType":"uint256","name":"available","type":"uint256"},{"internalType":"uint256","name":"needed","type":"uint256"}],"name":"InsufficientLiquidity","type":"error"},{"inputs":[{"internalType":"uint256","name":"lastID","type":"uint256"},{"internalType":"uint256","name":"currentID","type":"uint256"}],"name":"InvalidBatchSequence","type":"error"},{"inputs":[{"internalType":"address","name":"expectedSender","type":"address"}],"name":"InvalidClaimRequests","type":"error"},{"inputs":[{"internalType":"uint256","name":"lastID","type":"uint256"},{"internalType":"uint256","name":"receivedID","type":"uint256"}],"name":"InvalidDepositSequence","type":"error"},{"inputs":[{"internalType":"uint256","name":"expected","type":"uint256"},{"internalType":"uint256","name":"received","type":"uint256"}],"name":"InvalidDepositSum","type":"error"},{"inputs":[],"name":"InvalidDrainAddress","type":"error"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"InvalidImplicitDeposit","type":"error"},{"inputs":[{"internalType":"uint256","name":"maxDeposit","type":"uint256"},{"internalType":"uint256","name":"minDeposit","type":"uint256"}],"name":"InvalidMaxDepositToMinDeposit","type":"error"},{"inputs":[{"internalType":"uint256","name":"minDeposit","type":"uint256"},{"internalType":"uint256","name":"fee","type":"uint256"}],"name":"InvalidMinDepositToFee","type":"error"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"address","name":"sender","type":"address"}],"name":"InvalidRecipient","type":"error"},{"inputs":[],"name":"InvalidSignatureThreshold","type":"error"},{"inputs":[],"name":"ReentrancyGuardReentrantCall","type":"error"},{"inputs":[{"internalType":"uint8","name":"bits","type":"uint8"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"SafeCastOverflowedUintDowncast","type":"error"},{"inputs":[{"internalType":"uint256","name":"threshold","type":"uint256"},{"internalType":"uint256","name":"received","type":"uint256"}],"name":"SignatureDeficit","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"id","type":"uint256"}],"name":"BatchProcessed","type":"event"},{"anonymous":false,"inputs":[],"name":"DefaultAdminDelayChangeCanceled","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint48","name":"newDelay","type":"uint48"},{"indexed":false,"internalType":"uint48","name":"effectSchedule","type":"uint48"}],"name":"DefaultAdminDelayChangeScheduled","type":"event"},{"anonymous":false,"inputs":[],"name":"DefaultAdminTransferCanceled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"newAdmin","type":"address"},{"indexed":false,"internalType":"uint48","name":"acceptSchedule","type":"uint48"}],"name":"DefaultAdminTransferScheduled","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"newDepositFee","type":"uint256"}],"name":"DepositFeeUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"recipient","type":"address"},{"indexed":true,"internalType":"uint256","name":"id","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"fee","type":"uint256"}],"name":"Deposited","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"recipient","type":"address"},{"indexed":true,"internalType":"uint256","name":"id","type":"uint256"}],"name":"Failed","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"newMaximalDepositAmount","type":"uint256"}],"name":"MaximalDepositAmountUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"newMinimalDepositAmount","type":"uint256"}],"name":"MinimalDepositAmountUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"newReserveAmount","type":"uint256"},{"indexed":false,"internalType":"address","name":"newReserveDrain","type":"address"}],"name":"ReserveBalanceUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"recipient","type":"address"},{"indexed":true,"internalType":"uint256","name":"id","type":"uint256"}],"name":"Resolved","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"previousAdminRole","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"newAdminRole","type":"bytes32"}],"name":"RoleAdminChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleGranted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleRevoked","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"newSignatureThreshold","type":"uint256"}],"name":"SignatureThresholdUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"inputs":[],"name":"DEFAULT_ADMIN_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"PAUSE_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"VALIDATOR_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"acceptDefaultAdminTransfer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newAdmin","type":"address"}],"name":"beginDefaultAdminTransfer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"cancelDefaultAdminTransfer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint48","name":"newDelay","type":"uint48"}],"name":"changeDefaultAdminDelay","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"depositID","type":"uint256"},{"internalType":"address","name":"receiver","type":"address"}],"name":"claim","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"defaultAdmin","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"defaultAdminDelay","outputs":[{"internalType":"uint48","name":"","type":"uint48"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"defaultAdminDelayIncreaseWait","outputs":[{"internalType":"uint48","name":"","type":"uint48"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"fee","type":"uint256"}],"name":"deposit","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"depositFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"drain","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"}],"name":"getRoleAdmin","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"grantRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"hasRole","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"lastBatchID","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"lastDepositID","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"lastResolvedDepositID","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"maxDepositAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"minDepositAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"peerChainID","outputs":[{"internalType":"uint256","name":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pendingDefaultAdmin","outputs":[{"internalType":"address","name":"newAdmin","type":"address"},{"internalType":"uint48","name":"schedule","type":"uint48"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pendingDefaultAdminDelay","outputs":[{"internalType":"uint48","name":"newDelay","type":"uint48"},{"internalType":"uint48","name":"schedule","type":"uint48"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"refill","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"renounceRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"reserveBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"reserveDrain","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"batchID","type":"uint256"},{"internalType":"uint256","name":"total","type":"uint256"},{"components":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"internalType":"struct OperaBridge.Deposit[]","name":"deposits","type":"tuple[]"},{"internalType":"bytes[]","name":"signatures","type":"bytes[]"}],"name":"resolve","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"revokeRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"rollbackDefaultAdminDelay","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_fee","type":"uint256"}],"name":"setDepositFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_max","type":"uint256"}],"name":"setMaximalDeposit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_min","type":"uint256"}],"name":"setMinimalDeposit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_balance","type":"uint256"},{"internalType":"address","name":"_drain","type":"address"}],"name":"setReserveBalance","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_threshold","type":"uint256"}],"name":"setSignatureThreshold","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"signatureThreshold","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"depositID","type":"uint256"}],"name":"unresolvedDeposit","outputs":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"stateMutability":"view","type":"function"},{"stateMutability":"payable","type":"receive"}]''')
contract = w3_fantom.eth.contract(address=w3_fantom.to_checksum_address(contract_address), abi=contract_abi)

# Функция для проверки баланса FTM
def check_balance_ftm(private_key):
    try:
        account_address = w3_fantom.eth.account.from_key(private_key).address
        balance_wei = w3_fantom.eth.get_balance(account_address)
        balance_ftm = w3_fantom.from_wei(balance_wei, 'ether')
        return balance_wei, balance_ftm
    except Exception as e:
        print(f"❌ Ошибка проверки баланса FTM: {str(e)}")
        return 0, 0

# Функция для проверки баланса S в Sonic
def check_balance_sonic(private_key):
    try:
        account_address = w3_sonic.eth.account.from_key(private_key).address
        balance_wei = w3_sonic.eth.get_balance(account_address)
        balance_s = w3_sonic.from_wei(balance_wei, 'ether')
        return balance_wei, balance_s
    except Exception as e:
        print(f"❌ Ошибка проверки баланса S: {str(e)}")
        return 0, 0

# Функция для бриджа FTM → S
def bridge_ftm_to_sonic(private_key):
    try:
        account = w3_fantom.eth.account.from_key(private_key)
        wallet_address = account.address

        print(f"ℹ️ Обрабатываем кошелёк: {wallet_address}")

        # Проверка адреса
        if not w3_fantom.is_address(wallet_address):
            raise Exception("Некорректный адрес кошелька")

        # Проверка состояния контракта
        if contract.functions.paused().call():
            raise Exception("Контракт приостановлен")

        # Получаем баланс FTM
        balance_wei, balance_ftm = check_balance_ftm(private_key)
        print(f"ℹ️ Баланс FTM: {balance_ftm} FTM")

        # Проверка комиссии депозита
        deposit_fee = contract.functions.depositFee().call()
        deposit_fee_ftm = w3_fantom.from_wei(deposit_fee, 'ether')
        print(f"ℹ️ Комиссия контракта: {deposit_fee_ftm} FTM")

        # Проверка лимитов депозита
        min_deposit = contract.functions.minDepositAmount().call()
        max_deposit = contract.functions.maxDepositAmount().call()
        min_deposit_ftm = w3_fantom.from_wei(min_deposit, 'ether')
        max_deposit_ftm = w3_fantom.from_wei(max_deposit, 'ether') if max_deposit != 0 else "без лимита"
        print(f"ℹ️ Лимиты депозита: мин={min_deposit_ftm} FTM, макс={max_deposit_ftm}")

        # Проверка баланса на минимальный депозит
        if balance_wei < min_deposit + deposit_fee:
            print(f"❌ Недостаточно FTM для минимального депозита: {balance_ftm} FTM, нужно минимум {w3_fantom.from_wei(min_deposit + deposit_fee, 'ether')} FTM")
            return None

        # Предполагаемая сумма для оценки газа (берём весь баланс минус комиссия)
        estimated_deposit = max(balance_wei - deposit_fee, min_deposit)
        nonce = w3_fantom.eth.get_transaction_count(wallet_address)
        tx_estimate = {
            'from': wallet_address,
            'value': estimated_deposit,
            'nonce': nonce,
            'chainId': 250  # Fantom Opera
        }

        # Оценка газа
        try:
            estimated_gas = contract.functions.deposit(deposit_fee).estimate_gas(tx_estimate)
        except Exception as e:
            print(f"❌ Ошибка оценки газа: {str(e)}")
            return None
        gas_limit = int(estimated_gas * 1.2)  # Буфер +20%
        gas_price = w3_fantom.eth.gas_price
        gas_cost = gas_price * gas_limit
        gas_cost_ftm = w3_fantom.from_wei(gas_cost, 'ether')
        print(f"ℹ️ Оценка газа: limit={gas_limit}, price={w3_fantom.from_wei(gas_price, 'gwei')} gwei, стоимость={gas_cost_ftm} FTM")

        # Вычисляем максимальную сумму для бриджа
        amount_to_deposit = max(balance_wei - deposit_fee - gas_cost, 0)
        amount_to_deposit_ftm = w3_fantom.from_wei(amount_to_deposit, 'ether')
        print(f"ℹ️ Максимум для бриджа: {amount_to_deposit_ftm} FTM")

        # Проверки
        if amount_to_deposit <= 0:
            print(f"❌ Сумма для бриджа равна нулю: баланс {balance_ftm} FTM, комиссия {deposit_fee_ftm} FTM, газ {gas_cost_ftm} FTM")
            return None
        if balance_wei < amount_to_deposit + deposit_fee + gas_cost:
            print(f"❌ Недостаточно FTM: {balance_ftm} FTM, нужно {w3_fantom.from_wei(amount_to_deposit + deposit_fee + gas_cost, 'ether')} FTM")
            return None
        if amount_to_deposit < min_deposit:
            print(f"❌ Сумма ниже минимальной: {amount_to_deposit_ftm} FTM, нужно {min_deposit_ftm} FTM")
            return None
        if max_deposit != 0 and amount_to_deposit > max_deposit:
            print(f"❌ Сумма выше максимальной: {amount_to_deposit_ftm} FTM, макс {max_deposit_ftm} FTM")
            return None

        # Создаём транзакцию
        tx = contract.functions.deposit(deposit_fee).build_transaction({
            'from': wallet_address,
            'value': amount_to_deposit,
            'nonce': nonce,
            'gas': gas_limit,
            'gasPrice': gas_price,
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

# Функция для перевода S в Sonic (без изменений)
def transfer_sonic_tokens(private_key, destination_address):
    try:
        account = w3_sonic.eth.account.from_key(private_key)
        wallet_address = account.address

        print(f"ℹ️ Перевод S на {destination_address}")

        # Проверка адреса
        if not w3_sonic.is_address(destination_address):
            raise Exception("Некорректный адрес назначения")

        # Проверка баланса S
        balance_s_wei, balance_s = check_balance_sonic(private_key)
        print(f"ℹ️ Баланс S: {balance_s} S")

        # Параметры газа
        gas_limit = 30000  # Фиксированный лимит с запасом
        gas_price = w3_sonic.eth.gas_price
        gas_cost = gas_price * gas_limit
        gas_cost_s = w3_sonic.from_wei(gas_cost, 'ether')
        print(f"ℹ️ Стоимость газа: {gas_cost_s} S (gas_limit={gas_limit}, gas_price={w3_sonic.from_wei(gas_price, 'gwei')} gwei)")

        # Проверка достаточности баланса для газа
        if balance_s_wei <= gas_cost:
            print(f"❌ Недостаточно S для оплаты газа: {balance_s} S, нужно минимум {gas_cost_s} S")
            return None

        # Максимальная сумма для перевода
        transfer_amount = balance_s_wei - gas_cost
        transfer_amount_s = w3_sonic.from_wei(transfer_amount, 'ether')
        if transfer_amount <= 0:
            print(f"❌ Сумма для перевода равна нулю: баланс {balance_s} S, газ {gas_cost_s} S")
            return None
        print(f"ℹ️ Отправляем: {transfer_amount_s} S")

        # Получаем chainId
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
            'gasPrice': gas_price,
            'gas': gas_limit
        }

        # Подписываем и отправляем
        signed_sonic_tx = w3_sonic.eth.account.sign_transaction(sonic_tx, private_key)
        sonic_tx_hash = w3_sonic.eth.send_raw_transaction(signed_sonic_tx.raw_transaction)
        print(f"✅ Перевод S отправлен: {w3_sonic.to_hex(sonic_tx_hash)}")

        # Ждём подтверждения
        sonic_receipt = w3_sonic.eth.wait_for_transaction_receipt(sonic_tx_hash, timeout=120)
        if sonic_receipt.status == 1:
            print(f"✅ Успех! S переведены на {destination_address}")
            print(f"Sonic: https://sonicscan.io/tx/{w3_sonic.to_hex(sonic_tx_hash)}")
            return sonic_tx_hash
        else:
            raise Exception(f"Провал перевода S: https://sonicscan.io/tx/{w3_sonic.to_hex(sonic_tx_hash)}")
    except Exception as e:
        print(f"❌ Ошибка перевода S: {str(e)}")
        return None

# Функция обработки кошельков
def process_wallets(excel_file='wallets.xlsx'):
    try:
        df = pd.read_excel(excel_file)
        print(f"✅ Успешно загружен файл {excel_file}")
    except Exception as e:
        print(f"❌ Ошибка при чтении файла {excel_file}: {str(e)}")
        return

    required_columns = ['PrivateKey', 'Destination']
    if not all(col in df.columns for col in required_columns):
        print(f"❌ В файле {excel_file} отсутствуют необходимые столбцы: {required_columns}")
        return

    for index, row in df.iterrows():
        private_key = str(row['PrivateKey']).strip()
        destination = str(row['Destination']).strip()

        print(f"\n=== Обработка кошелька {index + 1} ===")
        print(f"Приватный ключ: {private_key[:6]}...{private_key[-6:]}")
        print(f"Адрес назначения: {destination}")

        # Проверка приватного ключа
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key
        if not (len(private_key) == 66 and all(c in '0123456789abcdef' for c in private_key[2:])):
            print(f"❌ Неверный формат приватного ключа")
            continue

        # Проверка адреса назначения
        if not w3_sonic.is_address(destination):
            print(f"❌ Некорректный адрес назначения: {destination}")
            continue

        # Выполняем бридж FTM → S
        bridge_tx = bridge_ftm_to_sonic(private_key)
        if not bridge_tx:
            print(f"❌ Бридж не выполнен")
            continue

        # Ждём зачисления S
        print("ℹ️ Ожидаем зачисления S...")
        for attempt in range(3):
            sonic_balance_wei, sonic_balance = check_balance_sonic(private_key)
            if sonic_balance >= 0.0005:
                break
            print(f"ℹ️ Попытка {attempt + 1}/3: S ещё не зачислены, ждём 30 секунд...")
            time.sleep(15)
        else:
            print(f"❌ Недостаточно S: {sonic_balance:.6f} S")
            continue

        # Перевод S
        sonic_tx = transfer_sonic_tokens(private_key, destination)
        if not sonic_tx:
            print(f"⚠️ Перевод S не выполнен")
            continue

    print("\n=== Обработка завершена ===")

if __name__ == "__main__":
    process_wallets('wallets.xlsx')
