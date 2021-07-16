# =========================== fgmodel/targetSG ==========================
"""
 @class    fgmodel.targetSG

 @brief    Interfaces for the target detection module 
            based on the single Gaussian RGB color modeling


 The target pixels are assumed to have similar RGB value, and is modeled as a
 single Guassian distribution.  It then transform the
 distribution into a Gaussian with uncorrelated components by
 diagonalizing the covariance matrix. The fg detection is done by
 thresholding each component independently in the transformed color space(tilt):
       |color_tilt_i - mu_tilt_i| < tau * cov_tilt_i, for all i=1,2,3
 tau can be user-input

 The interface is adapted from the fgmodel/targetNeon.
"""
# =========================== fgmodel/targetSG ==========================
"""
 @file     targetSG.m

 @author  Yiye Chen,       yychen2019@gatech.edu
 @date     2021/02/28 [Matlab version]
           2021/07/15 [Python version]

 @classf   fgmodel
"""
# =========================== fgmodel/targetSG ==========================

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from roipoly import RoiPoly

from detector.fgmodel.appearance import appearance


class tModel_SG():
    """
    The target model class storing the statistics of the target color
    """
    def __init__(self):
        self.mu = None
        self.sig = None
        self.sigEignVec = None
        self.sigEignVal = None

        self.has_Eign = False

    def getSigEign(self):
        self.has_Eign = True
        return None
    

class targetSG(appearance):
    """
    The single-Gaussian based target detection class.
    The target color is modeled as a single-Guassian distribution
    """
    def __init__(self, tModel=None):
        # sanity check 
        if tModel is not None:
            assert isinstance(tModel, tModel_SG), \
                "The targetSG class requires a target model of the type tModel_SG. Now getting the type: {}".format(type(tModel))

        super().__init__(tModel, None)
        self.foo = None
    
    def measure(self, I):
        self.fgIm = np.ones_like(I, dtype=np.bool)
        return None

    def saveMod(self, filename):
        return None
    
    def loadMod(self, filename):
        return None

    @staticmethod
    def _calibSimple():
        """
        calibrate the target model given a set of target pixels 
        """
        return None
    
    @staticmethod
    def buildSimple():
        """
        Return a targetSG detector instance given a set of target pixels
        """
        return None
    
    @staticmethod
    def _calibFromImage(img, nPoly=1, fh=None, *args, **kwargs):
        """
        @brief  Calibrate the foreground model given an image sequence
             with target elements within it.

        Runs a user-guided foregound selection interface to capture and learn
        the target color. The reader element should have only the frames
        to process and no more.  Recover a classification model based on
        user-specified regions from the image frames.

        This method is **user-interactive**; it will display figures and
        request user selection of image regions.

        The output variables are structures with the results of the estimation
        process for the target model. The fields are as follows:
    
        mData (dict)
          pix     - (2, N) pixel locations/values collected for training
          data    - (3, N) source image data at the locations.
   
    
        @param[input]     imseq   The reader instance with image frames to process.
        @param[input]     nPoly   (Optional) The number of polygons per image
                                  Default = 1 (if argument missing/empty matrix).
        @param[input]     fh      Figure to use if given (new figure otherwise).
    
        @param[output]    tModel  The trained target model.
        @param[output]    mData   The training pixel locations and color data.
        """
        if fh is None:
            fh = plt.figure()
            newFig = True
        else:
            newFig = False

        fh.suptitle('LEFT-CLICK TO SELECT POLYGON VERTICES THEN RIGHT-CLICK '
                  ' OR DOUBLE CLICK TO SELECT FINAL VERTICE, FOR EACH POLYGON')
        ax = fh.add_subplot(1,1,1) # assume only one image will be display
        ax.imshow(img)
        plt.show(block=False)

        print('\n\n***INSTRUCTIONS***  Use LEFT-CLICK to select a series of polygon '
              'vertices; use RIGHT-CLICK or DOUBLE-CLICKto select the final vertex of each polygon. \n')
        print(f'\t\t\tDo this to define {nPoly} polygons containing pixels you would like ' 
              'to color match.\n\n\n')

        pix = np.array([])
        dat = np.array([])

        # collect training pixels from each user-defined polygon
        for jj in range(nPoly):
            roi = RoiPoly(color='r', fig=fh)
            b = roi.get_mask(img[:, :, 0])
            vals = img.reshape(-1, img.shape[2])
            vals = vals[b.reshape(-1) == 1, :]

            # TODO: in the Matlab version and targetNeon, the pix are populated in the same way of dat
            # But it should collect the pixel coordinates according to the function comment
            # Do the coordinates for now 
            rowIds, colIds = np.where(b == 1) # this and np.ndarray.reshape are all column-first
            pix_this = np.vstack((rowIds, colIds)) 
            if pix.size == 0:
                pix = pix_this 
            else:
                pix = np.concatenate((pix, pix_this), axis=1)

            if dat.size == 0:
                dat = vals.T
            else:
                dat = np.concatenate((dat, vals.T), axis=1)


        mData = {
            "pix": pix,
            "data": dat 
        }

        tModel = tModel_SG()
        return tModel, mData

    @staticmethod 
    def buildFromImage(img, *args, **kwargs):
        """
        @brief  Instantiate a single-Gaussian color target model from image selections

        @param[in]  img                 The image to be calibrated on
        @param[in]  nPoly(optional)     The number of polygon target areas planning to draw. Default is 1
        @param[in]  fh(optional)        The figure handle for displaying the image to draw ROI
        """

        # if kwargs contains nPoly or fh, they will automatically be parsed out
        tModel, mData = targetSG._calibFromImage(img, *args, **kwargs)
        det = targetSG(tModel)
        return det 
