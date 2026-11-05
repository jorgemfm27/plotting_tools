import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap, to_rgba
from matplotlib.ticker import LogLocator, LogFormatter
from matplotlib import patches, path
# from matplotlib.transforms import as transforms

##############################################
# Plotting methods
##############################################
def plot_matrix(matrix, ax = None, 
                cmap: str = 'viridis', 
                tick_labels: list = None,
                quantity_label: str = None,
                unit: str = None,
                title: str = None,
                vmin: float = None,
                vmax: float = None, 
                lognorm: bool = False,
                fontsize: float = 10,
                cbar_orientation: str = 'vertical',
                print_numbers: bool = False,
                reverse_text_color: bool = False,
                decimal_place: int = None):
    '''
    Plot a matrix.
    '''
    # figure
    if not ax:
        fig, ax = plt.subplots(figsize=((2+matrix.shape[0]*0.5)+2, (2+matrix.shape[1]*0.5)))
    else:
        fig = plt.gcf()
    # color scale
    if (not vmin):
        vmin = np.min(abs(matrix))
    if (not vmax):
        vmax = np.max(abs(matrix))
    if lognorm:
        norm = matplotlib.colors.LogNorm(vmin=vmin, vmax=vmax)
        c_thresh = 10**((np.log10(vmax)+np.log10(vmin))/2)
    else:
        norm = None
        c_thresh = (vmax+vmin)/2
    # Plot matrix
    im = ax.matshow(np.abs(matrix), cmap=cmap, norm=norm)
    ax.set_xticks([i for i in range(matrix.shape[1])])
    ax.set_yticks([i for i in range(matrix.shape[0])])
    if tick_labels:
        max_char = max([ len(label) for label in ['port 1', 'port 2', 'port b']])
        ax.set_xticklabels(tick_labels, rotation=45 if max_char>15 else None)
        ax.set_yticklabels(tick_labels)
    # colorbar
    get_cbar(im, ax, label=quantity_label, unit=unit, orientation=cbar_orientation)
    # print numbers
    if print_numbers:
        for i  in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                text_str = quantity_to_string(val=matrix[i,j], unit=unit, decimal_place=decimal_place)
                if reverse_text_color:
                    text_clr = 'w' if abs(matrix[i,j]) > c_thresh else 'k'
                else:
                    text_clr = 'w' if abs(matrix[i,j]) < c_thresh else 'k'
                ax.text(j, i, text_str, color=text_clr, va='center', ha='center', fontsize=fontsize)
    # title
    if title:
        ax.set_title(title)

def plot_line_cmap(x, y, color_percentage: float, ax = None, cmap: str = 'viridis', **kw):
    '''
    Plot a line with single color colored by a colormap.
    '''
    # figure
    if not ax:
        ax = plt.gca()
    else:
        fig = plt.gcf()
    # define colormap
    cmap = matplotlib.colormaps[cmap]
    color = cmap(color_percentage)
    # plot
    ax.plot(x, y, color=color, **kw)

def plot_line_with_cmap(x, y, color_percentage: list, ax = None, cmap: str = 'viridis', **kw):
    '''
    Plot a line with gradient by a colormap.
    '''
    # figure
    if not ax:
        ax = plt.gca()
    else:
        fig = plt.gcf()
    # Color level to map
    c_xy = color_percentage
    # Parse data for line segments
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    # # Build colormap 
    # if color_termination: # use custom color termination
    #     cmap = LinearSegmentedColormap.from_list('custom_cmap', [color_termination, _color])
    # else:
    #     cmap = LinearSegmentedColormap.from_list('custom_cmap', [to_rgba(_color, 0), _color])
    cmap = matplotlib.colormaps[cmap]
    norm = plt.Normalize(0, 1)
    lc = LineCollection(segments, cmap=cmap, norm=norm)
    lc.set_array(c_xy)
    lc.set_lw(2)
    line = ax.add_collection(lc, **kw)
    ax.plot(x,y, color='None')

def plot_stiched_data(X_values: list, Y_axis: list, Data_axis: list, ax=None, **plot_args):
    '''
    Plot stiched data.
    Args:
        X_values: list of x values in plot.
        Y_axis: list of y axis for each x value.
        Data_axis: list of each data set for each x value.
    '''
    if not ax:
        fig, ax = plt.subplots()
    else:
        fig = plt.gcf()

    _unique_x_values = np.sort(np.unique(X_values))
    for i, (x_value, y_axis, data_axis) in enumerate(zip(X_values, Y_axis, Data_axis)):
        # format y axis for stich plot
        dy = y_axis[1]-y_axis[0]
        _y_values = np.append(y_axis, [y_axis[-1]+dy])
        _y_axis = np.vstack([_y_values-dy/2, _y_values-dy/2])
        # format x axis for stich plot
        _i = int(np.where(x_value==_unique_x_values)[0])
        if _i == 0:
            dx = _unique_x_values[1]-_unique_x_values[0]
            _x_axis = np.repeat(np.array([[x_value-dx/2], [x_value+dx/2]]), repeats=_y_values.shape[0], axis=1)
        elif _i == len(_unique_x_values)-1:
            dx = _unique_x_values[_i] - np.mean(_unique_x_values[_i-1:_i+1])
            _x_axis = np.repeat(np.array([[np.mean(_unique_x_values[_i-1:_i+1])], [_unique_x_values[_i]+dx]]),
                                repeats=_y_values.shape[0], axis=1)
        else:
            _x_axis = np.repeat(np.array([[np.mean(_unique_x_values[_i-1:_i+1])], [np.mean(_unique_x_values[_i:_i+2])]]),
                                repeats=_y_values.shape[0], axis=1)
        # format results for stich plot
        _data_axis = data_axis.reshape(1, len(data_axis))
        # plot data
        ax.pcolormesh(_x_axis, _y_axis, _data_axis, shading='flat', **plot_args)
    return fig, ax

