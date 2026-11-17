"""Draw the README accuracy chart from resultSVM.xlsx.

Run from the repository root:
    uv run --with openpyxl --with matplotlib python scripts/accuracy_chart.py
"""

import matplotlib
import openpyxl

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# Each setup was run in two batches ("Lote"): 1-2, 3-4, 5-6 and 7-8.
SETUPS = [
    "Reduced set\n18 attributes",
    "Full set\n18 attributes",
    "Full set\n3 attributes",
    "Full set\n5 attributes",
]
SERIES = [("dataCav", "Cavitation vs normal"), ("dataEmp", "Running empty vs normal")]
MODES = {
    "light": dict(surface="#fcfcfb", ink="#0b0b0b", muted="#52514e", grid="#e4e3df", colors=["#2a78d6", "#eb6834"]),
    "dark": dict(surface="#1a1a19", ink="#f0efec", muted="#c3c2b7", grid="#34332f", colors=["#3987e5", "#d95926"]),
}


def load() -> dict[str, list[float]]:
    sheet = openpyxl.load_workbook("resultSVM.xlsx", data_only=True)["resultSVM"]
    # columns: A name, B batch, ..., F mean accuracy
    acc: dict[str, dict[int, float]] = {"dataCav": {}, "dataEmp": {}}
    for row in sheet.iter_rows(min_row=2, max_row=17, min_col=1, max_col=6, values_only=True):
        name, batch, mean_acc = row[0], row[1], row[5]
        if name in acc and mean_acc is not None:
            acc[name][int(batch)] = float(mean_acc) * 100
    return {n: [(a[2 * i + 1] + a[2 * i + 2]) / 2 for i in range(4)] for n, a in acc.items()}


def draw(mode: str, data: dict[str, list[float]]) -> None:
    t = MODES[mode]
    fig, ax = plt.subplots(figsize=(9, 4.6), dpi=200)
    fig.patch.set_facecolor(t["surface"])
    ax.set_facecolor(t["surface"])
    width, gap = 0.36, 0.02
    for s, (key, label) in enumerate(SERIES):
        xs = [i + (s - 0.5) * (width + gap) for i in range(4)]
        bars = ax.bar(xs, data[key], width, color=t["colors"][s], label=label, zorder=3)
        for x, v in zip(xs, data[key]):
            ax.text(x, v + 1.2, f"{v:.1f}", ha="center", va="bottom", fontsize=9, color=t["ink"])
    ax.set_ylim(0, 112)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xticks(range(4), SETUPS, color=t["muted"], fontsize=9)
    ax.tick_params(axis="y", colors=t["muted"], labelsize=9, length=0)
    ax.tick_params(axis="x", length=0)
    ax.set_ylabel("Accuracy, 5-fold cross-validation (%)", color=t["muted"], fontsize=9)
    ax.yaxis.grid(True, color=t["grid"], linewidth=0.8, zorder=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(t["grid"])
    leg = ax.legend(loc="lower left", frameon=False, fontsize=9, ncol=2, bbox_to_anchor=(0, -0.3))
    for text in leg.get_texts():
        text.set_color(t["ink"])
    fig.subplots_adjust(bottom=0.27, left=0.09, right=0.99, top=0.97)
    fig.savefig(f"assets/results/accuracy-{mode}.png", facecolor=t["surface"])
    plt.close(fig)


if __name__ == "__main__":
    results = load()
    for name, vals in results.items():
        print(name, [round(v, 2) for v in vals])
    for mode in MODES:
        draw(mode, results)
