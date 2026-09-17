"""Generate deterministic good and bad demo contracts from the PDFs in template/."""
from __future__ import annotations

import argparse
import json
import random
import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from .pdf_renderer import render_contract
from .template_loader import ROOT, catalog, fill_template, inspect_template, load_template

TEMPLATE_DIR = ROOT / "template"
DEFAULT_OUTPUT = ROOT / "data" / "generated_contracts"


@dataclass(frozen=True)
class Profile:
    good: tuple[str, ...]
    bad: tuple[str, ...]
    issues: tuple[str, ...]


PROFILES: dict[str, Profile] = {
    "qard": Profile(
        good=(
            "The Client shall repay only the principal amount. No interest, profit or time-based increase is payable.",
            "A late payment may trigger recovery of documented direct collection costs only; no amount is income to the Institution.",
        ),
        bad=(
            "The Client shall pay interest at 8.5% per annum on the outstanding principal.",
            "Overdue interest compounds monthly and a further 2% monthly late fee is retained as Institution income.",
        ),
        issues=("explicit interest on a loan", "compounding and retained late-payment income"),
    ),
    "murabaha": Profile(
        good=(
            "Before sale to the Client, the Institution purchases, takes title to and bears ownership risk in the identified Goods.",
            "The disclosed cost price and profit produce one fixed Contract Price that cannot increase because of time or default.",
            "Any late-payment undertaking is paid to an independent charity and is not income to the Institution.",
        ),
        bad=(
            "The Institution may sell the Goods before it acquires title or possession and bears no ownership risk at any time.",
            "The profit rate resets quarterly at EIBOR plus 3%, so the Contract Price changes after execution.",
            "A 2% monthly late fee compounds on all overdue sums and is retained as Institution income.",
        ),
        issues=("sale before ownership or possession", "variable and uncertain sale price", "compounding retained late fee"),
    ),
    "musawamah": Profile(
        good=(
            "The Institution owns and bears the risk of the identified Goods before accepting the Client's purchase offer.",
            "The parties agree one fixed Contract Price at acceptance; the Institution is not required to disclose its acquisition cost.",
        ),
        bad=(
            "The Institution is never required to own or possess the Goods before selling them to the Client.",
            "The Institution may change the Contract Price at its sole discretion after the sale, including by reference to market interest rates.",
            "All late fees are retained by the Institution as revenue.",
        ),
        issues=("sale without ownership", "unilateral price uncertainty", "retained late-payment income"),
    ),
    "mudarabah": Profile(
        good=(
            "Profit is distributed only as the stated percentage of actual realized profit, after agreed permissible expenses.",
            "Financial loss is borne by Rab Al-Maal in proportion to invested capital unless caused by proven misconduct, negligence or breach by the Mudarib.",
        ),
        bad=(
            "Rab Al-Maal receives a guaranteed return of 9% of invested capital per annum regardless of actual profit.",
            "The Mudarib guarantees repayment of all capital and bears every commercial loss even without misconduct, negligence or breach.",
        ),
        issues=("fixed guaranteed return", "capital guarantee and improper loss allocation"),
    ),
    "syndication": Profile(
        good=(
            "Profit is shared according to the agreed percentages of actual profit; no party is promised a fixed monetary return.",
            "Investment loss is borne by Rab Al-Maal except to the extent caused by proven misconduct, negligence or breach by the Mudarib.",
        ),
        bad=(
            "Rab Al-Maal is guaranteed principal plus a fixed 10% annual return whether or not the underlying transaction earns profit.",
            "The Mudarib must reimburse all investment losses even when it acted without misconduct, negligence or breach.",
        ),
        issues=("guaranteed principal and return", "improper transfer of investment loss"),
    ),
    "musharakah": Profile(
        good=(
            "Actual profit is distributed by the agreed profit-sharing ratio, while financial loss is allocated in proportion to contributed capital.",
            "No partner guarantees another partner's capital or a fixed return except liability for its own proven misconduct or breach.",
        ),
        bad=(
            "The Institution receives a guaranteed 12% annual return calculated on its capital contribution regardless of actual profit.",
            "The Client guarantees the Institution's capital and bears 100% of all losses even without misconduct or breach.",
        ),
        issues=("guaranteed return on capital", "capital guarantee and loss allocation contrary to contributions"),
    ),
    "salam": Profile(
        good=(
            "The full Salam price is paid to the Supplier at execution of this Agreement.",
            "The goods, grade, quantity, delivery date and delivery place are fixed in the completed schedule and are not left to future agreement.",
        ),
        bad=(
            "Only 10% of the Salam price is paid at execution; the balance is payable after delivery.",
            "The Supplier may choose any grade and quantity of goods, and the delivery date and place will be agreed later.",
        ),
        issues=("Salam price not fully paid at execution", "material uncertainty in goods and delivery"),
    ),
    "istisna": Profile(
        good=(
            "The manufactured asset, specifications, price, milestones and delivery date are fixed in the completed schedules.",
            "Milestone payments reflect manufacturing progress and do not increase merely because time passes.",
        ),
        bad=(
            "The Manufacturer may substitute any materials, quantity or specifications without the Institution's consent.",
            "The unpaid Contract Price increases by 2% per month, compounded monthly, solely because time passes.",
            "The delivery date is optional and may be set by the Manufacturer after execution.",
        ),
        issues=("material uncertainty in specifications", "compounding time-based price increase", "uncertain delivery date"),
    ),
    "ijarah": Profile(
        good=(
            "Rent begins only after the leased asset is delivered and usable by the Lessee.",
            "The Lessor bears ownership-related structural maintenance and ownership risk; the Lessee bears operating misuse and routine operating costs.",
        ),
        bad=(
            "Rent is payable from execution even if the leased asset has not been delivered or cannot be used.",
            "The Lessee bears every ownership risk and all major structural maintenance, even without misuse.",
            "Overdue rent accrues interest at 2% per month, compounded and retained by the Lessor.",
        ),
        issues=("rent before usufruct is available", "owner obligations transferred to lessee", "compounding retained interest"),
    ),
}


