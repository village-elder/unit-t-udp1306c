"""Entry point: python main.py  or  pdm run gui"""

import logging
import tkinter as tk

from gui.app import App


def main() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    for noisy in ("matplotlib", "PIL", "fontTools"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    def _tk_error(_, exc, val, tb):
        logging.getLogger("tkinter").error(
            "Unhandled callback exception", exc_info=(exc, val, tb)
        )

    tk.Tk.report_callback_exception = _tk_error

    App().mainloop()


if __name__ == "__main__":
    main()
