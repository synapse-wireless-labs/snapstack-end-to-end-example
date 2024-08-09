from time import sleep

import tornado


def rgb_request(r, g, b):
    return tornado.httpclient.HTTPRequest(
        "http://localhost:8888/bridge/rgb",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=tornado.escape.json_encode({"r": r, "g": g, "b": b}),
    )


client = tornado.httpclient.HTTPClient()

try:
    response = client.fetch("http://localhost:8888/bridge/rgb")
    print(response.body)

    for color in range(8):
        r = (color >> 2) & 1
        g = (color >> 1) & 1
        b = color & 1

        print(f"{color}: {r}, {g}, {b}")

        response = client.fetch(rgb_request(r, g, b))
        print(response.body)
        sleep(1)

except Exception as e:
    print(f"Error: {e}")

client.close()