COMPANIES = ("Atlas Foods Limited", "Cedar Trading Limited", "Harbor Textiles Limited", "Nour Manufacturing Limited")
SUPPLIERS = ("Green Fields Commodities Limited", "Precision Works Limited", "Crescent Equipment Limited")
INVESTORS = ("Amana Investment Partners", "Safa Pension Trust", "Baraka Capital Partners")
CITIES = ("Karachi", "Lahore", "Islamabad")


def money_words(amount: int) -> str:
    # Demo amounts are intentionally chosen in exact millions.
    return f"{amount // 1_000_000} million Pakistani Rupees"


def values_for(rng: random.Random, key: str, number: int) -> dict[str, str]:
    agreement = date(2026, 9, 17) + timedelta(days=number * 3)
    end = agreement.replace(year=agreement.year + 1)
    principal = rng.choice((5_000_000, 8_000_000, 12_000_000, 20_000_000))
    profit = principal // 10
    sale = principal + profit
    client = rng.choice(COMPANIES)
    supplier = rng.choice(SUPPLIERS)
    investor = rng.choice(INVESTORS)
    institution = "Amanah Islamic Finance Institution"
    city = rng.choice(CITIES)
    goods = {
        "salam": "100 metric tonnes of Grade A milling wheat, crop year 2026",
        "istisna": "one 500 kVA modular solar generation unit",
        "ijarah": "one new CNC machining centre, model PX-500, serial DEMO-500",
    }.get(key, "20 commercial refrigeration units, model CRU-2026")
    result = {
        "city": city, "day": str(agreement.day), "month": agreement.strftime("%B"),
        "month_year": agreement.strftime("%B %Y"), "year": str(agreement.year),
        "date": agreement.isoformat(), "sale_date": agreement.isoformat(),
        "purchase_date": (agreement + timedelta(days=2)).isoformat(),
        "delivery_date": (agreement + timedelta(days=60)).isoformat(),
        "milestone_date1": (agreement + timedelta(days=10)).isoformat(),
        "milestone_date2": (agreement + timedelta(days=30)).isoformat(),
        "milestone_date3": (agreement + timedelta(days=60)).isoformat(),
        "lease_start": (agreement + timedelta(days=7)).isoformat(), "end_date": end.isoformat(),
        "client": client, "client_base": client.removesuffix(" Limited"),
        "client_address": f"18 Demo Commerce Road, {city}",
        "client_contact": f"{client}, 18 Demo Commerce Road, {city}",
        "client_registration": f"DEMO-CLIENT-{number:04d}", "client_signatory": "Ayesha Rahman",
        "company_registration": f"DEMO-REG-{number:04d}",
        "institution": institution, "institution_base": "Amanah Islamic Finance",
        "institution_prefix": "Amanah Islamic", "institution_address": f"1 Finance Avenue, {city}",
        "institution_contact": f"{institution}, 1 Finance Avenue, {city}", "institution_branch": "Demo Main",
        "supplier": supplier, "supplier_address": f"45 Industrial Estate, {city}",
        "supplier_contact": f"{supplier}, 45 Industrial Estate, {city}",
        "supplier_account": f"DEMO-SUP-{number:06d}", "investor": investor,
        "investor_registration": f"DEMO-INV-{number:04d}", "investor_address": f"9 Investor Walk, {city}",
        "principal": f"{principal:,}", "principal_words": money_words(principal),
        "principal_currency": f"PKR {principal:,}", "client_capital": f"{principal:,}",
        "client_capital_words": money_words(principal), "profit": f"{profit:,}",
        "profit_words": money_words(profit), "sale_price": f"{sale:,}",
        "sale_price_words": money_words(sale), "deposit": f"{principal // 10:,}",
        "milestone_amount": f"{principal // 4:,}", "milestone_currency": f"PKR {principal // 4:,}",
        "profit_rate": "10", "client_share": "40", "bank_share": "60", "threshold": f"{principal:,}",
        "threshold_words": money_words(principal), "goods": goods,
        "goods_priced": f"{goods}; quantity: 1; Contract Price: PKR {principal:,}",
        "specifications": "new condition; commercial grade; manufacturer warranty included",
        "quantity_text": "1 unit", "delivery_terms": f"delivered to {city} by {(agreement + timedelta(days=60)).isoformat()}",
        "delivery_address": f"Demo Logistics Centre, {city}",
        "project": "the acquisition and operation of the assets described in the attached synthetic project schedule",
        "collateral": "the synthetic project assets described in Schedule A",
        "security_ref": "Security Schedule A", "security_title": "Security Schedule",
        "accounting_location": "Pakistan", "reference": f"DEMO-{key.upper()}-{number:04d}",
        "witness1": "Omar Siddiqui", "witness2": "Mariam Khan",
        "signature_client": "/s/ Ayesha Rahman", "signature_supplier": "/s/ Bilal Ahmed",
        "signature_bank": "/s/ Farah Malik", "signature_investor": "/s/ Hasan Ali",
        "signature_witness1": "/s/ Omar Siddiqui", "signature_witness2": "/s/ Mariam Khan",
        "witness_id1": f"DEMO-W1-{number:04d}", "witness_id2": f"DEMO-W2-{number:04d}",
        "bank_signatory": "Farah Malik", "parent_name": "Synthetic record", "designation": "Authorized signatory",
        "stamp": "DEMO STAMP", "purchase_address": f"Demo Logistics Centre, {city}",
    }
    return result


