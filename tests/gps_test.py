
import matplotlib.pyplot as plt
import time
import sys

from gps import GPS


def main():

    plt.ion()
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))

    gps = GPS()

    start_time = time.time()

    times = []
    lat = []
    long = []

    # Set up the plots
    ax1.set_title("Latitude vs Time")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Latitude")
    lat_line, = ax1.plot([], [], '-o')

    ax2.set_title("Longitude vs Time")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Longitude")
    long_line, = ax2.plot([], [], '-o')

    ax3.set_title("Latitude vs Longitude")
    ax3.set_xlabel("Longitude")
    ax3.set_ylabel("Latitude")
    ax3.grid(True)

    while True:
        gps.update()

        current_time = time.time() - start_time
        useful, coord = gps.get_latlong()

        if useful:
            lat.append(coord[0])
            long.append(coord[1])
            times.append(current_time)

            lat_line.set_data(times, lat)
            long_line.set_data(times, long)

            ax1.set_xlim(0, max(times) + 1)
            ax1.set_ylim(min(lat) - 0.01, max(lat) + 0.01)

            ax2.set_xlim(0, max(times) + 1)
            ax2.set_ylim(min(long) - 0.01, max(long) + 0.01)

            ax3.scatter(long, lat, color='blue')
        else:
            print("Incorrect GPS data")

        plt.pause(0.1)

if __name__ == "__main__":
    main()


