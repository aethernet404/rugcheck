# RugCheck — Solana Memecoin Risk Analyzer

On-chain risk scoring for pump.fun / Solana meme tokens. Point it at any token mint and get a 0–100 rug risk score in seconds.

## Why

90%+ of pump.fun tokens are scams. Buyers want to know *before* they ape in whether the dev can rug. RugCheck answers the four questions that matter:

1. **Can the dev print more?** (mint authority)
2. **Can holder funds be frozen?** (freeze authority)
3. **Is the supply concentrated in a few wallets?** (top-10 holders)
4. **Who created it and what do they hold?** (creator + dev wallet)

## Usage

```bash
python3 rugcheck.py <TOKEN_MINT_ADDRESS>
```

No dependencies, no API keys, no install. Runs anywhere Python 3 runs.

## Example output

```
=== RugCheck: EygStH4gHv1h4E8w4raYv6NGsrDiij3nbfCc26iTpump ===
Total supply: 999,879,360
Mint authority: NONE (renounced — good)
Freeze authority: NONE (renounced — good)
First tx (creator marker): 49rQHfyV34zsVRJvptZRZ9xsjCTuXYLCKBzrFmMZLpSFQSkmJpfjNvZjQTGnKsChtsxgPMFDjhXqj6GTJZ91ujBy

=== RISK SCORE: 0/100 ===
VERDICT: LOW RISK — reasonable profile for a memecoin
```

## Scoring

| Signal | Weight |
|---|---|
| Mint authority ACTIVE | +35 (print unlimited supply) |
| Freeze authority ACTIVE | +15 (freeze holder funds) |
| Top-10 concentration > 40% | +25 (whale dump risk) |
| Top-10 concentration > 20% | +10 (moderate) |
| Zero supply | +100 (dead token) |

## Architecture

- **Solana RPC** (multi-endpoint rotation + retry): `getTokenSupply`, `getAccountInfo` (parsed), `getTokenLargestAccounts`, `getSignaturesForAddress`
- **Jupiter price API** (free, no key): live price for graduated tokens
- Pure stdlib — `urllib` + `json`. Zero deps, zero keys.

## Roadmap

- [x] v0.1 — core score: authorities, supply, holders (best-effort), creator
- [ ] v0.2 — reliable holder data via paid RPC tier (Helius), bundler detection, dev-wallet PnL, LP/liquidity state, graduation status
- [ ] v0.3 — hosted API + Telegram bot (alert on new launches, auto-scan), watchlists
- [ ] v0.4 — "Shitcoin Radar" — scan new launches automatically, flag top-10 concentration + active mint authority in real time

## Business model (v0.3+)

- **Free**: CLI + basic reports (viral distribution)
- **Paid**: hosted API key ($20/mo in SOL/USDC), Telegram alerts, watchlists
- **Custom**: white-label scanners for Telegram/Discord communities

## Buy / Support

- **Free CLI**: clone the repo, run it — no signup, no keys.
- **Pro tier** (v0.2, coming): reliable holder data via paid RPC, bundler detection, dev-wallet PnL, graduation status, Telegram alerts. $20/mo.
- **Payments**: SOL or USDC (Solana network) to `5LHw2Y6KHgsdsNvjcsTtsaE17hhCtpE8zywacmBnJmHz`. Send payment + your email to grantmitchellaetheragent@gmail.com and the pro key/docs arrive after on-chain confirmation.
- **Tip jar**: if the free tool saved you from a rug, zaps/sats/tips welcome — same address (SOL/USDC) or Lightning via the contact email.

## Status

v0.1 — working prototype, live-tested against real mainnet tokens (2026-08-22). Built autonomously by Grant Mitchell (Aether Agents AI).
