# pip install solders
import os
from solders.keypair import Keypair

print("Генерую нову пару ключів...")
kp = Keypair()

address = str(kp.pubkey())   # публічна адреса
private_key = str(kp)        # приватний ключ у base58 (64 байти)

print("Адреса гаманця:", address)

print("Зберігаю у key.csv...")
fd = os.open("key.csv", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, "w") as f:
    f.write(f"{address};{private_key}\n")

print("Готово. Приватний ключ у key.csv")


# pip install solders requests
import requests, time
from solders.keypair import Keypair

RPC = "https://api.mainnet-beta.solana.com"

def balance_sol(addr):
    r = requests.post(RPC, json={
        "jsonrpc": "2.0", "id": 1,
        "method": "getBalance", "params": [addr]}, timeout=15)
    return r.json()["result"]["value"] / 1e9

with open("keys.csv") as f:
    keys = [l.strip() for l in f if l.strip()]

left = list(keys)
for key in keys:
    try:
        addr = str(Keypair.from_base58_string(key).pubkey())
        bal = balance_sol(addr)
    except Exception as e:
        print("Помилка, пропускаю:", e)
        continue
    if bal > 0:
        with open("results.csv", "a") as out:
            out.write(f"{addr};{key};{bal}\n")
    left.remove(key)
    with open("keys.csv", "w") as f:
        f.write("\n".join(left) + ("\n" if left else ""))
    time.sleep(0.2)  # ліміти публічного RPC







