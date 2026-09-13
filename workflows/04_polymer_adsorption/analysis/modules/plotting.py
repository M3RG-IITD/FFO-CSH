"""
Module 5: Publication-Quality Plotting

Generates multi-panel Figure 5 for the manuscript.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from matplotlib import rcParams, font_manager as fm
# ===== Font setup (Arial for Nature-style) =====
arial_path = "arial.ttf"
arial_prop = fm.FontProperties(fname=arial_path)
rcParams['font.family'] = arial_prop.get_name()
fm.fontManager.addfont(arial_path)


# Color scheme
COLORS = {
    '1:1': '#E64B35',   # Red
    '2:1': '#F39B7F',   # Orange
    '3:1': '#4DBBD5',   # Blue
}

CE_ORDER = ['1:1', '2:1', '3:1']


def setup_style():
    """Set publication-quality matplotlib defaults."""
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica'],
        'font.size': 8,
        'axes.labelsize': 9,
        'axes.titlesize': 10,
        'xtick.labelsize': 7,
        'ytick.labelsize': 7,
        'legend.fontsize': 7,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'axes.linewidth': 0.8,
        'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
    })


def plot_rg_comparison(rg_summaries, ax):
    """Panel (b): Rg, Rg_parallel, Rg_perp comparison."""
    available = [ce for ce in CE_ORDER if ce in rg_summaries]
    if not available:
        ax.text(0.5, 0.5, 'No Rg data', transform=ax.transAxes, ha='center')
        return
    
    x = np.arange(len(available))
    width = 0.25
    
    rg_total = [rg_summaries[ce]['Rg_mean'] for ce in available]
    rg_par = [rg_summaries[ce]['Rg_parallel_mean'] for ce in available]
    rg_perp = [rg_summaries[ce]['Rg_perp_mean'] for ce in available]
    
    ax.bar(x - width, rg_total, width, label='$R_g$ (total)', color='gray', edgecolor='black', lw=0.5)
    ax.bar(x, rg_par, width, label='$R_{g,\\parallel}$ (in-plane)', color='steelblue', edgecolor='black', lw=0.5)
    ax.bar(x + width, rg_perp, width, label='$R_{g,\\perp}$ (out-of-plane)', color='indianred', edgecolor='black', lw=0.5)
    
    ax.set_xticks(x)
    ax.set_xticklabels([f'C:E = {ce}' for ce in CE_ORDER])
    ax.set_ylabel('$R_g$ (Å)')
    ax.legend(loc='upper right', frameon=False)
    ax.set_title('(b) Polymer conformation')


def plot_flattening(rg_summaries_s1, rg_summaries_s2, ax):
    """Panel showing flattening index: bulk vs adsorbed."""
    x = np.arange(len(CE_ORDER))
    width = 0.3
    
    f_bulk = [rg_summaries_s2[ce]['F_index_mean'] for ce in CE_ORDER]
    f_ads = [rg_summaries_s1[ce]['F_index_mean'] for ce in CE_ORDER]
    
    ax.bar(x - width/2, f_bulk, width, label='Bulk solution', color='lightgray', edgecolor='black', lw=0.5)
    ax.bar(x + width/2, f_ads, width, label='Adsorbed', color='steelblue', edgecolor='black', lw=0.5)
    
    ax.set_xticks(x)
    ax.set_xticklabels([f'{ce}' for ce in CE_ORDER])
    ax.set_xlabel('C:E ratio')
    ax.set_ylabel('Flattening index $F = R_{g,\\parallel}/R_{g,\\perp}$')
    ax.legend(frameon=False)
    ax.set_title('Flattening upon adsorption')


def plot_coverage(coverage_summaries, ax):
    """Panel (c): Surface coverage vs C:E ratio."""
    available = [ce for ce in CE_ORDER if ce in coverage_summaries]
    if not available:
        ax.text(0.5, 0.5, 'No coverage data', transform=ax.transAxes, ha='center')
        return
    x_pos = np.arange(len(available))
    
    means = [coverage_summaries[ce]['coverage_grid_mean'] for ce in available]
    stds = [coverage_summaries[ce]['coverage_grid_std'] for ce in available]
    
    ax.bar(x_pos, means, yerr=stds, color=[COLORS[ce] for ce in available],
           edgecolor='black', lw=0.5, capsize=3)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(available)
    ax.set_xlabel('C:E ratio')
    ax.set_ylabel('Surface coverage (%)')
    ax.set_title('(c) Surface coverage')


def plot_adsorption_energy(energy_summaries, ax):
    """Panel (d): Adsorption energy violin/bar plot."""
    available = [ce for ce in CE_ORDER if ce in energy_summaries]
    if not available:
        ax.text(0.5, 0.5, 'No energy data', transform=ax.transAxes, ha='center')
        return
    x_pos = np.arange(len(available))
    
    means = [energy_summaries[ce]['E_ads'] for ce in available]
    errs = [energy_summaries[ce]['E_ads_err'] for ce in available]
    
    bars = ax.bar(x_pos, means, yerr=errs,
                  color=[COLORS[ce] for ce in CE_ORDER],
                  edgecolor='black', lw=0.5, capsize=3)
    
    # Add value labels
    for i, (m, e) in enumerate(zip(means, errs)):
        ax.text(i, m - abs(m)*0.15, f'{m:.0f}\n±{e:.0f}',
                ha='center', va='top', fontsize=7)
    
    ax.axhline(0, color='black', lw=0.5, ls='--')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(CE_ORDER)
    ax.set_xlabel('C:E ratio')
    ax.set_ylabel('$E_{ads}$ (kcal/mol)')
    ax.set_title('(d) Adsorption energy')


def plot_density_profile(density_profiles, csh_types, ax):
    """Panel (f-left): Number density profiles."""
    for component, (z, rho) in density_profiles.items():
        styles = {
            'polymer': ('Polymer', '-', 'purple'),
            'water_O': ('Water O', '--', 'blue'),
            'Ca': ('Ca$^{2+}$', '-', 'green'),
            'COO': ('COO$^-$', ':', 'red'),
        }
        if component in styles:
            label, ls, color = styles[component]
            ax.plot(z, rho, ls=ls, color=color, label=label, lw=1.0)
    
    ax.set_xlabel('Distance from surface, z (Å)')
    ax.set_ylabel('Number density (Å$^{-3}$)')
    ax.legend(frameon=False, fontsize=6)
    ax.set_title('(f) Density profiles')


def plot_rdf(rdf_data, ax):
    """Panel (f-right): Ca-COO RDF for different C:E ratios."""
    for ce in CE_ORDER:
        if ce in rdf_data:
            r, gr = rdf_data[ce]
            ax.plot(r, gr, color=COLORS[ce], label=f'C:E = {ce}', lw=1.0)
    
    ax.set_xlabel('r (Å)')
    ax.set_ylabel('g(r)')
    ax.legend(frameon=False)
    ax.set_title('Ca–COO$^-$ radial distribution')


def plot_contacts(contact_summaries, ax):
    """Panel: Contact number vs C:E ratio."""
    available = [ce for ce in CE_ORDER if ce in contact_summaries]
    if not available:
        ax.text(0.5, 0.5, 'No contact data', transform=ax.transAxes, ha='center')
        return
    x_pos = np.arange(len(available))
    
    means = [contact_summaries[ce]['contacts_mean'] for ce in available]
    stds = [contact_summaries[ce]['contacts_std'] for ce in available]
    
    ax.bar(x_pos, means, yerr=stds, color=[COLORS[ce] for ce in available],
           edgecolor='black', lw=0.5, capsize=3)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(available)
    ax.set_xlabel('C:E ratio')
    ax.set_ylabel('Ca–COO$^-$ contacts')
    ax.set_title('(e) Contact statistics')


def plot_height(height_summaries, ax):
    """Panel: Polymer height above surface."""
    available = [ce for ce in CE_ORDER if ce in height_summaries]
    if not available:
        ax.text(0.5, 0.5, 'No height data', transform=ax.transAxes, ha='center')
        return
    x_pos = np.arange(len(available))
    
    means = [height_summaries[ce]['height_mean'] for ce in available]
    stds = [height_summaries[ce]['height_std'] for ce in available]
    
    ax.bar(x_pos, means, yerr=stds, color=[COLORS[ce] for ce in available],
           edgecolor='black', lw=0.5, capsize=3)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(available)
    ax.set_xlabel('C:E ratio')
    ax.set_ylabel('Height above surface (Å)')
    ax.set_title('Polymer COM height')


def assemble_figure5(all_results, output_path="figures/figure5.pdf"):
    """
    Assemble the complete multi-panel Figure 5.
    
    all_results should be a dict with keys:
      rg_s1, rg_s2, coverage, energy, contacts, density, rdf, height
    """
    setup_style()
    
    fig = plt.figure(figsize=(14, 12))
    gs = gridspec.GridSpec(3, 4, hspace=0.4, wspace=0.35)
    
    # Row 1: Rg comparison (adsorbed), flattening, coverage
    ax_rg = fig.add_subplot(gs[0, 0:2])
    plot_rg_comparison(all_results.get('rg_s1', {}), ax_rg)
    
    ax_flat = fig.add_subplot(gs[0, 2])
    if 'rg_s1' in all_results and 'rg_s2' in all_results:
        plot_flattening(all_results['rg_s1'], all_results['rg_s2'], ax_flat)
    
    ax_cov = fig.add_subplot(gs[0, 3])
    if 'coverage' in all_results:
        plot_coverage(all_results['coverage'], ax_cov)
    
    # Row 2: E_ads, contacts, density profile, RDF
    ax_eads = fig.add_subplot(gs[1, 0])
    if 'energy' in all_results:
        plot_adsorption_energy(all_results['energy'], ax_eads)
    
    ax_contacts = fig.add_subplot(gs[1, 1])
    if 'contacts' in all_results:
        plot_contacts(all_results['contacts'], ax_contacts)
    
    ax_density = fig.add_subplot(gs[1, 2])
    if 'density' in all_results:
        # Use one representative system for density
        first_ce = list(all_results['density'].keys())[0]
        plot_density_profile(all_results['density'][first_ce], None, ax_density)
    
    ax_rdf = fig.add_subplot(gs[1, 3])
    if 'rdf' in all_results:
        plot_rdf(all_results['rdf'], ax_rdf)
    
    # Row 3: Height, orientation, E_ads time series
    ax_height = fig.add_subplot(gs[2, 0])
    if 'height' in all_results:
        plot_height(all_results['height'], ax_height)
    
    # E_ads time series for all C:E
    ax_eads_ts = fig.add_subplot(gs[2, 1:3])
    if 'energy' in all_results:
        for ce in CE_ORDER:
            if ce in all_results['energy'] and 'E_ads_series' in all_results['energy'][ce]:
                series = all_results['energy'][ce]['E_ads_series']
                # Running average
                window = min(200, len(series)//5)
                if window > 1:
                    running = np.convolve(series, np.ones(window)/window, mode='valid')
                    ax_eads_ts.plot(running, color=COLORS[ce], label=f'{ce}', lw=0.8)
        ax_eads_ts.axhline(0, color='black', lw=0.5, ls='--')
        ax_eads_ts.set_xlabel('Frame')
        ax_eads_ts.set_ylabel('$E_{ads}$ (kcal/mol)')
        ax_eads_ts.legend(frameon=False)
        ax_eads_ts.set_title('$E_{ads}$ time series')
    
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    print(f"\n  Figure saved to {output_path}")
    plt.close()
