
import  pylab
import  matplotlib          as mpl
import  numpy               as np
import  matplotlib.colors   as colors
import  matplotlib.pyplot   as plt
import  matplotlib.colors   as mcolors
from    colormap            import cmap_builder, test_cmap # for _build_colormap()

# ---------------------------------------------------------------------------
# Useful colormaps:
# plt.cm.spectral, plt.get_cmap('jet')
# hint: reverse colormaps by adding underscore and r, e.g. plt.cm.spectral_r
# ---------------------------------------------------------------------------

# cmap_rg = mcolors.LinearSegmentedColormap('my_colormap', cdict, 100)

def _build_colormap(color1, color2, color3):
    """ Builds colormap from three given colors (given as strings)"""
    cm = cmap_builder('blue', 'orange', 'green')
    return cm

def show_truncated_colormap(cmap = plt.cm.spectral, minv = 0.2, maxv = 0.8):
    """ Compare original and truncated colormap """
    arr = np.linspace(0, 50, 100).reshape((10, 10))
    fig, ax = plt.subplots(ncols=2)

    cmap = plt.cm.spectral
    new_cmap = _truncate_colormap(cmap, minv, maxv)
    ax[0].imshow(arr, interpolation='nearest', cmap=cmap)
    ax[1].imshow(arr, interpolation='nearest', cmap=new_cmap)
    plt.show()

def _truncate_colormap(cmap = plt.cm.spectral, minval=0.0, maxval=1.0, n=100):
    """ Sample colormap from given colormap """

    """ """
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

def do_plot ( arr, filename = "test.png", title = "A plot", bool_save = False, minval=0, maxval=0.95, cmap=plt.cm.spectral ):
    """ A function to plot and label a raster dataset given as an array. Extra
        options to choose bounds of the colourscale and the colormap to use.
    """

    # TODO: use opencv for saving files

    dpi = 200

    # define source colormap
    cmap = plt.cm.spectral

    # cut colors of sourcecolormap to get appropriate colors for ndvi
    cmap_ndvi = _truncate_colormap(cmap, minval=0.9, maxval=0.5, n=100)

    plt.imshow (arr, interpolation='nearest', cmap = cmap)
    plt.title(title)
    plt.colorbar()
    plt.axis('off')

    if bool_save == True:
        plt.savefig(filename,bbox_inches='tight', dpi = dpi)
    else:
        plt.show()
    plt.clf()
