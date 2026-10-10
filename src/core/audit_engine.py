"""Qurilish materiallari va byudjet mablag'lari auditi tahlil dvigateli."""
from src.core.market_benchmarks import MARKET_RATES, ENGINEERING_NORMS

class AuditEngine:
    @staticmethod
    def audit_entry(category: str, quantity: float, unit_price: float, total_cost: float, building_sqm: float = 0.0) -> dict:
        """Kiritilgan smeta ma'lumotlarini bozor va me'yorlar bilan tekshirish."""
        findings = []
        is_red = False
        is_yellow = False
        damage_amount = 0.0

        benchmark = MARKET_RATES.get(category, {})
        market_price = benchmark.get("market_price", unit_price)
        max_allowed_price = benchmark.get("max_allowed", unit_price * 1.1)

        # ---------------- 1. NARX AUDITI (Price Gouging Check) ----------------
        price_diff_pct = 0.0
        if market_price > 0:
            price_diff_pct = ((unit_price - market_price) / market_price) * 100.0

        if unit_price > max_allowed_price:
            overpay_per_unit = unit_price - market_price
            price_damage = max(0.0, overpay_per_unit * quantity)
            damage_amount += price_damage

            if price_diff_pct > 30.0:
                is_red = True
                findings.append(f"QALLOBLIK XAVFI: Birlik narxi bozor narxidan {price_diff_pct:+.1f}% qimmat! ({unit_price:,.0f} vs {market_price:,.0f} UZS)")
            else:
                is_yellow = True
                findings.append(f"NARX OSHIRILGAN: Birlik narxi ruxsat etilgan chegaradan {price_diff_pct:+.1f}% baland.")
        elif unit_price < benchmark.get("min_allowed", 0.0):
            is_yellow = True
            findings.append(f"SIFATSIZLIK XAVFI: Narx bozor minimumidan ancha past ({price_diff_pct:+.1f}%). Kontrafakt bo'lishi mumkin.")
        else:
            findings.append(f"Narx me'yorda: Bozor etaloniga mos ({market_price:,.0f} UZS/birlik).")

        # ---------------- 2. HAJM AUDITI (Volume Inflation Check) ----------------
        norm_info = ENGINEERING_NORMS.get(category)
        theoretical_qty = 0.0

        if norm_info and building_sqm > 0:
            norm_factor = norm_info["norm_per_building_sqm"]
            tol_pct = norm_info["tolerance_pct"]
            theoretical_qty = building_sqm * norm_factor
            max_permitted_qty = theoretical_qty * (1.0 + (tol_pct / 100.0))

            if quantity > max_permitted_qty:
                excess_qty = quantity - theoretical_qty
                volume_damage = excess_qty * market_price
                damage_amount += volume_damage
                is_red = True
                findings.append(
                    f"HAJMNI SOXTALASHTIRISH: Bino maydoni ({building_sqm:g} m²) uchun me'yor {theoretical_qty:,.0f}, ammo kiritilgan hajm {quantity:,.0f}! Ortiqcha: +{excess_qty:,.0f}"
                )
            else:
                findings.append(f"Material hajmi ShNQ me'yorlariga to'g'ri keladi (Maksimum ruxsat: {max_permitted_qty:,.0f}).")

        # ---------------- 3. YAKUNIY STATUS VA XULOSA ----------------
        if is_red:
            final_status = "Qizil"
            verdict_text = "BYUDJET O'G'IRLIGI / MAQSADSIZ SARF ANIQLANDI"
        elif is_yellow:
            final_status = "Sariq"
            verdict_text = "SHUBHALI XARAJAT / QAYTA AUDIT TALAB ETILADI"
        else:
            final_status = "Yashil"
            verdict_text = "MABLAG'LAR ME'YORIDA VA MAQSADLI SARFLANGAN"

        return {
            "status": final_status,
            "verdict": verdict_text,
            "findings": findings,
            "market_price": market_price,
            "price_diff_pct": price_diff_pct,
            "damage_amount": damage_amount,
            "theoretical_qty": theoretical_qty,
            "source": benchmark.get("source", "Bozor tahlili")
        }