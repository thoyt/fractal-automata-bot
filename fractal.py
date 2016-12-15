import os
import glob

import imageio
import numpy as np
import scipy.misc as smp
from natsort import natsorted
from random import getrandbits, random


class FractalAutomaton:

    P_SUM_PARENTS = 0.5
    P_SUM_LOCAL = 0.8
    P_SUM_CHILDREN = 0.5

    def __init__(self, depth, k, setup=True):
        self.depth = depth
        self._grid_sizes = [2**i for i in range(depth)]
        if setup:
            self.setup(k)
        self.rule = {
            'array': [5, 7, 8, 10, 11, 12],
            'sum_parents': True,
            'sum_local': True,
            'sum_children': True
            }

    def setup(self, k):
        grid = np.array([np.random.rand(N, N) for N in self._grid_sizes])

        # initialize the grid with density k
        for i in range(depth):
            np.place(grid[i], grid[i] > 1-k, 1)
            np.place(grid[i], grid[i] <= 1-k, 0)
        self.grid = grid
        self.id = getrandbits(16)
        self.k = k
        self.frame = 0

    def set_random_rule(self, k=0.3):
        rule = {}
        rule['sum_parents'] = random() < self.P_SUM_PARENTS
        rule['sum_local'] = random() < self.P_SUM_LOCAL
        rule['sum_children'] = random() < self.P_SUM_CHILDREN
        max_neighbors = 0
        if rule['sum_parents']:
            max_neighbors += 4
        if rule['sum_local']:
            max_neighbors += 8
        if rule['sum_children']:
            max_neighbors += 4

        if max_neighbors == 0:
            rule['sum_local'] = True
            max_neighbors = 8

        array = []
        for n in range(max_neighbors):
            if random() < k:
                array.append(n)
        rule['array'] = array
        print rule
        self.rule = rule

    def update(self):
        new_grid = self.grid.copy()
        for d in range(1, self.depth):
            # local grid
            gl = self.grid[d]
            N = self._grid_sizes[d]
            nbrs = np.zeros((N,N))

            if self.rule['sum_local']:
                # sum the neighbors in the local grid
                Zl = np.lib.pad(gl, 1, 'wrap')
                nbrs += (sum(np.roll(np.roll(Zl, i, 0), j, 1)
                     for i in (-1, 0, 1) for j in (-1, 0, 1))
                    )[1:-1, 1:-1]

            if self.rule['sum_parents']:
                # add the parent neighbors
                gp = self.grid[d-1].copy()
                Zp = np.lib.pad(gp, 1, 'wrap')
                pnbrs = sum(np.roll(np.roll(Zp, i, 0), j, 1)
                            for i in (1, 0) for j in (1, 0))
                for i in range(N):
                    for j in range(N):
                        nbrs[i,j] += pnbrs[i/2 + i%2, j/2 + j%2]

            if self.rule['sum_children']:
                # add the child neighbors
                if d + 1 < self.depth:
                    gc = self.grid[d+1]
                    Zc = gc.reshape((N, 2, N, 2)).sum(-1).sum(1)
                    nbrs += Zc

            new_grid[d] = np.in1d(nbrs.ravel(), self.rule['array']).reshape(
                         nbrs.shape).astype(int)

        self.grid = new_grid

    def save_frame(self, id=1, filename=None, size=(1000,1000)):
        if not filename:
            filename = 'frames/fractal_%s_frame_%s.png' % (self.id, self.frame)
        data = smp.imresize(self.grid[depth-1], size, interp='nearest')
        self.frame += 1
        return smp.imsave(filename, data)

    def render_gif(self):
        pattern = 'frames/fractal_%s_*.png' % self.id
        filenames = natsorted(glob.glob(pattern))
        images = []
        for filename in filenames:
            images.append(imageio.imread(filename))
        imageio.mimsave('gifs/fractal_%s_%s.gif' % (self.id, self.k), images)

    def run(self, max_frames=100, save_gif=False, threshold=0.7,
            set_random_rule=False):
        thr = threshold * self._grid_sizes[-1] ** 2
        for i_fr in range(max_frames):
            self.update()
            self.save_frame()
            if (i_fr > 5 and
                (len(np.where(self.grid[-1] == 1)[0]) > thr or
                 np.all(self.grid[-1] == 0))):
                break
        if save_gif and i_fr > 10:
            self.render_gif()

        rule = "array: (%s) sum_parents: %s, sum_local: %s, sum_children: %s" % (
                ','.join(map(str, self.rule['array'])), self.rule['sum_parents'],
                self.rule['sum_local'], self.rule['sum_children'])

        print "fractal %s done at frame %s with rule %s" % (self.id, i_fr, rule)
        return i_fr


if __name__=='__main__':
    depth = 10
    dk = 0.05

    f = FractalAutomaton(depth, k, setup=False)
    while True:
        f.set_random_rule()
        k = 0.01
        while k < 0.6 or i_fr < 99:
            f.setup(k) 
            i_fr = f.run(save_gif=True)
            k += dk
