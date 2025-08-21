from spidb import lookup
import matplotlib.pyplot as plt
import numpy as np
from dankpy import color


def generate_boxwhisker(df, feature="snr", notch=False, showcaps=False, whis=0):
    # groups = data.groupby(["target", "material"])
    # targets = snr.index.tolist()

    # materials = ["Oatmeal", "Rice", "Flour", "Wheat Groats", "Corn Flakes"]
    # targets = ['$\\it{C.}$ $\\it{maculatus}$', '$\\it{T.}$ $\\it{confusum}$',
    #    '$\\it{T.}$ $\\it{molitor}$ (larvae)',
    #    '$\\it{T.}$ $\\it{molitor}$']

    data = df.copy()

    data["material"] = data["material"].apply(
        lambda x: f"{lookup.lookup(x, latex=True, min=True)} \n {x}"
    )

    data["target"] = data["target"].apply(
        lambda x: lookup.lookup(x, latex=True, min=True)
    )

    materials = data.material.unique()
    materials.sort()
    targets = data.target.unique()
    targets.sort()

    j = 0

    fig, ax = plt.subplots()
    for m in materials:
        # for m in data.material.unique():
        group = data[data["material"] == m]
        group.sort_values(by="target", inplace=True)

        artists = []
        c = 0
        for i in targets:
            # for i in data.target.unique():
            g = group[group["target"] == i]
            b = ax.boxplot(
                g[feature].values,
                positions=[j + 0.5],
                showfliers=False,
                boxprops=dict(facecolor=color.colors[c]),
                medianprops=dict(color="black", linewidth=0),
                patch_artist=True,
                widths=0.25,
                showcaps=showcaps,
                notch=notch,
                whis=whis,
            )
            j += 1
            c += 1
            artists.append(b)
        # p += 1
    ax.set_ylim(0, None)
    # ax.set_ylim(85, None)
    # ax.set_yticks(np.arange(85, 126, 10))

    if feature == "nsel":
        ax.set_ylabel("NSEL [dB]")
    elif feature == "nspa":
        ax.set_ylabel("NSPA [dB]")

    # place legend above the plot
    ax.legend(
        [element["boxes"][0] for element in artists],
        list(group.target.unique()),
        loc="upper center",
        ncols=4,
        columnspacing=1,
        markerscale=0.5,
        bbox_to_anchor=(0.5, 1.35),
    )

    lims = ax.get_xlim()
    ax.set_xticks(
        np.arange(0, lims[1], lims[1] // len(materials))
        + lims[1] // (2 * len(materials))
    )
    ax.vlines(np.arange(0, 20, 4), 0, 100, color="black", alpha=0.25)
    ax.set_xticklabels([material for material in materials])
    ax.vlines(np.arange(0, 20, 4), 0, 80, color="black", alpha=0.25)
    ax.set_xticklabels([material for material in materials])
    plt.tick_params(axis="x", which="both", bottom=False, top=False)

    return fig, ax
