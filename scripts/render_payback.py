"""Генерация графика окупаемости ИС «Караваны» для BusinessCase.md.

Источник цифр:
  - BusinessCase.md, разделы 5.1, 5.2, 5.3, 5.4
  - SDP.md, разделы 4.2.4, 4.2.6

Запуск:
  python scripts/render_payback.py
Результат:
  diagrams/out/Payback.png
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

# --- Параметры проекта (синхронизированы с SDP/BusinessCase) ---

# Фазы RUP по месяцам от старта проекта (M0 = 23.03.2026)
PHASES = [
    # (имя, начало месяца, конец месяца, стоимость крышек, цвет фона)
    ("Inception",    0,  2,  3_032,  "#E3F2FD"),
    ("Elaboration",  2,  4,  8_076,  "#FFF9C4"),
    ("Construction", 4, 11, 51_624,  "#FFE0B2"),
    ("Transition",  11, 12,  5_648,  "#C8E6C9"),
]
INFRA_COST = 5_500   # размазывается по Construction
PILOT_COST = 3_000   # в Transition
RELEASE_MONTH = 12   # M12 — релиз 1.0 (31.12.2026)
OPS_COST_MO = 10_000 # после релиза

# MRR — ключевые точки прогноза (см. BusinessCase 5.4)
MRR_POINTS = [
    (0, 0),
    (1, 2_200),
    (3, 4_400),
    (6, 11_400),
    (12, 20_400),
    (18, 29_400),
    (24, 38_400),
]


def cumulative_cost(m: float) -> float:
    """Совокупные затраты к концу месяца m от старта проекта."""
    total = 0.0
    for name, start, end, cost, _ in PHASES:
        if m >= end:
            total += cost
            if name == "Construction":
                total += INFRA_COST
            if name == "Transition":
                total += PILOT_COST
        elif m > start:
            frac = (m - start) / (end - start)
            total += cost * frac
            if name == "Construction":
                total += INFRA_COST * frac
            if name == "Transition":
                total += PILOT_COST * frac
    if m > RELEASE_MONTH:
        total += OPS_COST_MO * (m - RELEASE_MONTH)
    return total


def mrr_at(rel_month: float) -> float:
    """MRR на месяце rel_month после релиза (линейная интерполяция)."""
    pts = MRR_POINTS
    if rel_month <= pts[0][0]:
        return pts[0][1]
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        if x0 <= rel_month <= x1:
            return y0 + (y1 - y0) * (rel_month - x0) / (x1 - x0)
    last_x, last_y = pts[-1]
    return last_y + 1_500 * (rel_month - last_x)


def cumulative_revenue(m: int) -> float:
    """Совокупная выручка к концу месяца m от старта проекта."""
    if m <= RELEASE_MONTH:
        return 0.0
    total = 0.0
    for r in range(1, m - RELEASE_MONTH + 1):
        total += mrr_at(r)
    return total


def main() -> None:
    months = np.arange(0, 41)
    costs = [cumulative_cost(m) for m in months]
    revenues = [cumulative_revenue(m) for m in months]

    # Точка окупаемости — пересечение кривых выручки и затрат
    crossing_m = None
    for i in range(len(months) - 1):
        if revenues[i] < costs[i] and revenues[i + 1] >= costs[i + 1]:
            crossing_m = int(months[i + 1])
            break

    fig, ax = plt.subplots(figsize=(13, 6.5))

    # Фоновые регионы RUP-фаз
    for name, start, end, _, color in PHASES:
        ax.axvspan(start, end, alpha=0.55, color=color)
        ax.text(
            (start + end) / 2,
            ax.get_ylim()[1] if False else 0,
            name,
            ha="center", va="bottom", fontsize=9, color="#444",
            transform=ax.get_xaxis_transform(),
        )
    # Эксплуатация
    ax.axvspan(RELEASE_MONTH, 40, alpha=0.35, color="#ECEFF1")
    ax.text(
        (RELEASE_MONTH + 40) / 2, 0,
        "Эксплуатация (post-release)",
        ha="center", va="bottom", fontsize=9, color="#444",
        transform=ax.get_xaxis_transform(),
    )

    # Кривые
    ax.plot(months, costs, color="#C62828", linewidth=2.5, label="Совокупные затраты")
    ax.plot(months, revenues, color="#2E7D32", linewidth=2.5, label="Совокупная выручка")

    # Маркер релиза
    ax.axvline(x=RELEASE_MONTH, color="black", linestyle="--", alpha=0.6)
    ax.text(
        RELEASE_MONTH + 0.2, max(costs) * 0.92,
        "Релиз 1.0\n31.12.2026",
        fontsize=9, color="black",
    )

    # Точка окупаемости
    if crossing_m is not None:
        cross_val = costs[crossing_m]
        ax.scatter(
            [crossing_m], [cross_val],
            color="gold", s=200, zorder=5,
            edgecolors="black", linewidth=1.5,
        )
        ax.annotate(
            f"Точка окупаемости\n≈M{crossing_m} (+{crossing_m - RELEASE_MONTH} мес. после релиза)\n≈{cross_val:,.0f} крышек".replace(",", " "),
            xy=(crossing_m, cross_val),
            xytext=(crossing_m - 12, cross_val + 60_000),
            fontsize=10, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="black", lw=1.2),
            bbox=dict(boxstyle="round,pad=0.4", fc="#FFFDE7", ec="black", lw=0.8),
        )

    # Оси
    ax.set_xlabel(
        "Месяцы от старта проекта (M0 = 23.03.2026)",
        fontsize=11,
    )
    ax.set_ylabel("Совокупная сумма, крышек", fontsize=11)
    ax.set_title(
        "График окупаемости проекта ИС «Караваны»",
        fontsize=13, fontweight="bold", pad=12,
    )
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 40)
    ax.set_ylim(0, max(max(costs), max(revenues)) * 1.15)

    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda x, _: f"{int(x):,}".replace(",", " "))
    )

    ax.legend(loc="upper left", fontsize=10, framealpha=0.95)

    out_dir = Path("diagrams/out")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "Payback.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=120, bbox_inches="tight")
    print(f"Saved {out_path} (точка окупаемости: M{crossing_m})")


if __name__ == "__main__":
    main()
