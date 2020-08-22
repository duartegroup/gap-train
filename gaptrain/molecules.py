import autode as ade
from autode.input_output import xyz_file_to_atoms
from autode.atoms import Atom
from gaptrain.log import logger
from scipy.spatial.distance import cdist
from scipy.spatial import distance_matrix
import numpy as np


class Species(ade.species.Species):

    def in_box(self, box):
        """Is this molecule totally inside a box with an origin at
        (0,0,0) and top right corner (a, b, c) = box.size

        :param box: (gaptrain.box.Box)
        """
        coords = self.get_coordinates()

        if np.min(coords) < 0.0:
            return False

        # Maximum x, y, z component of all atoms should be < a, b, c
        # respectively
        if max(np.max(coords, axis=0) - box.size) > 0:
            return False

        return True

    def min_distance(self, coords):
        """Calculate the minimum distance from this molecule to a set
        of coordinates

        :param coords: (np.ndarray) shape = (n, 3)
        """
        # Infinite distance to the other set if there are no coordinates
        if len(coords) == 0:
            return np.inf

        return np.min(cdist(coords, self.get_coordinates()))

    def centroid(self):
        """
        Get the centroid of this molecule

        :return: (np.ndarray) shape = (3,)
        """
        return np.average(self.get_coordinates(), axis=0)

    def calculate_radius(self, with_vdw=False):
        """
        Calculate the radius of this species as half the maximum distance
        between two atoms

        :param with_vdw: (bool) Add the van der Walls radius to the two
                         most distant atoms

        :return: (float) Radius in Å
        """
        if with_vdw:
            raise NotImplementedError

        # No radius for a single atom
        if self.n_atoms == 1:
            return 0.0

        coords = self.get_coordinates()
        max_distance = np.max(distance_matrix(coords, coords))

        return max_distance / 2.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.radius = self.calculate_radius()


class Molecule(Species):

    def __init__(self,  xyz_filename,  charge=0, spin_multiplicity=1,
                 gmx_itp_filename=None):
        """Molecule e.g. H2O

        -----------------------------------------------------------------------
        :param xyz_filename: (str)

        :param charge: (int)

        :param spin_multiplicity: (int)

        :param gmx_itp_filename: (str) Filename(path) of the GROMACS .itp file
                                 containing MM parameters required to simulate
        """
        super().__init__(name='mol',
                         charge=charge,
                         mult=spin_multiplicity,
                         atoms=xyz_file_to_atoms(xyz_filename))

        self.itp_filename = gmx_itp_filename

        logger.info(f'Initialised {xyz_filename.rstrip(".xyz")}\n'
                    f'Number of atoms      = {self.n_atoms}\n'
                    f'GROMACS itp filename = {self.itp_filename}')


class Ion(Species):

    def __init__(self, label, charge, spin_multiplicity=1,
                 gmx_itp_filename=None):
        """Ion

        -----------------------------------------------------------------------
        :param label: (str) e.g. 'Pd'

        :param charge: (int)

        :param spin_multiplicity: (int)
        """
        super().__init__(name=label,
                         charge=charge,
                         mult=spin_multiplicity,
                         atoms=[Atom(label)])

        self.itp_filename = gmx_itp_filename
