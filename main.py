import argparse
import logging

from analysis import analize
from omtool.datamodel import Config
from creator import create
from integration import integrate
from manual_analysis import manual_analize

if __name__ == '__main__':
    logging.basicConfig(
        level = logging.INFO, 
        format = '[%(levelname)s] %(asctime)s | %(message)s', 
        datefmt = '%H:%M:%S'
    )

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'mode', 
        help = 'Mode of the program to run', 
        choices = ['create', 'integrate', 'analize', 'mananalize', 'test'])
    parser.add_argument(
        'inputparams',
        help = 'input parameters for particular mode (for example, path to config file)',
        nargs = argparse.REMAINDER
    )

    args = parser.parse_args()

    if args.mode == 'create':
        create(Config.from_yaml(args.inputparams[0]))
    elif args.mode == 'integrate':
        integrate(Config.from_yaml(args.inputparams[0]))
    elif args.mode == 'analize':
        analize(Config.from_yaml(args.inputparams[0]))
    elif args.mode == 'mananalize':
        manual_analize()
