import pandas as pd
import numpy as np

def gradient_strength(no3, sigma, depth, from_depth, layer_thickness=20):
    """
    Calculate gradient ratio between no3 and sigma
    over depth range [from_depth, from_depth+layer_thickness].
    """
    nc_depth_range = (from_depth<=depth) & (depth<=from_depth+layer_thickness)
    if len(no3)==0 or not np.any(nc_depth_range):
        return np.nan
    else:
        try:
            def slope(x, y, x_range):
                return np.polyfit(x.loc[x_range], y.loc[x_range].sort_values(), 1)[0]

            no3_grad = slope(depth, no3, nc_depth_range)
            sigma_grad = slope(depth, sigma, nc_depth_range)

            return no3_grad/sigma_grad
        except:
            return np.nan

def find_nitracline0(no3, depth, no3_crit=1.0):
    """
    Fix!!
    """
    index = np.where(no3 >= no3_crit)[0]
    if len(index)>0:
        return depth.iloc[index[0]].astype(float)
    else:
        return np.nan

def find_nitracline(no3, depth, delta_no3_crit=1.0):
    no3sfc = no3.loc[depth<=10].mean()
    index = np.where(no3>no3sfc + delta_no3_crit)[0]
    if len(index)>0:
        return depth.iloc[index[0]].astype(float)
    else:
        # criterion applies nowhere
        return np.nan

def find_ml (sigth, depth, delta_sigth_crit=0.1):
    index = np.where(sigth>np.nanmean(sigth.iloc[:5]) + delta_sigth_crit)[0]
    if len(index)>0:
        return depth.iloc[index[0]].astype(float)
    else:
        return np.nan

def find_isolume(par, par_level=0.415):
    condition = par<=par_level
    if any(condition):
        return par.loc[condition].index[0]
    else:
        return np.nan

def find_Zeu (par_ratio, crit_ratio=0.01):
    condition = par_ratio<0.01
    if any(condition):
        return par_ratio.loc[condition].index[0]
    else:
        return np.nan

def find_Kd (par):
    raise NotImplementedError('sort out indices etc')
    par=par.loc[10:50]
    par=par.dropna()
    if len(par)>0:
        p = np.polyfit(x=par.index,y=np.log(par),deg=1)
        return -p[0]
    else:
        return np.nan

def find_heps(eps,depth):
    index = np.where((eps.values<5e-9) & (depth>5))[0]
    if len(index)>0:
        return depth.iloc[index[0]],eps.iloc[index[0]] # increase by 1 because of zero-based indexing
    else:
        return np.nan,np.nan

def average_layer(c, depth, from_depth, layer_thickness=30):
    """
    Average quantity c between no3 and sigma
    over depth range [from_depth, from_depth+layer_thickness].
    """
    nc_depth_range = (from_depth<=depth) & (depth<=from_depth+layer_thickness)
    if len(c)==0 or not np.any(nc_depth_range):
        return np.nan
    else:
        return c.loc[nc_depth_range].mean()
