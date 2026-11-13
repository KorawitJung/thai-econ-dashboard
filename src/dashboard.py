"""Build the Thai economy dashboard PDF (+ PNG previews for GitHub).

Usage:
    python src/dashboard.py            # real data if BOT_API_TOKEN is set, else sample
    python src/dashboard.py --sample   # always use sample data
"""
from __future__ import annotations

import argparse
import sys
import textwrap
from datetime import date, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

sys.path.insert(0, str(Path(__file__).parent))
import bot_api  # noqa: E402
import sample_data  # noqa: E402
from theme import AMBER, BG, BLUE, GREEN, INK, MUTED, NAVY, RED, SAMPLE, card  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
DATA = ROOT / "data"
DISCLAIMER = ("For educational purposes only. Not for commercial use. Not investment advice. "
              "Data: Bank of Thailand API (bot.or.th).")
PAGE = (11.69, 8.27)  # A4 landscape
L, R = 0.045, 0.955   # page margins


# ----------------------------------------------------------------- data
def load(sample: bool, years: int = 3):
    end = date.today()
    start = end - timedelta(days=365 * years)
    if not sample:
        try:
            fx = bot_api.exchange_rate(max(start, end - timedelta(days=365)), end)
            infl = bot_api.inflation(start, end)
            pr = bot_api.policy_rate()
            pr = pr[pr["date"] >= pd.Timestamp(start) - pd.Timedelta(days=730)]
            return fx, infl, pr, "Bank of Thailand API"
        except Exception as e:  # noqa: BLE001
            print(f"[warn] BOT API unavailable ({e}); falling back to SAMPLE data", file=sys.stderr)
    fx, infl, pr = sample_data.make(start, end)
    return fx, infl, pr, "SAMPLE DATA (synthetic, not official)"


# ----------------------------------------------------------- components
def header(fig, title, subtitle, source, page, pages):
    fig.patch.set_facecolor(BG)
    fig.patches.append(plt.Rectangle((0, 0.885), 1, 0.115, transform=fig.transFigure, color=NAVY, zorder=0))
    fig.text(L, 0.945, title, color="white", fontsize=19, weight="bold", va="center")
    fig.text(L, 0.905, subtitle, color="#b8c7da", fontsize=9.5, va="center")
    is_sample = "SAMPLE" in source
    fig.text(R, 0.945, f"Updated {date.today():%d %b %Y}", color="white", fontsize=9.5, ha="right", va="center")
    fig.text(R, 0.905, "●  " + source, ha="right", va="center", fontsize=8.5,
             color="#ffb27a" if is_sample else "#86e0b3")
    fig.patches.append(plt.Rectangle((0, 0), 1, 0.045, transform=fig.transFigure, color="white", zorder=0))
    fig.text(L, 0.0225, DISCLAIMER, fontsize=7.5, color=MUTED, va="center", style="italic")
    fig.text(R, 0.0225, f"{page} / {pages}", fontsize=8, color=MUTED, va="center", ha="right")
    if is_sample:
        fig.text(0.5, 0.47, "SAMPLE DATA", fontsize=80, color=SAMPLE, alpha=0.05, ha="center",
                 va="center", rotation=18, weight="bold", zorder=100)


def kpi(fig, x, y, w, h, label, value, delta, delta_good, note, series, color):
    card(fig, x, y, w, h, accent=color)
    fig.text(x + 0.018, y + h - 0.035, label.upper(), fontsize=7.5, color=MUTED, weight="bold")
    fig.text(x + 0.018, y + h - 0.095, value, fontsize=24, color=INK, weight="bold")
    fig.text(x + 0.018, y + 0.028, delta, fontsize=7.5, color=GREEN if delta_good else RED, weight="bold",
             bbox=dict(boxstyle="round,pad=0.35,rounding_size=0.6",
                       fc="#e7f6ee" if delta_good else "#fdecec", ec="none"))
    fig.text(x + w - 0.015, y + 0.028, note, fontsize=7.5, color=MUTED, ha="right")
    sp = fig.add_axes([x + w * 0.6, y + h * 0.45, w * 0.35, h * 0.33])
    v = series.to_numpy(dtype=float)
    sp.plot(v, color=color, lw=1.4)
    sp.fill_between(range(len(v)), v, v.min(), color=color, alpha=0.12)
    sp.plot(len(v) - 1, v[-1], "o", color=color, ms=3.5)
    sp.axis("off")
    sp.set_zorder(5)


