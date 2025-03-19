
import matplotlib.pyplot as plt
import time
import sys

from gps import GPS


def main():

    plt.ion()
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))

    gps = GPS()
    gps.open_port()
    gps.update_data()

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
        gps.update_data()
        

        current_time = time.time() - start_time
        coord = gps.get_data()

        if coord[0]:
            lat.append(coord[0])
            long.append(coord[1])
            times.append(current_time)

            lat_line.set_data(times, lat)
            long_line.set_data(times, long)

            ax1.set_xlim(0, max(times) + 1)
            ax1.set_ylim(min(lats) - 0.01, max(lats) + 0.01)

            ax2.set_xlim(0, max(times) + 1)
            ax2.set_ylim(min(longs) - 0.01, max(longs) + 0.01)

            ax3.scatter(long, lat, color='blue')
        else:
            print("Incorrect GPS data")

        plt.pause(0.1)

if __name__ == "__main__":
    main()


