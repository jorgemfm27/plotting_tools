# plotting_tools

A small matplotlib helper library for publication-style figures, with a focus on
quantum-computing plots: matrices, colormapped lines, SI-aware axis labels, and
hand-drawn-style quantum circuit diagrams.

## Installation

Clone and install in editable mode:

```bash
git clone https://github.com/jorgemfm27/plotting_tools.git
cd plotting_tools
pip install -e .
```

Requires `numpy` and `matplotlib` (plus `scipy`, used by one smoothing path in
`Quantum_circuit.add_repetition_barrier`).

## Usage

```python
import plotting_tools as pt
```

### Plotting primitives

| Function | Purpose |
| --- | --- |
| `plot_matrix` | Heatmap of a 2D array with optional colorbar, log norm, and per-cell numbers |
| `plot_line_cmap` | Draw a line in a single colormap color, picked by a 0–1 percentage |
| `plot_line_with_cmap` | Draw a line whose color varies along its length |
| `plot_stiched_data` | Stitch several X/Y/data segments into one continuous 2D plot |
| `plot_squiggly_line` | Sine-wiggle connector between two points |
| `plot_polygon_patch` | Polygon patch with rounded corners |
| `plot_arrow` | Curved arrow with independent head and tail widths |

### Axis and figure helpers

| Function | Purpose |
| --- | --- |
| `SI_prefix_and_scale_factor` | Pick the SI prefix and scale factor for a value |
| `quantity_to_string` | Format a value (optionally ± error) with SI units |
| `set_xlabel` / `set_ylabel` | Axis labels with automatic SI prefixing of ticks |
| `set_cbarlabel` | Same, for a colorbar |
| `set_aspect_ratio_lim` | Set axis limits to a target aspect ratio |
| `move_subplot` | Shift and rescale an axes' position in figure coordinates |
| `get_cbar` | Create a colorbar at an explicit position and size |
| `get_fig` | Thin `plt.subplots` wrapper |
| `savefig` | Save a figure at 300 dpi with a tight bounding box |

### Quantum circuit diagrams

`Quantum_circuit` builds circuit figures by adding elements to a qubit register:

```python
qc = pt.Quantum_circuit(Qubits=['D1', 'A1', 'D2'])
qc.add_initial_state('D1', r'$|0\rangle$')
qc.add_single_Q_gate('D1', name='H')
qc.add_CZ_gate('D1', 'A1')
qc.add_measurement('A1')
```

Available elements: `add_initial_state`, `add_single_Q_gate`, `add_measurement`,
`add_barrier`, `add_repetition_barrier`, `add_square_gate`, `add_gaussian_gate`,
`add_LRU_gate`, `add_CZ_gate`, `add_CX_gate`, and `add_multiqubit_operation`.

## License

No license specified — all rights reserved by default.
