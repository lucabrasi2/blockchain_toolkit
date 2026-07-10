from ethereum.tokens import (
    get_token_balance,
    USDT_CONTRACT,
)

wallet = input("Ethereum Address: ").strip()

result = get_token_balance(
    wallet,
    USDT_CONTRACT,
)

print("\n========== TOKEN REPORT ==========")
print(f"Token   : {result['symbol']}")
print(f"Balance : {result['balance']}")