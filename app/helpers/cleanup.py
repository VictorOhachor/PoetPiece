import threading
import time
from flask import current_app

# Use a dictionary to track processed POST requests and their timestamps
failed_posts = {}

# Lock for thread-safe operations on failed_posts
lock = threading.Lock()

# Define the cleanup interval (in seconds)
CLEANUP_INTERVAL = 3600


def cleanup_failed_posts():
    with lock:
        current_time = time.time()
        # Remove entries older than CLEANUP_INTERVAL seconds
        keys_to_remove = [key for key, timestamp in failed_posts 
                          if current_time - timestamp > CLEANUP_INTERVAL]
        for key in keys_to_remove:
            del failed_posts[key]


def start_cleanup_thread():
    while True:
        time.sleep(CLEANUP_INTERVAL)
        print(f'cleaning processed POST requests after {CLEANUP_INTERVAL} seconds...')
        cleanup_failed_posts()


# Start the cleanup thread as a daemon
cleanup_thread = threading.Thread(target=start_cleanup_thread)
cleanup_thread.setDaemon(True)
cleanup_thread.start()


@current_app.before_request
def perform_cleanup():
    cleanup_failed_posts()
