#!/usr/bin/env python3

"""
The main entry point for the application.
"""

import logging
from project import control

# Setting up logging
logging.basicConfig(
    filename='main.log',
    filemode='w',
    format='%(name)s - %(levelname)s - %(message)s'
)


def main():
    """ The main function to instantiate and run the application controller. """

    controller = control.ApplicationController()
    controller.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logging.exception("caught at main")
        raise error  # personal choice, still want to see error in IDE
