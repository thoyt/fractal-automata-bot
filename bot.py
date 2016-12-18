import os
from random import randint

from twitter import *

from settings import *
from fractal import FractalAutomaton

def get_clients():
    auth = OAuth(MY_ACCESS_TOKEN_KEY,
                 MY_ACCESS_TOKEN_SECRET,
                 MY_CONSUMER_KEY,
                 MY_CONSUMER_SECRET,
                 )
    t = Twitter(auth=auth)
    t_up = Twitter(domain='upload.twitter.com', auth=auth)
    return t, t_up

if __name__=='__main__':
    t, t_up = get_clients()

    depth = randint(8,11)
    k = 0.0001
    min_frames = 50
    clean = True

    f = FractalAutomaton(depth, k, setup=False)
    f.set_random_rule()
    i_fr = 0
    while i_fr < min_frames and k < 0.6:
        f.setup(k)
        filename, i_fr = f.run(min_frames, clean=clean)
        status = "rule = %s, k = %s" % (f.rule, k)
        k *= 1.2

    if filename is not None:
        with open(filename, "rb") as gif:
            gifdata = gif.read()
            img_id = t_up.media.upload(media=gifdata)["media_id_string"]
            t.statuses.update(status=status, media_ids=img_id)

        os.remove(filename)
