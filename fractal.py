import numpy as np
import scipy.misc as smp
from random import getrandbits

class FractalAutomaton:

    def __init__(self, depth, k):
        self._grid_sizes = [2**i for i in range(depth)]
        grid = [np.random.rand(N, N) for N in self._grid_sizes]
        self.neighbors = [np.zeros((N, N)) for N in self._grid_sizes]

        # initialize the grid with density k
        for i in range(depth):
            np.place(grid[i], grid[i] > 1-k, 1)
            np.place(grid[i], grid[i] <= 1-k, 0)
        self.grid = grid
        self.depth = depth
        self.rule_array = [5, 7, 8, 10, 11, 12]
        self.update()

    def update(self):
        for d in range(1, self.depth):
            # local grid
            gl = self.grid[d]
            N = self._grid_sizes[d]

            # sum the neighbors in the local grid
            Zl = np.lib.pad(gl, 1, 'wrap')
            nbrs = np.zeros((N,N))
            nbrs += (sum(np.roll(np.roll(Zl, i, 0), j, 1)
                     for i in (-1, 0, 1) for j in (-1, 0, 1))
                     - Zl)[1:-1, 1:-1]
            #nbrs += (Zl[:-2,:-2] + Zl[0:-2,1:-1] + Zl[:-2,2:] +
            #         Zl[1:-1,:-2] + Zl[1:-1,2:] +
            #         Zl[2:,:-2] + Zl[2:,1:-1] + Zl[2:,2:])

            # add the parent neighbors
            gp = self.grid[d-1]
            Zp = np.lib.pad(gp, 1, 'wrap')
            pnbrs = sum(np.roll(np.roll(Zp, i, 0), j, 1)
                        for i in (1, 0) for j in (1, 0))
            for i in range(N):
                for j in range(N):
                    nbrs[i,j] = pnbrs[i/2 + i%2, j/2 + j%2]

            # add the child neighbors
            if d + 1 < self.depth:
                gc = self.grid[d+1]
                Zc = gc.reshape((N, 2, N, 2)).sum(-1).sum(1)
                nbrs += Zc

            gl = np.in1d(nbrs.ravel(), self.rule_array).reshape(
                         nbrs.shape).astype(int)
            

    def save_frame(self, filename=None, size=(1000,1000)):
        if not filename:
            filename = 'fractal_%s.png' % getrandbits(16)
        data = smp.imresize(self.grid[depth-1], size, interp='nearest')
        return smp.imsave(filename, data)


if __name__=='__main__':
    depth = 8
    N = 10
    f = FractalAutomaton(depth, 0.2)
    for _ in range(N):
        f.save_frame()
        f.update()
