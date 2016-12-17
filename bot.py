from settings import *
from twitter import *

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
    status = "hello world"
    filename = "gifs/twitter.gif"
    with open(filename, "rb") as gif:
        gifdata = gif.read()
        img_id = t_up.media.upload(media=gifdata)["media_id_string"]
        t.statuses.update(status=status, media_ids=img_id)