def chart_card(fig, x, y, w, h, title, subtitle=""):
    card(fig, x, y, w, h)
    fig.text(x + 0.018, y + h - 0.035, title, fontsize=10.5, color=INK, weight="bold")
    if subtitle:
        fig.text(x + 0.018, y + h - 0.06, subtitle, fontsize=7.5, color=MUTED)
    ax = fig.add_axes([x + 0.04, y + 0.045, w - 0.06, h - 0.125])
    ax.set_facecolor("white")
    ax.set_zorder(5)
    ax.tick_params(length=0)
    return ax


def date_axis(ax, yearly=False):
    if yearly:
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    else:
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 7)))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))


def policy_on(dates, pr):
    s = pr.set_index("date")["policy_rate"]
    return s.reindex(s.index.union(dates)).ffill().reindex(dates)


# ---------------------------------------------------------------- pages
def page_overview(fx, infl, pr, source):
    fig = plt.figure(figsize=PAGE)
    header(fig, "Thailand Macro Dashboard",
           "Thai baht  ·  Inflation  ·  Monetary policy", source, 1, 2)

    fxs, cpi, rate = fx.set_index("date")["usd_thb"], infl.set_index("date")["cpi_yoy"], pr["policy_rate"]
    chg = fxs.iloc[-1] - fxs.iloc[max(0, len(fxs) - 22)]
    real_series = policy_on(cpi.index, pr) - cpi
    real = real_series.iloc[-1]
    in_band = 1 <= cpi.iloc[-1] <= 3
    rate_chg = rate.iloc[-1] - rate.iloc[-2] if len(rate) > 1 else 0

    gap, top, h = 0.0125, 0.71, 0.15
    w = (R - L - 3 * gap) / 4
    xs = [L + i * (w + gap) for i in range(4)]
    kpi(fig, xs[0], top, w, h, "USD/THB mid rate", f"{fxs.iloc[-1]:.2f}",
        f"{'▲' if chg > 0 else '▼'} {abs(chg):.2f} vs 1M", chg < 0,
        "baht " + ("weaker" if chg > 0 else "stronger"), fxs.tail(66), BLUE)
    kpi(fig, xs[1], top, w, h, "Headline CPI, YoY", f"{cpi.iloc[-1]:.2f}%",
        "Within 1–3% target" if in_band else "Outside 1–3% target", in_band,
        f"{cpi.index[-1]:%b %Y}", cpi.tail(12), AMBER)
    kpi(fig, xs[2], top, w, h, "BOT policy rate", f"{rate.iloc[-1]:.2f}%",
        (f"{'▲' if rate_chg > 0 else '▼'} {abs(rate_chg) * 100:.0f} bp last move") if rate_chg else "Unchanged",
        rate_chg <= 0, f"since {pr['date'].iloc[-1]:%b %Y}", pd.concat([rate, rate.tail(1)]), GREEN)
    kpi(fig, xs[3], top, w, h, "Real policy rate", f"{real:+.2f}%",
        "Restrictive" if real > 1 else ("Accommodative" if real < 0 else "Neutral"), real <= 1,
        "policy − CPI", real_series.tail(12), NAVY)

    big_w = 0.6
    x2 = L + big_w + gap
    # FX trend
    ax = chart_card(fig, L, 0.385, big_w, 0.305, "USD/THB exchange rate",
                    "THB per 1 USD  ·  higher = weaker baht")
    ax.plot(fxs.index, fxs.values, color=BLUE, lw=1.3, label="Daily mid rate")
    ax.plot(fxs.index, fxs.rolling(20).mean(), color=INK, lw=0.9, ls=(0, (3, 2)), label="20-day average")
    ax.fill_between(fxs.index, fxs.values, fxs.min() - 0.4, color=BLUE, alpha=0.06)
    for d, up, lab in ((fxs.idxmax(), True, "High"), (fxs.idxmin(), False, "Low")):
        ax.annotate(f"{lab} {fxs[d]:.2f}", (d, fxs[d]), xytext=(0, 6 if up else -6), textcoords="offset points",
                    ha="center", va="bottom" if up else "top", fontsize=7.5, color=INK, weight="bold")
    ax.set_ylim(fxs.min() - 0.4, fxs.max() + 0.6)
    ax.set_xlim(fxs.index[0], fxs.index[-1])
    ax.legend(loc="upper right", ncol=2)
    date_axis(ax)

    # Volatility
    ax = chart_card(fig, x2, 0.385, R - x2, 0.305, "Daily moves", "distribution of daily % change")
    ret = fxs.pct_change().dropna() * 100
    ax.hist(ret, bins=26, color=BLUE, alpha=0.8, edgecolor="white", linewidth=0.6)
    ax.axvline(0, color=INK, lw=0.7)
    ax.text(0.98, 0.95, f"Annualised vol\n{ret.std() * 252 ** 0.5:.1f}%", transform=ax.transAxes,
            ha="right", va="top", fontsize=8.5, color=INK, weight="bold")

    # Inflation vs policy
    ax = chart_card(fig, L, 0.07, big_w, 0.295, "Inflation vs policy rate", "% · bars = headline CPI YoY")
    ax.axhspan(1, 3, color=AMBER, alpha=0.1, lw=0)
    ax.text(cpi.index[0], 2.92, "  BOT target band 1–3%", fontsize=7.5, color=AMBER, va="top", weight="bold")
    ax.bar(cpi.index, cpi.values, width=22, color=[AMBER if v >= 0 else RED for v in cpi.values],
           label="Headline CPI YoY")
    step = pd.concat([pr.set_index("date")["policy_rate"], pd.Series([rate.iloc[-1]], index=[cpi.index[-1]])])
    ax.step(step.index, step.values, where="post", color=GREEN, lw=2.2, label="Policy rate")
    ax.axhline(0, color=INK, lw=0.6)
    ax.set_xlim(cpi.index[0] - pd.Timedelta(days=20), cpi.index[-1] + pd.Timedelta(days=20))
    ax.set_ylim(min(-0.5, cpi.min() - 0.3), max(3.4, cpi.max() + 0.5))
    ax.legend(loc="upper right", ncol=2)
    date_axis(ax)

    # Real rate
    ax = chart_card(fig, x2, 0.07, R - x2, 0.295, "Real policy rate", "% · policy rate − CPI")
    ax.fill_between(real_series.index, real_series, 0, where=real_series >= 0, color=GREEN, alpha=0.3,
                    interpolate=True)
    ax.fill_between(real_series.index, real_series, 0, where=real_series < 0, color=RED, alpha=0.3,
                    interpolate=True)
    ax.plot(real_series.index, real_series, color=INK, lw=0.9)
    ax.axhline(0, color=INK, lw=0.6)
    date_axis(ax, yearly=True)
    return fig


