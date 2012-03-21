import sys
import pprint
import subprocess
import os

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import prepfold
import psr_utils

import candidate
import utils
from rating_classes import subint_stats

def main():
    pfdfn = sys.argv[1]

    pfd = prepfold.pfd(pfdfn)

    cand = candidate.Candidate(pfd.topo_p1, pfd.bary_p1, pfd.bestdm, \
                        psr_utils.ra_to_rad(pfd.rastr)*psr_utils.RADTODEG, \
                        psr_utils.dec_to_rad(pfd.decstr)*psr_utils.RADTODEG, \
                        pfdfn)

    print "Loaded %s" % cand.pfdfn
    print "    Best topo period (s): %f" % cand.topo_period
    print "    Best bary period (s): %f" % cand.bary_period
    print "    Best DM (cm^-3/pc): %f" % cand.dm
    print "    RA (J2000 - deg): %f" % cand.raj_deg
    print "    Dec (J2000 - deg): %f" % cand.decj_deg

    print "-"*10
    pprint.pprint(cand.__dict__)
    print "-"*10

    intstats.add_data(cand)

    print "Added subint stats to cand"
    pprint.pprint(cand.__dict__)
    print "-"*10

    print "Subint stats object:"
    pprint.pprint(cand.subint_stats.__dict__)
    print "-"*10

    print "Sub-int Stats:"
    print "On-fraction (area): %g" % cand.subint_stats.get_on_frac()
    print "On-fraction (peak): %g" % cand.subint_stats.get_peak_on_frac()
    print "Area SNR stddev: %g" % cand.subint_stats.get_snr_stddev()
    print "Peak SNR stddev: %g" % cand.subint_stats.get_peak_snr_stddev()
    print "Avg correlation coefficient: %g" % cand.subint_stats.get_avg_corrcoef()
    
    sgauss = cand.singlegaussfit
    tvph = cand.time_vs_phase
    onpulse_phs = sgauss.get_onpulse_region()
    onpulse_bin = np.round(onpulse_phs*tvph.nbin).astype(int)
    prof = utils.get_scaled_profile(cand.profile, cand.pfd.varprof)
    imax = plt.axes([0.1,0.1,0.5,0.7])
    plt.imshow(scale2d(tvph.data), interpolation='nearest', \
            aspect='auto', origin='lower', cmap=matplotlib.cm.gist_yarg)
    if onpulse_bin[0] < onpulse_bin[1]:
        plt.axvspan(onpulse_bin[0], onpulse_bin[1]+1, fc='g', alpha=0.2, lw=0)
    else:
        plt.axvspan(onpulse_bin[0], tvph.nbin, fc='g', alpha=0.2, lw=0)
        plt.axvspan(-0.5, onpulse_bin[1]+1, fc='g', alpha=0.2, lw=0)
        

    plt.axes([0.1,0.8,0.5,0.15], sharex=imax)
    plt.plot(prof, 'k-', label='Profile')
    plt.plot(sgauss.make_gaussians(len(prof)), 'r--', label='Fit')
    if onpulse_bin[0] < onpulse_bin[1]:
        plt.axvspan(onpulse_bin[0], onpulse_bin[1]+1, fc='g', alpha=0.2, lw=0, label='On-pulse')
    else:
        plt.axvspan(onpulse_bin[0], tvph.nbin, fc='g', alpha=0.2, lw=0, label='On-pulse')
        plt.axvspan(-0.5, onpulse_bin[1]+1, fc='g', alpha=0.2, lw=0, label='_nolabel_')
    plt.legend(loc='best', prop=dict(size='xx-small'))
    
    plt.axes([0.6,0.1,0.15,0.7], sharey=imax)
    snrs = cand.subint_stats.snrs
    plt.plot(snrs, np.arange(len(snrs)), 'mo', label='SNR (area)')
    plt.axvline(5.0, c='m', ls='--', lw=2)
    peaksnrs = cand.subint_stats.peak_snrs
    plt.plot(peaksnrs, np.arange(len(peaksnrs)), 'cD', label='SNR (peak)')
    plt.axvline(3.0, c='c', ls='--', lw=2)
    plt.legend(loc='best', prop=dict(size='xx-small'))
   
    plt.axes([0.75,0.1,0.15,0.7], sharey=imax)
    corrcoefs = cand.subint_stats.corr_coefs
    plt.plot(corrcoefs, np.arange(len(corrcoefs)), 'k.')
    imax.set_xlim(-0.5,tvph.nbin-0.5)
    imax.set_ylim(-0.5,tvph.nsubint-0.5)
    plt.show()


def scale2d(array2d, indep=False):
    """Scale a 2D array for plotting.
        Subtract min from each row.
        Divide by global max (if indep==False)
        or divide by max of each row (if indep==True)
    """
    # Min of each row
    min = np.outer(array2d.min(axis=1), np.ones(array2d.shape[1]))
    if indep==False:
        # Global maximum
        max = array2d.max()
    else:
        # maximum for each row
        max = np.outer(array2d.max(axis=1), np.ones(array2d.shape[1]))
    return (array2d - min)/max


if __name__=='__main__':
    intstats = subint_stats.SubintPulseWindowStats()
    main()

