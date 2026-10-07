Додав запис у `results.csv` для гаманців із балансом більше 0. Записую лише адресу та баланс, без приватного ключа: він і так зберігається в `keys.csv`, а дублювати секрети в другому файлі небезпечно.

```python
# pip install solders requests
import os, time, requests
from solders.keypair import Keypair

KEYS_FILE = "keys.csv"
RESULTS_FILE = "results.csv"
RPC = "https://api.mainnet-beta.solana.com"

def new_wallet():
    kp = Keypair()
    addr, priv = str(kp.pubkey()), str(kp)
    fd = os.open(KEYS_FILE, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "a") as f:
        f.write(f"{addr};{priv}\n")
    return addr

def balance_sol(addr):
    r = requests.post(RPC, json={
        "jsonrpc": "2.0", "id": 1,
        "method": "getBalance", "params": [addr]}, timeout=15)
    r.raise_for_status()
    return r.json()["result"]["value"] / 1e9

def save_result(addr, bal):
    with open(RESULTS_FILE, "a") as out:
        out.write(f"{addr};{bal}\n")

def check_wallets():
    if not os.path.exists(KEYS_FILE):
        print("Файлу keys.csv ще немає")
        return
    with open(KEYS_FILE) as f:
        lines = [l.strip() for l in f if l.strip()]
    for line in lines:
        addr = line.split(";")[0]
        try:
            bal = balance_sol(addr)
            print(addr, bal, "SOL")
            if bal > 0:
                save_result(addr, bal)
        except Exception as e:
            print("Помилка для", addr, "-", e)
        time.sleep(0.5)

if __name__ == "__main__":
    print("Новий гаманець:", new_wallet())
    check_wallets()
```

Зверніть увагу: при кожному запуску скрипт перевіряє всі гаманці з `keys.csv` наново, тож гаманець із коштами потрапить у `results.csv` повторно. Якщо потрібно записувати кожну адресу лише раз, можу додати перевірку на дублікати.