def plot_squiggly_line(x0, y0, x1, y1, amp=0.2, periods=8, **kw):
    '''
    Draw a squiggly line.
    '''
    # arrow plot flags
    arrow_0 = kw.get('arrow_0', False)
    arrow_1 = kw.get('arrow_1', True)
    # arrow dimensionts
    l_arrow_x = kw.get('l_arrow_x', .1)
    l_arrow_y = kw.get('l_arrow_y', .1)
    dx = x1-x0
    dy = y1-y0
    theta = np.arctan2(dy, dx)
    if arrow_0:
        x0 = x0 + l_arrow_x*np.cos(theta)
        y0 = y0 + l_arrow_y*np.sin(theta)
    if arrow_1:
        x1 = x1 - l_arrow_x*np.cos(theta)
        y1 = y1 - l_arrow_y*np.sin(theta)
    # get current axis
    ax = kw.get('ax', plt.gca())
    # Plot settings
    _plot_args = dict(color=kw.get('color', 'k'), lw=kw.get('lw', 2), solid_capstyle='round', clip_on=False)
    # compute displacement
    dx = x1-x0
    dy = y1-y0
    theta = np.arctan2(dy, dx)
    L = np.sqrt(dx**2 + dy**2)/2
    # midpoint
    x_avg, y_avg = (x0+x1)/2, (y0+y1)/2
    # waveform
    pad = kw.get('pad', L/5)
    phi = np.linspace(0, 2*np.pi, 101)*periods
    x = np.linspace(-(L-pad), (L-pad), len(phi))
    y = np.sin(phi)*amp
    # add padding
    x = np.array([-L]+list(x)+[L])
    y = np.array([0]+list(y)+[0])
    # plot
    ax.plot(x*np.cos(theta)-y*np.sin(theta) + x_avg, y*np.cos(theta)+x*np.sin(theta) + y_avg, **_plot_args)
    # arrow
    _plot_args = dict(color=kw.get('color', 'k'), lw=0, clip_on=False)
    # arrow at point 0
    if arrow_0:
        pts = np.array([[x0+l_arrow_x*np.cos(theta), x0+l_arrow_x/2*np.cos(theta+np.pi/2), x0, x0+l_arrow_x/2*np.cos(theta-np.pi/2)],
                        [y0-l_arrow_y*np.sin(theta), y0-l_arrow_y/2*np.sin(theta+np.pi/2), y0, y0-l_arrow_y/2*np.sin(theta-np.pi/2)]]).T
        ax.add_patch(patches.Polygon(pts, **_plot_args))
    # arrow at point 1
    if arrow_1:
        pts = np.array([[x1+l_arrow_x*np.cos(theta), x1+l_arrow_x/2*np.cos(theta+np.pi/2), x1, x1+l_arrow_x/2*np.cos(theta-np.pi/2)],
                        [y1+l_arrow_y*np.sin(theta), y1+l_arrow_y/2*np.sin(theta+np.pi/2), y1, y1+l_arrow_y/2*np.sin(theta-np.pi/2)]]).T
        ax.add_patch(patches.Polygon(pts, **_plot_args))

def plot_polygon_patch(xy_coords, radius=0, **kw):
    '''
    Plot polygon patch.
    Args:
        radius: if not 0, rounds egdes of polygon.
    '''
    class RoundedPolygon(patches.PathPatch):
        def __init__(self, xy, pad, **kwargs):
            p = path.Path(*self.__round(xy=xy, pad=pad))
            super().__init__(path=p, **kwargs)
        def __round(self, xy, pad):
            n = len(xy)
            for i in range(0, n):
                x0, x1, x2 = np.atleast_1d(xy[i - 1], xy[i], xy[(i + 1) % n])
                d01, d12 = x1 - x0, x2 - x1
                d01, d12 = d01 / np.linalg.norm(d01), d12 / np.linalg.norm(d12)
                x00 = x0 + pad * d01
                x01 = x1 - pad * d01
                x10 = x1 + pad * d12
                x11 = x2 - pad * d12
                if i == 0:
                    verts = [x00, x01, x1, x10]
                else:
                    verts += [x01, x1, x10]
            codes = [path.Path.MOVETO] + n*[path.Path.LINETO, path.Path.CURVE3, path.Path.CURVE3]
            return np.atleast_1d(verts, codes)
    ax = kw.pop('ax', plt.gca())
    ax.add_patch(RoundedPolygon(xy_coords, pad=radius, **kw))

def plot_arrow(x0, y0, x1, y1, arc_rad=.3, head_width=5, head_length=5, tail_width=1, **kw):
    '''
    Args:
        arc_rag : curvature of arrow in radians.
    '''
    ax = kw.pop('ax', plt.gca())
    clip_on = kw.pop('clip_on', False)
    lw = kw.pop('lw', 2)
    arrowstyle = kw.pop('arrowstyle', '<->')
    color = kw.pop('color', None)
    # Arrow
    kw = dict(arrowstyle=f'{arrowstyle}, head_width={head_width}, head_length={head_length}')
    ax.add_patch(patches.FancyArrowPatch((x0, y0), (x1, y1), connectionstyle=f'arc3,rad={arc_rad}', clip_on=clip_on, lw=lw, color=color, **kw))

##############################################
# Plotting helper functions
##############################################
SI_PREFIXES = dict(zip(range(-24, 25, 3), 'yzafpnμm kMGTPEZY'))
SI_PREFIXES[0] = ""
SI_UNITS = ',m,s,g,W,J,V,A,F,T,H,Hz,Ohm,S,N,C,px,b,B,K,Bar,Vpeak,Vpp,Vp,Vrms,$\Phi_0$,$s^{-1}$,A/s'.split(
    ',')

def SI_prefix_and_scale_factor(val, unit=None):
    """
    Takes in a value and unit and if applicable returns the proper
    scale factor and SI prefix.
    Args:
        val (float) : the value
        unit (str)  : the unit of the value
    returns:
        scale_factor (float) : scale_factor needed to convert value
        unit (str)           : unit including the prefix
    """

    if unit in SI_UNITS:
        try:
            with np.errstate(all="ignore"):
                prefix_power = np.log10(abs(val))//3 * 3
                if unit in ['$s^{-1}$']:
                    prefix = SI_PREFIXES[-prefix_power]
                else:
                    prefix = SI_PREFIXES[prefix_power]
                # Greek symbols not supported in tex
                if plt.rcParams['text.usetex'] and prefix == 'μ':
                    prefix = r'$\mu$'
            return 10 ** -prefix_power, prefix + unit
        except (KeyError, TypeError):
            pass
    return 1, unit if unit is not None else ""

