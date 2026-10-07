import os, time, random, logging
import requests
from solders.keypair import Keypair

RPC = os.environ.get("SOLANA_RPC", "https://api.mainnet-beta.solana.com")
RESULTS_FILE = "results.csv"
MIN_DELAY, MAX_DELAY = 2, 10
ERR_BASE, ERR_MAX = 5, 300   # пауза після помилки: 5 с → до 5 хв

log = logging.getLogger("scanner")
session = requests.Session()


def get_lamports(addr):
    r = session.post(RPC, json={
        "jsonrpc": "2.0", "id": 1,
        "method": "getBalance", "params": [addr]}, timeout=15)
    r.raise_for_status()                      # 429 теж тут стане винятком
    data = r.json()
    if "error" in data:
        raise RuntimeError(data["error"])
    return data["result"]["value"]


def persist_hit(kp, addr, lamports):
    fd = os.open(RESULTS_FILE, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "a") as f:
        f.write(f"{addr};{kp};{lamports}\n")


def cycle():
    """True, якщо перевірка пройшла; False, якщо RPC дав помилку."""
    kp = Keypair()
    addr = str(kp.pubkey())
    try:
        lamports = get_lamports(addr)
    except Exception as e:
        log.warning("Помилка RPC: %s", e)
        return False
    if lamports > 0:
        persist_hit(kp, addr, lamports)
        log.info("Знайдено баланс: %s", addr)
    return True


def main():
    logging.basicConfig(level=logging.INFO)
    n, fails = 0, 0
    try:
        while True:
            n += 1
            if cycle():
                fails = 0
                delay = random.uniform(MIN_DELAY, MAX_DELAY)
            else:
                fails += 1
                delay = min(ERR_BASE * 2 ** (fails - 1), ERR_MAX)
                delay += random.uniform(0, 1)     # jitter
                log.info("Підряд помилок: %d, пауза %.1f с", fails, delay)
            time.sleep(delay)
    except KeyboardInterrupt:
        log.info("Зупинено. Циклів: %d", n)


if __name__ == "__main__":
    main()
