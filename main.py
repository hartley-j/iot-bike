
import argparse

from camsystem import camsystem


def init_argparse():
    """
    Parses command line arguments
    :return: parser
    :rtype: argparse.parser object
    """
    parser = argparse.ArgumentParser(
        usage="%(prog)s [options] ",
        description="Detect objects using opencv."
    )

    parser.add_argument(
        "-p", "--pi", action="store_true",
        help="If raspi is being used"
    )

    parser.add_argument(
        "-f", "--file", action="store",
        help="Select an image file or directory to be detected",
        default=None
    )

    parser.add_argument(
        "-w", "--webcam", action="store_true",
        help="Use live webcam"
    )

    parser.add_argument(
        "-i", "--index", action="store",
        help="Select webcam index",
        default=0
    )

    parser.add_argument(
        "-c", "--capture", action="store_true",
        help="Take picture from webcam"
    )
    
    parser.add_argument(
        "-t", "--tracker", action="store_true",
        help="Use DEEP SORT algorithm for tracking"
    )

    parser.add_argument(
        "-d", "--display", action="store_true",
        help="Display detections (only works with gui)"
    )

    return parser


def main():
    """
    Main function. Runs either detect_images or use_webcam depending on the argument given in cli
    """
    # f = pyfiglet.figlet_format("Trac OS", font="slant")
    # print(f)

    parser = init_argparse()
    args = parser.parse_args()

    if args.file:
        camsystem.detect_images(args.file)
    elif args.webcam and not args.tracker:
        camsystem.use_webcam_live(args.index, args.pi, args.display)
    elif args.capture:
        camsystem.use_webcam_pic(args.index)
    elif args.webcam and args.tracker:
        camsystem.track_from_webcam(args.index)


if __name__ == "__main__":
    main()
