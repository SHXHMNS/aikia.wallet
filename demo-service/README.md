# AIKIA.WALLET buyer demo

Self-contained, browser-only sales prototype with fictional sample data. No account, wallet issuer or package install is required.

## Run locally

From the repository root:

```sh
python3 -m http.server 4173 --directory demo-service
```

Open `http://localhost:4173`. A copy is also served inside the Next.js workspace at `/demo/index.html`.

## Demo flow

- Switch between the **Owner dashboard** and the restricted-layout **Staff dashboard**.
- As the owner, edit venue identity and card art/color, set the qualifying action and reward target, and configure the Ink / Chrome / Pink lifetime tiers and benefits.
- As staff, find a fictional member by code or QR camera scan, record a qualifying action, and redeem an available reward.
- Join as a fictional guest and inspect the member card preview.
- Reset browser data to restore the sample account.

## Limits

The demo stores sample records in this browser's `localStorage`. It has no server, production authentication, tenant isolation, real pass issuance, notification delivery or reward entitlement. The role switch is a presentation aid, not access control. Use fictional data only.

The active development workspace is [`../software/`](../software/README.md): Next.js, Supabase and Google Wallet first, with a provider boundary for planned Apple Wallet support. Do not use browser storage as the production data layer.
