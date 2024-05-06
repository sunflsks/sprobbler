    TODOS:
    - add a way to manually trigger a refresh
    - add capability for gunicorn to read port from config file (right now it is hardcoded into supervisord.conf)
    - despaghettify
    - switch to postgres and use a view instead of querying within server every single time
    - track_id AND name must both be available concurrently in all contexts
