#!/usr/bin/env python

##############################################################################
##
# Copyright 2019 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# lnstacks is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# lnstacks is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
##############################################################################


import os
import h5py
import numpy as np
import argparse
# import joblib


class MinusLnStack():
    """"Class created with the objective to apply
    the minus Napierian logarithm on many stacks
    situated on the same folder"""

    def __init__(self):
        pass

    def minus_ln_stack(self, h5_stack_fn, tree="TomoNormalized",
                       dataset="TomoNormalized"):
        """Minus Napierian logarithm applied to a hdf5 stack of images"""

        if h5_stack_fn is None:
            raise ValueError("Input stack cannot be None")

        h5_handler = h5py.File(h5_stack_fn, "r")

        h5_outfile_fn = h5_stack_fn.rsplit('.', 1)[0] + '_ln.hdf5'
        ext = h5_stack_fn.rsplit('.', 1)[1]
        h5_outfile = h5py.File(h5_outfile_fn, 'w')

        h5_group = h5_handler[tree]
        # Main Data
        input_data_stack = h5_group[dataset]

        # Shape information of data image stack
        infoshape = input_data_stack.shape
        n_frames = infoshape[0]
        n_rows = infoshape[1]
        n_cols = infoshape[2]

        grp_ln = h5_outfile.create_group(tree)

        # ext is "h5" or
        if ext == "h5" or ext == "hdf5":
            self.copy_metadata(h5_group, grp_ln)

        # dtype maybe should be retrieved from input stack
        grp_ln.create_dataset(dataset, shape=(n_frames, n_rows, n_cols),
                              chunks=(1, n_rows, n_cols), dtype='float32')
        grp_ln[dataset].attrs['Number of Frames'] = n_frames

        for n_img in range(n_frames):
            img = input_data_stack[n_img]
            grp_ln[dataset][n_img] = -np.log(img)

        h5_handler.close()
        h5_outfile.close()
        print("Stack {} has been converted".format(h5_stack_fn))

    def copy_metadata(self, h5_group, h5_grp_ln):
        """Copy metadata to ln stack"""

        #####################
        # Retrieving Angles #
        #####################
        try:
            angles = h5_group["rotation_angle"].value
            h5_grp_ln.create_dataset("rotation_angle", data=angles)
        except:
            print("\nAngles could not be extracted.")

        #######################
        # Retrieving Energies #
        #######################
        try:
            energies = h5_group["energy"].value
            h5_grp_ln.create_dataset("energy", data=energies)
        except:
            print("\nEnergies could not be extracted.")

        #########################
        # Retrieving Pixel Size #
        #########################
        try:
            x_pixel_size = h5_group["x_pixel_size"].value
            y_pixel_size = h5_group["y_pixel_size"].value
            h5_grp_ln.create_dataset("x_pixel_size", data=x_pixel_size)
            h5_grp_ln.create_dataset("y_pixel_size", data=y_pixel_size)
        except Exception:
            print("\nPixel size could NOT be extracted.")

    def mrc_stack_minus_ln(self, stack):
        """Minus neperian logarithm applied to a hdf5 stack of images"""
        pass


def main():
    parser = argparse.ArgumentParser(
        description="Apply minus logarithm to: \n" +
                    "- A single stack \n" +
                    "- Many stacks situated in the same folder\n" +
                    "It accepts hdf5 stacks and mrc stacks")

    parser.add_argument("input", type=str, default=None,
                        help="Input one of those:\n"
                             "  - File hdf5 (or mrc) stack, \n"
                             "  - Directory containing hdf5 (or mrc) stacks")

    args = parser.parse_args()
    ln_stack = MinusLnStack()

    if os.path.isfile(args.input):
        print("Applying minus log to the given stack")
        ln_stack.minus_ln_stack(args.input)
    elif os.path.isdir(args.input):
        print("Applying minus log to the stacks in the given directory")




if __name__ == "__main__":
    main()
