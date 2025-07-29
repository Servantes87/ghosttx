import requests
from datetime import datetime

ETHERSCAN_API = "https://api.etherscan.io/api"

class GhostTxScanner:
    def __init__(self, address, api_key):
        self.address = address.lower()
        self.api_key = api_key
        self.tx_list = []

    def fetch_transactions(self):
        print("[*] Загружаем транзакции...")
        url = (
            f"{ETHERSCAN_API}?module=account&action=txlist"
            f"&address={self.address}&startblock=0&endblock=99999999"
            f"&sort=asc&apikey={self.api_key}"
        )
        response = requests.get(url)
        data = response.json()
        if data['status'] != '1':
            raise Exception("Ошибка при загрузке данных")
        self.tx_list = data['result']

    def detect_ghost_transactions(self):
        ghost_txs = []

        for tx in self.tx_list:
            is_contract_call = tx.get('input') and tx['input'] != '0x'
            has_token_value = int(tx['value']) > 0

            if is_contract_call and not has_token_value:
                ghost_txs.append({
                    "hash": tx['hash'],
                    "to": tx['to'],
                    "method": tx['input'][:10],
                    "timestamp": datetime.utcfromtimestamp(int(tx['timeStamp'])).isoformat()
                })

        return ghost_txs

    def run(self):
        self.fetch_transactions()
        ghosts = self.detect_ghost_transactions()

        if not ghosts:
            print("✅ Призрачных транзакций не обнаружено.")
        else:
            print(f"\n👻 Найдено {len(ghosts)} подозрительных (невидимых) контрактных вызовов:\n")
            for tx in ghosts:
                print(f"⏱ {tx['timestamp']} | to: {tx['to']} | method ID: {tx['method']} | tx: {tx['hash'][:10]}...")
