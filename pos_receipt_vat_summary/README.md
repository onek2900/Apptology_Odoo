# POS Receipt VAT Summary (Odoo 17) — v4.6

**Fix:** VAT line could wrap onto two lines on narrow layouts.  
This version forces the VAT row to a **single line** using flex + nowrap while keeping:
- Label on the **left**, amount on the **right**.
- Insert position: **immediately under the last TOTAL** row.
- Bilingual label: `VAT (15%): / ضريبة القيمة المضافة (15%)`.
- Default tax table removed; 15% is display-only.

Install / Upgrade:
1. Extract into addons path as `pos_receipt_vat_summary`.
2. Restart Odoo and upgrade the module: `./odoo-bin -d <DB> -u pos_receipt_vat_summary`.
3. Developer Mode → Technical → **Frontend Assets** → **Clear Assets**.
4. Reload POS with `?debug=assets` and hard refresh (unregister service worker if active).