def quantity_to_string(val, unit, error=None, decimal_place=None):
    scale_factor, prefix = SI_prefix_and_scale_factor(val, unit)
    scaled_val = val*scale_factor
    # write number with uncertainty
    if error:
        scaled_error = error*scale_factor
        decimal_place_val = int(np.floor(np.log10(scaled_val)))
        decimal_place_error = int(np.floor(np.log10(scaled_error)))
        try:
            if decimal_place_error < 0:
                val_str = str(float(scaled_val))[:(decimal_place_val-decimal_place_error)+1]
                unc_digit = int(np.round(scaled_val%(10**(decimal_place_error+1))*(10**(-decimal_place_error))))
                unc_str = f'({unc_digit})'
                quantity_str = f'{val_str}{unc_str} {prefix}'
            elif decimal_place_error > decimal_place_val:
                val_str = str(int(scaled_val))
                quantity_str = f'({val_str}) {prefix}'
            else:
                val_str = str(float(scaled_val))[:(decimal_place_val-decimal_place_error)]
                unc_digit = int(np.round(scaled_val%(10**(decimal_place_error+1))  ))
                unc_str = f'({unc_digit})'
                quantity_str = f'{val_str}{unc_str} {prefix}'
        except:
            print('Could not write uncertainty!')
            decimal_place = 0
            quantity_str = '{:.{}f} {}'.format(scaled_val, decimal_place, prefix)
    else:
        if decimal_place is None:
            decimal_place = 3
        return f"{scaled_val:.{decimal_place}f} {prefix}"
    return quantity_str

def set_xlabel(label='', unit=None, axis=None, latexify_ticks=False, **kw):
    """
    Add a unit aware x-label to an axis object.
    Args:
        axis: matplotlib axis object to set label on
        label: the desired label
        unit:  the unit
        **kw : keyword argument to be passed to matplotlib.set_xlabel
    """
    if axis is None:
        axis = plt.gca()
    if unit is not None and unit != '':
        xticks = axis.get_xticks()
        scale_factor, unit = SI_prefix_and_scale_factor(
            val=max(abs(xticks)), unit=unit)
        tick_str = '{:.4g}' if not latexify_ticks else r'${:.4g}$'
        formatter = matplotlib.ticker.FuncFormatter(
            lambda x, pos: tick_str.format(x * scale_factor))
        axis.xaxis.set_major_formatter(formatter)
        axis.set_xlabel(label + ' ({})'.format(unit), **kw)
    else:
        axis.set_xlabel(label, **kw)
    return axis

def set_ylabel(label='', unit=None, axis=None, latexify_ticks=False, **kw):
    """
    Add a unit aware y-label to an axis object.
    Args:
        axis: matplotlib axis object to set label on
        label: the desired label
        unit:  the unit
        **kw : keyword argument to be passed to matplotlib.set_ylabel
    """
    if axis is None:
        axis = plt.gca()
    if unit is not None and unit != '':
        yticks = axis.get_yticks()
        scale_factor, unit = SI_prefix_and_scale_factor(
            val=max(abs(yticks)), unit=unit)
        tick_str = '{:.6g}' if not latexify_ticks else r'${:.6g}$'
        formatter = matplotlib.ticker.FuncFormatter(
            lambda x, pos: tick_str.format(x * scale_factor))
        axis.yaxis.set_major_formatter(formatter)
        axis.set_ylabel(label + ' ({})'.format(unit), **kw)
    else:
        axis.set_ylabel(label, **kw)
    return axis

def set_cbarlabel(cbar, label, unit=None, change_ticks=False, **kw):
    """
    Add a unit aware z-label to a colorbar object

    Args:
        cbar: colorbar object to set label on
        label: the desired label
        unit:  the unit
        **kw : keyword argument to be passed to cbar.set_label
    """
    if unit is not None and unit != '':
        if change_ticks:
            zticks = cbar.get_ticks()[1:-1]
            scale_factor, unit = SI_prefix_and_scale_factor(
                val=max(abs(zticks)), unit=unit)
            cbar.set_ticks(zticks)
            cbar.set_ticklabels([f'{v:.3g}' for v in zticks*scale_factor])
        cbar.set_label(label + ' ({})'.format(unit))
    else:
        cbar.set_label(label, **kw)
    return cbar

def set_aspect_ratio_lim(axis, ratio_x, ratio_y):
    '''
    Adjust limits of axis to achieve a desired aspect ratio.
    '''
    xlim = axis.get_xlim()
    ylim = axis.get_ylim()
    dx = abs(xlim[0]-xlim[1])
    dy = abs(ylim[1]-ylim[0])
    aspect_ratio = dy/dx
    if aspect_ratio < 1:
        ylim_new = np.mean(ylim) - dx/2*ratio_y, np.mean(ylim) + dx/2*ratio_y
        xlim_new = np.mean(xlim) - dx/2*ratio_x, np.mean(xlim) + dx/2*ratio_x
    else:
        xlim_new = np.mean(xlim) - dy/2*ratio_x, np.mean(xlim) + dy/2*ratio_x
        ylim_new = np.mean(ylim) - dy/2*ratio_y, np.mean(ylim) + dy/2*ratio_y
    axis.set_xlim(xlim_new)
    axis.set_ylim(ylim_new)

def move_subplot(ax, dx: float = 0, dy: float = 0, scale_x: float = 1, scale_y: float = 1):
    '''
    Move subplot by dx and dy
    '''
    pos = ax.get_position()
    pos = [pos.x0+dx*pos.width*scale_x, pos.y0+dy*pos.height*scale_y, pos.width*scale_x, pos.height*scale_y]
    ax.set_position(pos)