def page_insights(fx, infl, pr, source):
    fig = plt.figure(figsize=PAGE)
    header(fig, "Key Takeaways & Data Notes", "Auto-generated summary of the latest readings", source, 2, 2)
    fxs, cpi, rate = fx.set_index("date")["usd_thb"], infl.set_index("date")["cpi_yoy"], pr["policy_rate"]
    ytd = fxs[fxs.index >= pd.Timestamp(date.today().year, 1, 1)]
    ytd_chg = (ytd.iloc[-1] / ytd.iloc[0] - 1) * 100 if len(ytd) > 1 else 0.0
    below = int((cpi.tail(12) < 1).sum())
    real = rate.iloc[-1] - cpi.iloc[-1]

    insights = [
        (BLUE, "Thai baht", f"USD/THB is at {fxs.iloc[-1]:.2f}, {abs(ytd_chg):.1f}% "
         f"{'weaker' if ytd_chg > 0 else 'stronger'} year-to-date. 12-month range: "
         f"{fxs.tail(252).min():.2f} – {fxs.tail(252).max():.2f}."),
        (AMBER, "Inflation", f"Headline CPI is {cpi.iloc[-1]:.2f}% YoY. {below} of the last 12 months "
         "came in below the 1% floor of the BOT target band."),
        (GREEN, "Monetary policy", f"The policy rate is {rate.iloc[-1]:.2f}% after {len(rate) - 1} change(s) "
         f"in this window. The ex-post real rate is {real:+.2f}%."),
    ]
    cw, y = 0.53, 0.70
    for color, title, body in insights:
        card(fig, L, y, cw, 0.155, accent=color)
        fig.text(L + 0.025, y + 0.115, title.upper(), fontsize=8, color=color, weight="bold")
        fig.text(L + 0.025, y + 0.03, textwrap.fill(body, 68), fontsize=10.5, color=INK, va="bottom",
                 linespacing=1.5)
        y -= 0.175

    # Latest-months table
    x2 = L + cw + 0.02
    w2 = R - x2
    card(fig, x2, 0.35, w2, 0.505)
    fig.text(x2 + 0.02, 0.815, "Latest 6 months", fontsize=10.5, color=INK, weight="bold")
    m = pd.DataFrame({"USD/THB avg": fxs.resample("MS").mean(), "CPI YoY %": cpi}).dropna().tail(6)
    m["Policy %"] = policy_on(m.index, pr)
    cx = [x2 + 0.025 + w2 * f for f in (0, 0.27, 0.53, 0.76)]
    ty = 0.765
    for c, xx in zip(["Month", *m.columns], cx):
        fig.text(xx, ty, c.upper(), fontsize=7.5, color=MUTED, weight="bold")
    for i, (d, row) in enumerate(m[::-1].iterrows()):
        yy = ty - 0.065 * (i + 1)
        if i % 2 == 0:
            fig.patches.append(plt.Rectangle((x2 + 0.01, yy - 0.02), w2 - 0.02, 0.055,
                                             transform=fig.transFigure, color=BG, zorder=0.5))
        for v, xx in zip([f"{d:%b %Y}", f"{row.iloc[0]:.2f}", f"{row.iloc[1]:+.2f}", f"{row.iloc[2]:.2f}"], cx):
            fig.text(xx, yy, v, fontsize=9.5, color=INK)

    # Notes
    card(fig, L, 0.07, R - L, 0.255)
    fig.text(L + 0.02, 0.29, "ABOUT THE DATA", fontsize=8, color=MUTED, weight="bold")
    notes = [
        "Source: Bank of Thailand API Portal (portal.api.bot.or.th): daily average exchange rate, "
        "policy rate history, headline CPI.",
        "Real policy rate = policy rate − headline CPI YoY (simple ex-post measure).",
        "Annualised volatility = standard deviation of daily % changes × √252.",
        "Regenerated every Monday by GitHub Actions. Raw CSVs are in the repository's data/ folder.",
        "Educational project only: not for commercial use, not investment advice, and not intended to "
        "harm any person or organization.",
    ]
    for i, n in enumerate(notes):
        fig.text(L + 0.02, 0.25 - i * 0.037, "•   " + n, fontsize=9, color=INK)
    return fig


def build(fx, infl, pr, source):
    return [page_overview(fx, infl, pr, source), page_insights(fx, infl, pr, source)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true", help="use offline sample data")
    args = ap.parse_args()

    fx, infl, pr, source = load(args.sample)
    OUT.mkdir(exist_ok=True)
    DATA.mkdir(exist_ok=True)
    fx.to_csv(DATA / "usd_thb.csv", index=False)
    infl.to_csv(DATA / "cpi_yoy.csv", index=False)
    pr.to_csv(DATA / "policy_rate.csv", index=False)

    figs = build(fx, infl, pr, source)
    with PdfPages(OUT / "thai_econ_dashboard.pdf") as pdf:
        pdf.infodict().update(Title="Thailand Macro Dashboard", Subject=DISCLAIMER)
        for f in figs:
            pdf.savefig(f, facecolor=f.get_facecolor())
    for f, name in zip(figs, ("dashboard_preview.png", "dashboard_insights.png")):
        f.savefig(OUT / name, dpi=130, facecolor=f.get_facecolor())
    print(f"Saved {OUT / 'thai_econ_dashboard.pdf'}  [{source}]")


if __name__ == "__main__":
    main()
