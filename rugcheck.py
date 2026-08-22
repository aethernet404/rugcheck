#!/usr/bin/env python3
"""RugCheck — on-chain risk analyzer for Solana meme/pump.fun tokens.

Given a token mint address, pulls core on-chain facts from Solana RPC
(with endpoint rotation + retry) and produces a risk score.

Usage: python3 rugcheck.py <MINT_ADDRESS>
"""
import json
import sys
import time
import urllib.request

RPCS = [
    "https://api.mainnet-beta.solana.com",
    "https://solana-rpc.publicnode.com",
    "https://solana.drpc.org",
    "https://1rpc.io/solana",
    "https://solana.rpc.subquery.network/public",
]

def rpc_call(method, params, max_retries=4):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    for attempt in range(max_retries):
        rpc = RPCS[attempt % len(RPCS)]
        req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=12) as r:
                resp = json.load(r)
                if "error" in resp:
                    raise RuntimeError(f"RPC error: {resp['error']}")
                return resp["result"]
        except Exception as e:
            last_err = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"All RPCs failed: {last_err}")

def analyze(mint):
    print(f"=== RugCheck: {mint} ===")

    supply = rpc_call("getTokenSupply", [mint])
    total = int(supply["value"]["amount"])
    decimals = supply["value"]["decimals"]
    print(f"Total supply: {total / 10**decimals:,.0f}")

    acct = rpc_call("getAccountInfo", [mint, {"encoding": "jsonParsed"}])
    mint_authority = None
    freeze_authority = None
    if acct and acct.get("value"):
        data = acct["value"]["data"]
        if isinstance(data, dict) and data.get("parsed"):
            info = data["parsed"]["info"]
            mint_authority = info.get("mintAuthority")
            freeze_authority = info.get("freezeAuthority")
    print(f"Mint authority: {mint_authority or 'NONE (renounced — good)'}")
    print(f"Freeze authority: {freeze_authority or 'NONE (renounced — good)'}")

    top10_pct = None
    try:
        holders = rpc_call("getTokenLargestAccounts", [mint], max_retries=6)
        top = holders["value"]
        top_amt = sum(int(h["amount"]) for h in top)
        top10_pct = top_amt / total * 100 if total else 0
        print(f"Top {len(top)} holders: {top10_pct:.1f}% of supply")
    except Exception as e:
        print(f"Top holders: UNAVAILABLE (throttled: {str(e)[:60]})")

    price = None
    try:
        req = urllib.request.Request(
            f"https://api.jup.ag/price/v2?ids={mint}",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            pdata = json.load(r).get("data", {}).get(mint)
            if pdata:
                price = float(pdata.get("price"))
                print(f"Price: ${price:.10g}")
    except Exception as e:
        print(f"Price: UNAVAILABLE ({str(e)[:60]})")

    creator = None
    try:
        sigs = rpc_call("getSignaturesForAddress", [mint, {"limit": 1}])
        if sigs:
            creator = sigs[0]["signature"]
    except Exception:
        pass
    print(f"First tx (creator marker): {creator or 'unavailable'}")

    score = 0
    reasons = []
    if mint_authority:
        score += 35
        reasons.append("Mint authority ACTIVE — creator can print unlimited supply")
    if freeze_authority:
        score += 15
        reasons.append("Freeze authority ACTIVE — holder funds can be frozen")
    if top10_pct is not None:
        if top10_pct > 40:
            score += 25
            reasons.append(f"Top-10 concentration {top10_pct:.0f}% — whale dump risk")
        elif top10_pct > 20:
            score += 10
            reasons.append(f"Top-10 concentration {top10_pct:.0f}% — moderately concentrated")
    if total == 0:
        score += 100
        reasons.append("Zero supply — likely dead/broken token")
    score = min(score, 100)

    print("\n=== RISK SCORE: %d/100 ===" % score)
    if score >= 60:
        print("VERDICT: HIGH RISK — treat as potential rug")
    elif score >= 30:
        print("VERDICT: MEDIUM RISK — do your own research")
    else:
        print("VERDICT: LOW RISK — reasonable profile for a memecoin")
    for r in reasons:
        print(f"  - {r}")
    return score

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python3 rugcheck.py <MINT_ADDRESS>")
        sys.exit(1)
    try:
        analyze(sys.argv[1])
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