def get_cbar(mappeable=None, ax = None, orientation: str = 'vertical', pos: tuple = None, dims: tuple = None, label: str = None, unit: str = None, **kw):
    '''
    Add a cbar to subplot.
    Args:
        pos  : colorbar position tuple in relative axis units.
        dims : colorbar dimensions tuple (lx, ly) in relative axis units.
    '''
    assert orientation in ['vertical', 'horizontal']
    cmap = kw.get('cmap', None)
    if mappeable is None:
        vmin = kw.get('vmin', 0)
        vmax = kw.get('vmax', 1)
        norm = kw.get('norm', matplotlib.colors.Normalize(vmin=vmin, vmax=vmax))
        # mappeable = matplotlib.collections.QuadMesh(np.array([[[0,0],[1,1]]]), norm=norm, cmap=cmap)
        mappeable = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    if ax is None:
        ax = plt.gca()
    fig = ax.get_figure()
    cbar_ax = fig.add_subplot(111)
    _pos = ax.get_position()
    if dims is None:
        if orientation == 'vertical':
            dims = (0.05 ,1)
        else:
            dims = (1, 0.05)
    if pos is None:
        if orientation == 'vertical':
            pos = (1.05 ,0)
        else:
            pos = (0, -0.1)
            ax.xaxis.set_ticks_position('top')
            ax.xaxis.set_label_position('top')
    cbar_ax.set_position([_pos.x0+_pos.width*pos[0], _pos.y0+_pos.height*pos[1], _pos.width*dims[0], _pos.height*dims[1]])
    cbar = fig.colorbar(mappeable, cax=cbar_ax, orientation=orientation)
    # if mappeable is None and type(norm) is matplotlib.colors.LogNorm:
    #     cb.formatter = LogFormatter(10)
    #     # set ticks in log scale
    #     cb.locator = LogLocator() 
    #     cb.update_ticks()
    #     cbar_ax.set_ylim(vmin, vmax)
    if label:
        set_cbarlabel(cbar, label, unit=unit)
    return cbar

def get_fig(figsize, **kw):
    fig, axs = plt.subplots(figsize=figsize, **kw)
    return fig, axs

def savefig(fig, figname=None):
    '''
    Save figure to desktop.
    '''
    if type(fig) == str:
        figname = fig
        fig = plt.gcf()
    else:
        assert figname, 'need to provide figname.'
    fig.savefig(fname=rf'/Users/jorge/Desktop/{figname}', dpi=300, bbox_inches='tight')

