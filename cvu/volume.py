import nibabel
import numpy as np
import os

FSAVG5_XMIN=-68.7888
FSAVG5_XMAX=69.8464
FSAVG5_YMIN=-104.6920
FSAVG5_YMAX=69.1561
FSAVG5_ZMIN=-48.3923
FSAVG5_ZMAX=79.2110

LH_CORTEX_ASEGNUM=3
RH_CORTEX_ASEGNUM=42

#TODO hardcode slightly more softly
aseg_rois={ 'lh_hippocampus':53, 'rh_hippocampus':17,
			'lh_amygdala':54, 'rh_amygdala':18,
			'lh_thalamus':49, 'rh_thalamus':10,
			'lh_caudate':50, 'rh_caudate':11,
			'lh_putamen':51, 'rh_putamen':12,
			'lh_pallidum':52, 'rh_pallidum':13,
			'lh_globus_pallidus':52, 'rh_globus_pallidus':13,
			'lh_insula':55, 'rh_insula':19,
			'lh_nucleus_accumbens':58, 'rh_nucleus_accumbens':26,
			'lh_accumbens':58, 'rh_accumbens':26,
			'lh_accumbens_area':58, 'rh_accumbens_area':26,}
			#'brainstem':16, 'brain_stem':16 }

def surf_properties(use_fsavg5=True,lhsurf=None,rhsurf=None):
	if use_fsavg5:
		return (FSAVG5_XMIN,FSAVG5_YMIN,FSAVG5_ZMIN,
				FSAVG5_XMAX,FSAVG5_YMAX,FSAVG5_ZMAX)
	elif lhsurf is None or rhsurf is None:
		import cvu_utils
		raise cvu_utils.CVUError('Must use fsavg5 surface constants or provide '
			'an alternate mayavi surface to scrape dimensions')

	xs=np.vstack((lhsurf.mlab_source.x,rhsurf.mlab_source.x))
	ys=np.vstack((lhsurf.mlab_source.y,rhsurf.mlab_source.y))
	zs=np.vstack((lhsurf.mlab_source.z,rhsurf.mlab_source.z))

	xmin=np.min(xs); xmax=np.max(xs)
	ymin=np.min(ys); ymax=np.max(ys)
	zmin=np.min(zs); zmax=np.max(zs)
	return (xmin,ymin,zmin,xmax,ymax,zmax)

#the idea here is to provide a mean region location for each of the segmentation
#structures.

#First find the mean location within the volume, and then translate this
#location to surface/mayavi coordinates.

def roi_and_vol_properties(asegnum,asegd):
	roi_mean=np.mean(np.where(asegd==asegnum),axis=1)

	xc,yc,zc=np.where(np.logical_or(asegd==LH_CORTEX_ASEGNUM,
		asegd==RH_CORTEX_ASEGNUM))
	
	xmin=np.floor(np.min(xc)); xmax=np.ceil(np.max(xc))
	ymin=np.floor(np.min(yc)); ymax=np.ceil(np.max(yc))
	zmin=np.floor(np.min(zc)); zmax=np.ceil(np.max(zc))

	return roi_mean,(xmin,ymin,zmin,xmax,ymax,zmax)

def translate_coords(roi,surf_lims,cortical_vol_lims,
		orientation_swap=True):
	rx,ry,rz=roi
	xmins,ymins,zmins,xmaxs,ymaxs,zmaxs=surf_lims
	xminc,yminc,zminc,xmaxc,ymaxc,zmaxc=cortical_vol_lims

	retx=(rx-xminc)*(xmaxs-xmins)/(xmaxc-xminc)+xmins
	if orientation_swap:
		rety=(rz-zminc)*(ymaxs-ymins)/(zmaxc-zminc)+ymins
		retz=(ry-ymaxc)*(zmaxs-zmins)/(yminc-ymaxc)+zmins
		# z direction is reversed.  -1 automatically cancels out.
	else:
		rety=(ry-yminc)*(ymaxs-ymins)/(ymaxc-yminc)+ymins
		retz=(rz-zminc)*(zmaxs-zmins)/(zmaxc-zminc)+zmins

	return retx,rety,retz

def roi_coords(roi_name,asegd,subjdir=None,subject='fsavg5',lhsurf=None,rhsurf=None):
	#if subject is none, use fsavg5
	#TODO profile this code
	c=surf_properties(use_fsavg5=(subject=='fsavg5' or subject is None),
		lhsurf=lhsurf,rhsurf=rhsurf)
	r,v=roi_and_vol_properties(aseg_rois[roi_name],asegd)
	return translate_coords(r,c,v)