def generate(
    *, output_dir: Path, template_dir: Path, keys: list[str], pairs: int, seed: int,
) -> list[dict]:
    rng = random.Random(seed)
    manifest: list[dict] = []
    for key in keys:
        text, definition = load_template(key, template_dir)
        profile = PROFILES[key]
        for number in range(1, pairs + 1):
            values = values_for(rng, key, number)
            completed, audit = fill_template(text, definition, values)
            for variant in ("good", "bad"):
                sample_id = f"{key.upper()}-{number:03d}-{variant.upper()}"
                filename = f"{key}-{number:03d}-{variant}.pdf"
                path = output_dir / variant / filename
                terms = profile.good if variant == "good" else profile.bad
                render_contract(
                    path, title=definition["title"], sample_id=sample_id, variant=variant,
                    source_file=definition["file"], completed_text=completed, demo_terms=list(terms),
                )
                manifest.append({
                    "sample_id": sample_id, "contract_type": key, "variant": variant,
                    "file": str(path.relative_to(output_dir)), "source_template": definition["file"],
                    "expected_seeded_issues": [] if variant == "good" else list(profile.issues),
                    "good_sample_note": "No issue intentionally seeded; qualified review is still required."
                    if variant == "good" else None,
                    "field_count": len(audit), "seed": seed,
                })
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Synthetic contract demo set", "",
        "These contracts were generated from the PDFs in `template/`. They are fictional, for demo and testing only, and are not legal advice or Shariah rulings.", "",
        "Good samples contain no intentionally seeded issue. Bad samples contain explicit seeded issues listed below. Historical source-template wording may still warrant reviewer attention.", "",
        "## Answer key", "",
    ]
    for item in manifest:
        issues = "; ".join(item["expected_seeded_issues"]) or "no issue intentionally seeded"
        lines.append(f"- `{item['file']}`: {issues}.")
    (output_dir / "ANSWER-KEY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--template-dir", type=Path, default=TEMPLATE_DIR)
    parser.add_argument("--types", default="all", help="Comma-separated catalog keys, or all")
    parser.add_argument("--pairs", type=int, default=1, help="Good/bad pairs per contract type")
    parser.add_argument("--seed", type=int, default=20260917)
    parser.add_argument("--list-types", action="store_true")
    parser.add_argument("--inspect-template", type=Path)
    args = parser.parse_args()
    available = list(catalog())
    if args.list_types:
        print("\n".join(available))
        return
    if args.inspect_template:
        print(json.dumps(inspect_template(args.inspect_template), indent=2))
        return
    if args.pairs < 1 or args.pairs > 25:
        parser.error("--pairs must be between 1 and 25")
    keys = available if args.types == "all" else [part.strip() for part in args.types.split(",") if part.strip()]
    unknown = sorted(set(keys) - set(available))
    if unknown:
        parser.error(f"unknown contract type(s): {', '.join(unknown)}")
    manifest = generate(
        output_dir=args.output.resolve(), template_dir=args.template_dir.resolve(),
        keys=keys, pairs=args.pairs, seed=args.seed,
    )
    print(f"Generated {len(manifest)} PDFs in {args.output.resolve()}")


if __name__ == "__main__":
    main()
