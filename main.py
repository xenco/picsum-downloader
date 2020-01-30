import os
import random
import threading
import requests
import shutil
import sys
import time


def build_queue():
    q = []
    for _ in range(num_images):
        width, height = get_random_size()
        file_name = "%s_%s_%s.jpg" % (width, height, time.time())
        q.append({
            "src": "https://picsum.photos/%s/%s.jpg" % (width, height),
            "dst": "%s/%s" % (target_dir, file_name)
        })
    return q


def get_args():
    if len(sys.argv) < 3:
        print("Call with following format:\n%s [num_images] [target_dir]" % sys.argv[0])
        exit(1)

    num_images = sys.argv[1]
    try:
        num_images = int(num_images)
    except:
        print("Please provide the number of images as an integer")
        exit(1)

    target_dir = sys.argv[2]
    if not (os.path.exists(target_dir) and os.path.isdir(target_dir) and os.access(target_dir,
                                                                                   os.F_OK & os.R_OK & os.W_OK)):
        print("Dir does not exist or is not writeable\n%s created" % target_dir)
        os.makedirs(target_dir)

    return num_images, target_dir


def get_random_size():
    return random.randint(1, 10) * 100, random.randint(1, 10) * 100


def download_image(src, target):
    r = requests.get(src, stream=True)
    if r.status_code == 200 and r.raw:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, open(target, "wb"))
        return True
    else:
        print("Error %s: Downloading from %s" % (r.status_code, src))
        return False


def worker(data):
    for d in data:
        download_image(d["src"], d["dst"])
    return


num_images, target_dir = get_args()
queue = build_queue()

max_threads = 10
num_per_thread = max(1, int(len(queue) / max_threads))

threads = []

while len(queue) > 0:
    for i in range(max_threads):
        if len(queue) == 0:
            break

        data, queue = queue[:num_per_thread], queue[num_per_thread:]
        t = threading.Thread(target=worker, args=(data,))
        threads.append(t)
        t.start()

for t in threads:
    t.join()

print("Finished")
