#VIZMANAGER

#Will be the main realm where most of the dat viz will be calculated and stored for use on website,
#the MAIN program is the architect.
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

class VizManager:
    def __init__(self, analysis_results):
        self.results = analysis_results
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)

        self.palette = [
            (237 / 255, 28 / 255, 36 / 255),   # red
            (242 / 255, 101 / 255, 34 / 255),  # orange
            (247 / 255, 148 / 255, 29 / 255),  # vermillion
            (255 / 255, 198 / 255, 11 / 255),  # yellow
            (203 / 255, 219 / 255, 42 / 255),  # chartreuse
            (141 / 255, 198 / 255, 63 / 255),  # lime
            (57 / 255, 181 / 255, 74 / 255),   # green
            (0 / 255, 168 / 255, 133 / 255),   # seagreen
            (0 / 255, 171 / 255, 184 / 255),   # turquoise
        ]
        self.dark = {
            "black": (51 / 255, 51 / 255, 51 / 255),
            "gray": (120 / 255, 120 / 255, 120 / 255),
            "lightgray": (187 / 255, 187 / 255, 187 / 255),
            "white": (1.0, 1.0, 1.0),
        }

        self._apply_style()

    def _apply_style(self):
        """Sets global matplotlib style to match brand"""
        plt.rcParams.update({
            "figure.facecolor": self.dark["black"],
            "axes.facecolor": self.dark["black"],
            "axes.edgecolor": self.dark["lightgray"],
            "axes.labelcolor": self.dark["white"],
            "axes.titlecolor": self.dark["white"],
            "xtick.color": self.dark["lightgray"],
            "ytick.color": self.dark["lightgray"],
            "text.color": self.dark["white"],
            "grid.color": self.dark["gray"],
            "grid.linestyle": "--",
            "grid.alpha": 0.4,
            "font.family": "sans-serif",
            "axes.titlesize": 13,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
        })
    def get_top_n(self, dataset_key, sector, n=10):
        dataset = self.results.get(dataset_key, {})
        sector_data = dataset.get(sector, {})

        sorted_data = sorted(
            sector_data.items(), key=lambda x: x[1], reverse=True
        )[:n]
        labels = [x[0] for x in sorted_data]
        values = [x[1] for x in sorted_data]

        return labels, values

    def plot_3d_bars(self, labels, values, title, filename):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        x = np.arange(len(labels))
        y = np.zeros(len(labels))
        z = np.zeros(len(labels))
        dx = np.ones(len(labels)) * 0.5
        dy = np.ones(len(labels)) * 0.5
        dz = values
        colors = plt.cm.viridis(np.array(values) / max(values))
        ax.bar3d(x, y, z, dx, dy, dz, color=colors)

        # Labeling
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=30, ha='right')
        ax.set_title(title)
        for i, val in enumerate(values):
            ax.text(x[i], y[i], val, f"{val:,.0f}", ha='center')
        # Saving Diagrams
        filepath = self.output_dir / f"{filename}.png"
        plt.savefig(filepath, bbox_inches='tight')
        plt.close()

        return filepath

    def generate_description(self, labels, values, sector, dtype):
        if not values:
            return (f"No data available for {sector}.")
        top_label = labels[0]
        top_value = values[0]
        total = sum(values)

        dtype_map = {
            "direct_total_country": "total emissions",
            "direct_annual_country": "annual emissions",
            "potential_total_country": "potential emissions",
            "potential_annual_country": "annual potential emissions",
            "methane_annual_country": "methane emissions"
        }

        readable_type = dtype_map.get(dtype, "emissions")

        top_label = labels[0]
        top_value = values[0]
        total = sum(values)

        description = (
            f"In the {sector} sector, {top_label} is the dominant contributor, "
            f"producing approximately {top_value:,.0f} MtCO2 of {readable_type}. "
            f"Across the top {len(labels)} contributors, total emissions reach about "
            f"{total:,.0f}"
        )
        if len(values) > 1 and values[1] > 0:
            ratio = top_value / values[1] if values[1] else 0
            description += f" {top_label} emits about {ratio:.1f}x more than the second largest contributor in this sector."
        share = (top_value / total) * 100 if total else 0
        description += f" {top_label} alone accounts for about {share:.1f}% of emissions among these top contributors in the {sector} sector."
        return description

    def save_description(self, text, filename):
        filepath = self.output_dir / f"{filename}.txt"
        with open(filepath, "w") as f:
            f.write(text)
            return filepath

    def create_sector_visual(self, sector, dtype_key):
        labels, values = self.get_top_n(dtype_key, sector)

        if not labels:
            print(f"No data for {sector} ({dtype_key})")
            return
        title = f"{sector.upper()} - {dtype_key}"
        filename = f"{sector}_{dtype_key}"
        img_path = self.plot_3d_bars(labels, values, title, filename)
        desc = self.generate_description(labels, values, sector, dtype_key)
        txt_path = self.save_description(desc, filename)

        print(f"Saved diagram: {img_path}")
        print(f"Saved description: {txt_path}")
