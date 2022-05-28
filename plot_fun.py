import matplotlib.pyplot as plt
from misc import assem_array


class Plotfun:
    def plot_curve(data, para, pax=None):
        ud, fd, r = para
        ax=pax if pax is not None else plt.figure(figsize=[8, 6]).add_axes([0.15, 0.15, 0.8, 0.8])
        ax.set_xlabel(r'$x(\mathrn{mm})$', fontsize=17)
        ax.set_ylabel(r'$F(N)$', fontsize=17)
        ax.scatter(data[0], data[1], marker='o', c='#ec7e2e', label='Optimized')
        # ax.plot(x[:21], y[:21], lw=2.0, c='#4a72b7', ls='--')
        # ax.plot([2, 2], [0, 10000], '--', c='#86c57e')
        ax.plot([ud-r, ud+r], [fd, fd], ls='--', lw=2.0, c='k')
        ax.plot([ud-r, ud-r], [0, fd], ls='--', c='k')
        ax.plot([ud+r, ud+r], [0, fd], ls='--', c='k')
        ax.tick_params(axis='both', labelsize=15)
        ax.ticklabel_format(axis='y', style='sci', scilimits=(3, 3),
                            useMathText=True)
        ax.set_xticks(range(0,17,4))
        ax.spines['bottom'].set_linewidth(0.75)
        ax.spines['left'].set_linewidth(0.75)
        ax.spines['top'].set_linewidth(0.75)
        ax.spines['right'].set_linewidth(0.75)
        ax.legend(loc=0, fontsize=15)
        ax.set(xlim=(0, 12), ylim=(0))
        # ax.grid(True)

    def plot_pop(arr, pax=None):
        aarr = assem_array(arr)
        ax=pax if pax is not None else plt.figure().add_axes([0, 0, 1, 1])
        ax.imshow(aarr, cmap='BuGn', vmin=0, vmax=1)
        ax.axis('equal')
        ax.axis('off')

    def plot_union(arr, data, para):
        fig, ax = plt.subplots(1, 2)
        Plotfun.plot_pop(arr, ax[0])
        Plotfun.plot_curve(data, para, ax[1])
        plt.tight_layout()
    
    def close_all():
        plt.close("all")
    
    def show():
        plt.pause(0.1)