##############################################
# Plotting Quantum circuits
##############################################
class Quantum_circuit(object):
    def __init__(self, Qubits, ax=None, step_size_x=None, lw=1, **kw):
        if not ax:
            fig, ax = plt.subplots(figsize=(.6, .6*len(Qubits)), dpi=100)
        else:
            fig = ax.get_figure()
        # Qubit names
        self.Qubits = Qubits
        # Circuit axis
        self.ax = ax
        # Format graphic positions
        _xlim = ax.get_xlim()
        _ylim = ax.get_ylim()
        x_range = _xlim[1]-_xlim[0]
        y_range = _ylim[1]-_ylim[0]
        n = len(Qubits)
        y_positions = np.linspace(_ylim[0], _ylim[1], 2*(n-1)+3)[1::2]
        # Determine axis size
        bbox = self.ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        dx, dy = bbox.width, bbox.height
        # Determine gate size
        if not step_size_x:
            self.step_x = (y_range/len(y_positions))/(dx/dy)
            self.l_gate_y = (y_range/len(y_positions))*.8
        else:
            self.step_x = step_size_x
            self.l_gate_y = step_size_x*(dx/dy)*.8
        self.l_gate_x = self.step_x*.8
        self.lw = lw
        x_positions = np.ones(len(Qubits))*self.step_x/2+_xlim[0]
        # Qubit positions
        self.Q_pos = {q: [x_positions[i], y_positions[i]] for i, q in enumerate(Qubits)}
        # other arguments
        alpha = kw.get('alpha', 1)
        X_max = kw.get('X_max', {})
        # Draw initial circuit
        # for q, pos in zip(Qubits, y_positions):
        #     _xmax = X_max.get(q, 1)
        #     ax.axhline(pos, xmax=_xmax, color='k', lw=self.lw, ls='-', zorder=-1, alpha=alpha, clip_on=False)
        ax.axis('off')

    def add_initial_state(self, qubit, state, color='k', x_pad=0, size=None):
        _x, _y = self.Q_pos[qubit]
        self.ax.text(-self.l_gate_x/2*.65+x_pad, _y, state, color=color, size=size, va='center', ha='right')

    def add_single_Q_gate(self, qubit, name=None, length=1, ls='-', size=None, double_gate=False, **kw):
        '''
        Adds a single qubit gate on a qubit.
        '''
        _x, _y = self.Q_pos[qubit]
        # gate params
        _ec = kw.get('ec', 'k')
        if 'alpha' in kw:
            alpha = kw.get('alpha')
            _patch = patches.Rectangle((_x-(self.l_gate_x*length)/2, _y-self.l_gate_y*length/2), self.l_gate_x*length, self.l_gate_y*length,
                                       ec=_ec, fc='w', alpha=1, lw=0, zorder=1, ls=ls, clip_on=False)
            self.ax.add_patch(_patch)
        else:
            alpha = 1
        _patch = patches.Rectangle((_x-(self.l_gate_x*length)/2, _y-self.l_gate_y*length/2), self.l_gate_x*length, self.l_gate_y*length,
                                   ec=_ec, fc='w', alpha=alpha, lw=self.lw, zorder=1, ls=ls, clip_on=False)
        self.ax.add_patch(_patch)
        # write gate name
        if name:
            self.ax.text(_x, _y, name, va='center', ha='center', size=size, alpha=alpha, color=_ec, clip_on=False)
        # Draw double colored gate
        elif double_gate:
            color_1, color_2 = kw.get('color_1', 'C0'), kw.get('color_2', 'C1')
            _points = [[_x-self.l_gate_x/2, _y-self.l_gate_y/2], [_x-self.l_gate_x/2, _y+self.l_gate_y/2],
                       [_x+self.l_gate_x/2, _y+self.l_gate_y/2]]
            self.ax.add_patch(patches.Polygon(_points, color=color_1, alpha=.2, lw=0, clip_on=False, zorder=1))
            _points = [[_x-self.l_gate_x/2, _y-self.l_gate_y/2], [_x+self.l_gate_x/2, _y-self.l_gate_y/2],
                       [_x+self.l_gate_x/2, _y+self.l_gate_y/2]]
            self.ax.add_patch(patches.Polygon(_points, color=color_2, alpha=.2, lw=0, clip_on=False, zorder=1))
            # write gate names
            if 'name_1' in kw:
                name_1 = kw.get('name_1')
                self.ax.text(_x-self.l_gate_x/8, _y+self.l_gate_y/8, name_1, c=color_1, ha='center', va='center', size=size)
            if 'name_2' in kw:
                name_2 = kw.get('name_2')
                self.ax.text(_x+self.l_gate_x/8, _y-self.l_gate_y/4, name_2, c=color_2, ha='center', va='center', size=size)
        # add label
        label = kw.get('label', None)
        fontsize = kw.get('fontsize', None)
        clabel = kw.get('clabel', None)
        ylabel_correction = kw.get('ylabel_correction', 0)
        if label:
            self.ax.text(_x, _y+self.l_gate_y*(1.25/2)+ylabel_correction, f'{label}', va='bottom', ha='center', size=fontsize, color=clabel)
        # Update qubit position
        self.ax.axhline(_y, xmax=self.Q_pos[qubit][0], color='k', lw=self.lw, ls='-', zorder=-1, clip_on=False)
        self.Q_pos[qubit][0] += self.step_x+(length-1)*self.l_gate_x
        
    def add_measurement(self, qubit, steps = 1.8, alpha=1, head_size=1, head_length=1, **kw):
        '''
        Adds a measurement on a qubit.
        '''
        assert steps > 1, "Measurement needs at least 2 steps of duration"
        _x, _y = self.Q_pos[qubit]
        # gate params
        _patch = patches.Polygon([[_x-self.l_gate_x/2, _y-self.l_gate_y/2], [_x-self.l_gate_x/2, _y+self.l_gate_y/2],
                                  [_x+(steps-1)*self.step_x+self.l_gate_x/2, _y+self.l_gate_y/2],
                                  [_x+(steps-1)*self.step_x+self.l_gate_x/2, _y-self.l_gate_y/2]],
                                   ec=to_rgba('k', alpha), fc='w', lw=self.lw, zorder=1, clip_on=False)
        self.ax.add_patch(_patch)
        _patch = patches.Arc((_x+self.l_gate_x/2, _y-self.l_gate_y/3), self.l_gate_x*1.15, self.l_gate_y*1.15,
                             angle=0, theta1=0.0, theta2=180, color='k', lw=self.lw, zorder=1, alpha=alpha, clip_on=False)
        self.ax.add_patch(_patch)
        _head_width, _head_length = .1*head_size, .15*head_size
        self.ax.annotate('', xy=(_x+1.8/2*self.l_gate_x/2, _y-self.l_gate_y/2.5), 
                    xytext=(_x+1.1*self.l_gate_x*head_length, _y+.9*self.l_gate_y/2.5*head_length), zorder=1,
                    arrowprops=dict(arrowstyle=f'<|-, head_width={_head_width}, head_length={_head_length}',
                    color=to_rgba('k', alpha), lw=self.lw), annotation_clip=False)
        # add label
        label = kw.get('label', None)
        fontsize = kw.get('fontsize', None)
        clabel = kw.get('clabel', None)
        label_pos = kw.get('label_pos', 'top')
        ylabel_correction = kw.get('ylabel_correction', 0)
        if label:
            assert label_pos in ['top', 'bottom'], '"label_pos" must be "top" or "bottom"'
            if label_pos == 'bottom':
                self.ax.text(_x+(steps-1)*self.step_x/2, _y-self.l_gate_y*(1.25/2)+ylabel_correction, f'{label}', va='top', ha='center', size=fontsize, color=clabel)
            else:
                self.ax.text(_x+(steps-1)*self.step_x/2, _y+self.l_gate_y*(1.25/2)+ylabel_correction, f'{label}', va='bottom', ha='center', size=fontsize, color=clabel)
        # Update qubit position
        self.ax.axhline(_y, xmax=self.Q_pos[qubit][0], color='k', lw=self.lw, ls='-', zorder=-1, clip_on=False)
        self.Q_pos[qubit][0] += steps*self.step_x
        
    def add_barrier(self, qubits, steps = 0, apply_dashed = False, draw_arrow = False, **kw):
        '''
        Adds a barrier between qubits with wait time <steps>
        apply_dashed: draw dotted circuit line during barrier.
        add_arrow: draw arrow during barrier.
        '''
        if type(qubits) is str:
            qubits = [qubits]
        _Xs = [ self.Q_pos[q][0] for q in qubits]
        _x_barrier = np.max(_Xs)
        # Plot dashed circuit line
        if apply_dashed:
            _xlim, _ylim = self.ax.get_xlim(), self.ax.get_ylim()
            for q in qubits:
                _x = [self.Q_pos[q][0]-self.l_gate_x, _x_barrier+steps*self.step_x]
                _y = [self.Q_pos[q][1], self.Q_pos[q][1]]
                self.ax.plot(_x, _y, 'w--', lw=self.lw*2, zorder=.9, clip_on=False)
            self.ax.set_xlim(_xlim), self.ax.set_ylim(_ylim)
        # Plot arrow
        if draw_arrow:
            _xlim, _ylim = self.ax.get_xlim(), self.ax.get_ylim()
            for q in qubits:
                _x = [self.Q_pos[q][0]-self.step_x+self.l_gate_x/2, _x_barrier+steps*self.step_x-self.l_gate_x/2]
                _y = [self.Q_pos[q][1]+self.l_gate_y/4, self.Q_pos[q][1]+self.l_gate_y/4]
                self.ax.annotate("", xy=[_x[0], _y[0]], xytext=[_x[1], _y[1]],
                                 arrowprops=dict(arrowstyle="<->", lw=self.lw, shrinkA=0, shrinkB=0), annotation_clip=False)
                # if <arrow_label> in arguments write it
                if 'arrow_label' in kw:
                    _text = kw.get('arrow_label')
                    self.ax.text(np.mean(_x), _y[0]+self.l_gate_y*.1, _text, ha='center', va='bottom')
            self.ax.set_xlim(_xlim), self.ax.set_ylim(_ylim)
        # Update qubit position
        for q in qubits:
            self.Q_pos[q][0] = _x_barrier+steps*self.step_x
            self.ax.axhline(self.Q_pos[q][1], xmax=self.Q_pos[q][0]-self.step_x/2.3, color='k', lw=self.lw, ls='-', zorder=-1, clip_on=False)

    def add_repetition_barrier(self, qubit, type='open', **kw):
        '''
        Adds a repeting section note on a qubit.
        Args:
            type: "open" or "close" to open or close a repeating section.
        '''
        assert type in ['open', 'close'], 'type must be "open" or "close"!'
        # Get qubit position
        _x, _y = self.Q_pos[qubit]
        _xlim, _ylim = self.ax.get_xlim(), self.ax.get_ylim()
        if type == 'open':
            x_points = [-self.l_gate_x/2, self.l_gate_x*(-1/2+0.13), self.l_gate_x*(-1/2+0.26)]
            self._repetition_open = _x-self.l_gate_x/2
        else:
            x_points = [-self.l_gate_x/2, self.l_gate_x*(-1/2+0.13), self.l_gate_x*(-1/2+0.26)][::-1]
            # add label
            label = kw.get('label', None)
            fontsize = kw.get('fontsize', None)
            if label:
                _x_mid = (self._repetition_open+_x-self.l_gate_x/2)/2
                self.ax.text(_x_mid, _y+self.l_gate_y*(2/2), f'{label}', va='bottom', ha='center', size=fontsize)
        # plot repeating section
        color = kw.get('color', 'k')
        markersize = kw.get('markersize', 5+self.l_gate_x*2)
        self.ax.axvline(_x+x_points[0], color=color, lw=self.lw*2, clip_on=False)
        self.ax.axvline(_x+x_points[1], color=color, lw=self.lw, clip_on=False)
        self.ax.plot([_x+x_points[2], _x+x_points[2]], [_y+self.l_gate_y/7, _y-self.l_gate_y/7],
                     marker='.', ls='', color=color, clip_on=False, markersize=markersize)
        self.ax.set_xlim(_xlim), self.ax.set_ylim(_ylim)
        # Update qubit position
        self.ax.axhline(_y, xmax=self.Q_pos[qubit][0], color='k', lw=self.lw, ls='-', zorder=-1, clip_on=False)
        self.Q_pos[qubit][0] += self.step_x/2.5

    def add_square_gate(self, qubit, steps = 5, ls='-', color='C1', amplitude=1, fill_fraction=1, **kw):
        '''
        Adds a square pulse gate on a qubit.
        '''
        _x, _y = self.Q_pos[qubit]
        _X = np.linspace(_x-self.l_gate_x/2, _x+(steps-1)*self.step_x+self.l_gate_x/2, 1000)
        _Y = np.ones(len(_X))*_y-amplitude*self.l_gate_y/2
        _Y[:100], _Y[-100:] = _y, _y
        # apply gaussian filter
        from scipy.ndimage.filters import gaussian_filter1d
        gaussian_filter = kw.get('gaussian_filter', 0.01)
        _Y_s = gaussian_filter1d(_Y, gaussian_filter)
        _xlim, _ylim = self.ax.get_xlim(), self.ax.get_ylim()
        # Fill only fraction of the pulse
        fill_idx = int(1000*fill_fraction)
        mask = (1-np.heaviside(np.arange(1000)-fill_idx+1, 1))
        mask[0] = 0
        self.ax.fill_between(_X[:fill_idx], _Y_s[:fill_idx], _y, fc=to_rgba(color, .25), zorder=-1.1, clip_on=False)
        self.ax.plot(_X, _Y_s*mask+(1-mask)*_y, c=color, lw=self.lw, zorder=-1.1, ls=ls, clip_on=False)
        # Plot dashed line for unfilled fraction
        if fill_fraction != 1:
            self.ax.plot(_X, _Y_s, c=color, lw=self.lw*.9, zorder=-2.1, ls='--', clip_on=False)
        self.ax.set_xlim(_xlim), self.ax.set_ylim(_ylim)
        self.Q_pos[qubit][0] += self.step_x*steps
        self.ax.axhline(_y, xmax=self.Q_pos[qubit][0]-self.step_x/2, color='k', lw=self.lw, ls='-', zorder=-1, clip_on=False)
        # add label
        label = kw.get('label', None)
        fontsize = kw.get('fontsize', None)
        clabel = kw.get('clabel', None)
        label_pos = kw.get('label_pos', 'top')
        ylabel_correction = kw.get('ylabel_correction', 0)
        if label:
            assert label_pos in ['top', 'bottom'], '"label_pos" must be "top" or "bottom"'
            if label_pos == 'bottom':
                self.ax.text(_x+(steps-1)*self.step_x/2, _y-self.l_gate_y*(1.25/2)+ylabel_correction, f'{label}', va='top', ha='center', size=fontsize, color=clabel)
            else:
                self.ax.text(_x+(steps-1)*self.step_x/2, _y+self.l_gate_y*(1.25/2)+ylabel_correction, f'{label}', va='bottom', ha='center', size=fontsize, color=clabel)

    def add_gaussian_gate(self, qubit, steps=1, RF=True, ls='-', color='C3', amplitude=1, **kw):
        '''
        Adds a gaussian pulse gate on a qubit.
        '''
        _x, _y = self.Q_pos[qubit]
        _X = np.linspace(_x-self.l_gate_x/2, _x+(steps-1)*self.step_x+self.l_gate_x/2, 1000)
        # if RF include sinusoid
        if RF:
            _Y = (np.exp(-np.linspace(-2, 2, _X.shape[0])**2)) * self.l_gate_y/2 *np.sin(5*np.linspace(0, 2*np.pi, _X.shape[0])) + _y
        # else just envelope
        else:
            _Y = (np.exp(-np.linspace(-2, 2, _X.shape[0])**2)) * self.l_gate_y/2 + _y
        _Y[[0,-1]] = _y
        _xlim, _ylim = self.ax.get_xlim(), self.ax.get_ylim()
        # Fill only fraction of the pulse
        self.ax.fill_between(_X[:], _Y[:], _y, fc=to_rgba(color, .25), zorder=-2, clip_on=False)
        self.ax.plot(_X, _Y, c=color, lw=self.lw, zorder=-2, ls=ls, clip_on=False)
        self.ax.set_xlim(_xlim), self.ax.set_ylim(_ylim)
        self.Q_pos[qubit][0] += self.step_x*steps
        self.ax.axhline(_y, xmax=self.Q_pos[qubit][0]-self.step_x/2, color='k', lw=self.lw, ls='-', zorder=-1, clip_on=False)
        # add label
        label = kw.get('label', None)
        fontsize = kw.get('fontsize', None)
        clabel = kw.get('clabel', None)
        label_pos = kw.get('label_pos', 'top')
        ylabel_correction = kw.get('ylabel_correction', 0)
        if label:
            assert label_pos in ['top', 'bottom'], '"label_pos" must be "top" or "bottom"'
            if label_pos == 'bottom':
                self.ax.text(_x+(steps-1)*self.step_x/2, _y-self.l_gate_y*(1.25/2)+ylabel_correction, f'{label}', va='top', ha='center', size=fontsize, color=clabel)
            else:
                self.ax.text(_x+(steps-1)*self.step_x/2, _y+self.l_gate_y*(1.25/2)+ylabel_correction, f'{label}', va='bottom', ha='center', size=fontsize, color=clabel)

    def add_LRU_gate(self, qubit, steps = 1.8, echo=False, ls='-', **kw):
        '''
        '''
        _xlim, _ylim = self.ax.get_xlim(), self.ax.get_ylim()
        _x, _y = self.Q_pos[qubit]
        _X = np.linspace(_x-self.l_gate_x/2, _x+(steps-1)*self.step_x+self.l_gate_x/2, 100)
        _Y = np.ones(len(_X))*_y+self.l_gate_y/2
        _Y[:3], _Y[-3:] = _y, _y
        # add gaussian filter
        from scipy.ndimage.filters import gaussian_filter1d
        color = kw.get('color', '#26A69A')
        _Y_s = gaussian_filter1d(_Y, 1)
        self.ax.fill_between(_X, _Y_s, _y, fc='w', zorder=-1.1, ec='None', clip_on=False)
        self.ax.fill_between(_X, _Y_s, _y, fc=to_rgba(color, .25), zorder=-1.1, clip_on=False)
        self.ax.plot(_X, _Y_s, c=color, lw=self.lw*1.3, zorder=-1.1, ls=ls, clip_on=False)
        self.ax.set_xlim(_xlim), self.ax.set_ylim(_ylim)
        self.ax.axhline(_y, xmax=self.Q_pos[qubit][0]+(steps-0.5)*self.step_x, color='k', lw=self.lw, ls='-', zorder=-1, clip_on=False)
        if echo:
            assert steps%2 == 1, 'need odd number of steps for echo'
            _idle_steps = steps//2
            self.add_barrier([qubit], steps=_idle_steps)
            self.add_single_Q_gate(qubit, 'X', ax)
            self.add_barrier([qubit], steps=_idle_steps)
        else:
            self.Q_pos[qubit][0] += self.step_x*steps
        # add label
        label = kw.get('label', None)
        fontsize = kw.get('fontsize', None)
        clabel = kw.get('clabel', None)
        label_pos = kw.get('label_pos', 'top')
        ylabel_correction = kw.get('ylabel_correction', 0)
        if label:
            assert label_pos in ['top', 'bottom'], '"label_pos" must be "top" or "bottom"'
            if label_pos == 'bottom':
                self.ax.text(_x+(steps-1)*self.step_x/2, _y-self.l_gate_y*(1.25/2)+ylabel_correction, f'{label}', va='top', ha='center', size=fontsize, color=clabel)
            else:
                self.ax.text(_x+(steps-1)*self.step_x/2, _y+self.l_gate_y*(1.25/2)+ylabel_correction, f'{label}', va='bottom', ha='center', size=fontsize, color=clabel)

    def add_CZ_gate(self, qubit_1, qubit_2, x_correction=0, alpha=1, dot_size=1):
        '''
        Adds a controlled Z gate in qubits qubit_1 and qubit_2.
        '''
        _x_1, _y_1 = self.Q_pos[qubit_1]
        _x_2, _y_2 = self.Q_pos[qubit_2]
        _xlim, _ylim = self.ax.get_xlim(), self.ax.get_ylim()
        if _x_1 != _x_2:
            _x_1 = np.max([_x_1, _x_2])
            _x_2 = np.max([_x_1, _x_2])
        _patch = patches.Ellipse((_x_1+x_correction, _y_1), self.l_gate_x*.25*dot_size, self.l_gate_y*.25*dot_size,
                                   ec='None', fc='k', alpha=alpha, lw=0, zorder=1, clip_on=False)
        self.ax.add_patch(_patch)
        _patch = patches.Ellipse((_x_2+x_correction, _y_2), self.l_gate_x*.25*dot_size, self.l_gate_y*.25*dot_size,
                                   ec='None', fc='k', alpha=alpha, lw=0, zorder=1, clip_on=False)
        self.ax.add_patch(_patch)
        self.ax.plot([_x_1+x_correction, _x_2+x_correction], [_y_1, _y_2], c='k', lw=self.lw, zorder=1, alpha=alpha, clip_on=False)
        self.ax.set_xlim(_xlim), self.ax.set_ylim(_ylim)
        self.Q_pos[qubit_1][0] = _x_1+self.step_x
        self.Q_pos[qubit_2][0] = _x_2+self.step_x
        self.ax.axhline(_y_1, xmax=self.Q_pos[qubit_1][0]-self.step_x/2, color='k', lw=self.lw, ls='-', zorder=-1, clip_on=False)
        self.ax.axhline(_y_2, xmax=self.Q_pos[qubit_2][0]-self.step_x/2, color='k', lw=self.lw, ls='-', zorder=-1, clip_on=False)
         
    def add_CX_gate(self, qubit_1, qubit_2, x_correction=0, alpha=1, dot_size=1):
        '''
        Adds a controlled Z gate in qubits qubit_1 and qubit_2.
        '''
        _x_1, _y_1 = self.Q_pos[qubit_1]
        _x_2, _y_2 = self.Q_pos[qubit_2]
        _xlim, _ylim = self.ax.get_xlim(), self.ax.get_ylim()
        if _x_1 != _x_2:
            _x_1 = np.max([_x_1, _x_2])
            _x_2 = np.max([_x_1, _x_2])
        _patch = patches.Ellipse((_x_1+x_correction, _y_1), self.l_gate_x*.25*dot_size, self.l_gate_y*.25*dot_size,
                                   ec='None', fc='k', alpha=alpha, lw=0, zorder=1, clip_on=False)
        self.ax.add_patch(_patch)
        _patch = patches.Ellipse((_x_2+x_correction, _y_2), self.l_gate_x*.5*dot_size, self.l_gate_y*.5*dot_size,
                                   ec='k', fc='None', alpha=alpha, lw=self.lw, zorder=1, clip_on=False)
        self.ax.add_patch(_patch)
        self.ax.plot([_x_1+x_correction, _x_2+x_correction], [_y_1, _y_2+self.l_gate_y*.5*dot_size/2*np.sign(_y_2-_y_1)], c='k', lw=self.lw, zorder=1, alpha=alpha, clip_on=False)
        self.ax.set_xlim(_xlim), self.ax.set_ylim(_ylim)
        self.Q_pos[qubit_1][0] = _x_1+self.step_x
        self.Q_pos[qubit_2][0] = _x_2+self.step_x
        self.ax.axhline(_y_1, xmax=self.Q_pos[qubit_1][0]-self.step_x/2, color='k', lw=self.lw, ls='-', zorder=-1, clip_on=False)
        self.ax.axhline(_y_2, xmax=self.Q_pos[qubit_2][0]-self.step_x/2, color='k', lw=self.lw, ls='-', zorder=-1, clip_on=False)

    def add_multiqubit_operation(self, qubits, measurement=False, steps=2, name='', **kw):
        '''
        Add a multiqubit operation box.
        '''
        if type(qubits) is str:
            qubits = [qubits]
        elif type(qubits) is list:
            _x_list = [ self.Q_pos[q][0] for q in qubits ]
            _y_list = [ self.Q_pos[q][1] for q in qubits ]
            _y_1, _y_2 = np.max(_y_list), np.min(_y_list)
            _x = np.max(_x_list)
        _height = _y_1 - _y_2
        # gate params
        _ec = kw.get('ec', 'k')
        _ls = kw.get('ls', '-')
        if 'alpha' in kw:
            alpha = kw.get('alpha')
            _patch = patches.Rectangle((_x-(self.l_gate_x)/2, _y_2-self.l_gate_y/2), self.l_gate_x*steps, self.l_gate_y+_height,
                                       ec=_ec, fc='w', alpha=1, lw=0, zorder=1, ls=_ls, clip_on=False)
            self.ax.add_patch(_patch)
        else:
            alpha = 1
        _patch = patches.Rectangle((_x-(self.l_gate_x)/2, _y_2-self.l_gate_y/2), self.l_gate_x*steps, self.l_gate_y+_height,
                                   ec=_ec, fc='w', alpha=alpha, lw=self.lw, zorder=1, ls=_ls, clip_on=False)
        self.ax.add_patch(_patch)
        if measurement:
            _patch = patches.Arc((_x+self.l_gate_x/2, _y_2-self.l_gate_y/3), self.l_gate_x*1.15, self.l_gate_y*1.15,
                             angle=0, theta1=0.0, theta2=180, color='k', lw=self.lw, zorder=1, alpha=alpha, clip_on=False)
            self.ax.add_patch(_patch)
            head_size = kw.get('head_size', 1)
            head_length = kw.get('head_length', 1)
            _head_width, _head_length = .1*head_size, .15*head_size
            self.ax.annotate('', xy=(_x+1.8/2*self.l_gate_x/2, _y_2-self.l_gate_y/2.5), 
                        xytext=(_x+1.1*self.l_gate_x*head_length, _y_2+.9*self.l_gate_y/2.5*head_length), zorder=1,
                        arrowprops=dict(arrowstyle=f'<|-, head_width={_head_width}, head_length={_head_length}',
                        color=to_rgba('k', alpha), lw=self.lw), annotation_clip=False)
        # write gate name
        fontsize = kw.get('fontsize', None)
        self.ax.text(_x+(steps-1)*self.l_gate_x/2, (_y_1+_y_2)/2, name, va='center', ha='center', size=fontsize, alpha=alpha, color=_ec, clip_on=False)
        # add label
        label = kw.get('label', None)
        fontsize = kw.get('fontsize', None)
        clabel = kw.get('clabel', None)
        fontsize_label = kw.get('fontsize_label', None)
        ylabel_correction = kw.get('ylabel_correction', 0)
        if label:
            self.ax.text(_x+(steps-1)*self.l_gate_x/2, _y_1+self.l_gate_y*(1.25/2)+ylabel_correction, f'{label}', va='bottom', ha='center', size=fontsize_label, color=clabel)
        # Update qubit position
        for q in qubits:
            self.ax.axhline(self.Q_pos[q][1], xmax=self.Q_pos[q][0], color='k', lw=self.lw, ls='-', zorder=-1, clip_on=False)
            self.Q_pos[q][0] += self.step_x+(steps-1)*self.l_gate_x

# end