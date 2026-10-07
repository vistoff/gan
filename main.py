# pip install solders requests
import os, time, random, requests
from solders.keypair import Keypair

KEYS_FILE = "keys.csv"
RESULTS_FILE = "results.csv"
RPC = "https://api.mainnet-beta.solana.com"

MIN_DELAY = 2    # мінімальна пауза, с
MAX_DELAY = 10   # максимальна пауза, с

def new_wallet():
    kp = Keypair()
    addr, priv = str(kp.pubkey()), str(kp)
    fd = os.open(KEYS_FILE, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "a") as f:
        f.write(f"{addr};{priv}\n")
    return addr, priv          # тепер повертає й ключ


def balance_sol(addr):
    r = requests.post(RPC, json={
        "jsonrpc": "2.0", "id": 1,
        "method": "getBalance", "params": [addr]}, timeout=15)
    r.raise_for_status()
    return r.json()["result"]["value"] / 1e9

def save_result(addr, priv, bal):
    fd = os.open(RESULTS_FILE, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "a") as out:
        out.write(f"{addr};{priv};{bal}\n")

def countdown(seconds):
    end = time.time() + seconds
    while True:
        left = end - time.time()
        if left <= 0:
            break
        print(f"\rНаступний цикл через {left:4.1f} с ", end="", flush=True)
        time.sleep(0.1)
    print("\r" + " " * 40 + "\r", end="", flush=True)

def cycle():
    addr, priv = new_wallet()
    print("Новий гаманець:", addr)
    try:
        bal = balance_sol(addr)
        print("Баланс:", bal, "SOL")
        if bal > 0:
            save_result(addr, priv, bal)
            print("Записано в results.csv")
    except Exception as e:
        print("Помилка перевірки:", e)

if __name__ == "__main__":
    n = 0
    try:
        while True:
            n += 1
            print(f"--- Цикл {n} ---")
            cycle()
            countdown(random.uniform(MIN_DELAY, MAX_DELAY))
    except KeyboardInterrupt:
        print(f"\nЗупинено. Циклів виконано: {n}")