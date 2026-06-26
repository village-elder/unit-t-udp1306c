"""Data log panel: scrollable treeview + Clear / Export to CSV."""

import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable

from i18n import Translator
from poller import Sample

_COL_IDS = ("col_no", "col_dt", "col_volt", "col_amp", "col_watt", "col_flag")
_COL_WIDTHS = (45, 155, 90, 90, 90, 55)


class DataLogPanel(ttk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        t: Translator,
        *,
        on_clear: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self._t = t
        self._on_clear = on_clear
        self._rows: list[tuple] = []
        self._i18n: list[Callable] = []
        self._build()

    def _build(self) -> None:
        self._lf = tk.LabelFrame(self, text=self._t("data_record"))
        self._lf.pack(fill="x", padx=6, pady=(0, 6))
        self._i18n.append(lambda d, w=self._lf: w.config(text=d["data_record"]))

        tb = tk.Frame(self._lf)
        tb.pack(fill="x", padx=4, pady=2)

        btn_clr = tk.Button(tb, text=self._t("clear"), command=self._clear)
        btn_clr.pack(side="left", padx=2)
        self._i18n.append(lambda d, w=btn_clr: w.config(text=d["clear"]))

        btn_exp = tk.Button(tb, text=self._t("export"), command=self._export)
        btn_exp.pack(side="left", padx=2)
        self._i18n.append(lambda d, w=btn_exp: w.config(text=d["export"]))

        self._tree = ttk.Treeview(self._lf, columns=_COL_IDS, show="headings", height=5)
        for cid, w in zip(_COL_IDS, _COL_WIDTHS):
            self._tree.heading(cid, text=self._t(cid))
            self._tree.column(cid, width=w, anchor="center")
            self._i18n.append(
                lambda d, tree=self._tree, c=cid: tree.heading(c, text=d[c])
            )

        vsb = ttk.Scrollbar(self._lf, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="x", expand=True, padx=(4, 0), pady=(0, 4))
        vsb.pack(side="left", fill="y", pady=(0, 4))

    def add_sample(self, sample: Sample) -> None:
        n = len(self._rows) + 1
        row = (
            n,
            sample.ts.strftime("%Y-%m-%d %H:%M:%S"),
            f"{sample.voltage:.2f}",
            f"{sample.current:.3f}",
            f"{sample.power:.1f}",
            sample.mode,
        )
        self._rows.append(row)
        self._tree.insert("", "end", values=row)
        self._tree.yview_moveto(1.0)

    def _clear(self) -> None:
        self._tree.delete(*self._tree.get_children())
        self._rows.clear()
        if self._on_clear:
            self._on_clear()

    def _export(self) -> None:
        if not self._rows:
            messagebox.showinfo("", self._t("no_data"))
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as fp:
            w = csv.writer(fp)
            w.writerow([self._t(k) for k in _COL_IDS])
            w.writerows(self._rows)
        messagebox.showinfo(
            "", self._t("saved_rows").format(n=len(self._rows), path=path)
        )

    def apply_lang(self, strings: dict) -> None:
        for fn in self._i18n:
            fn(strings)
