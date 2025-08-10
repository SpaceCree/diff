import os
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox

from diff_utils import load_text_from_file, build_dual_highlighted_html, generate_html_report


class DiffApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Сравнение документов → HTML отчет")
        self.root.geometry("720x260")

        self.file_a: str | None = None
        self.file_b: str | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        pad = 8

        frm = tk.Frame(self.root)
        frm.pack(fill=tk.BOTH, expand=True, padx=pad, pady=pad)

        # Row A
        row_a = tk.Frame(frm)
        row_a.pack(fill=tk.X, pady=(0, pad))
        tk.Label(row_a, text="Документ A:").pack(side=tk.LEFT)
        self.var_a = tk.StringVar()
        ent_a = tk.Entry(row_a, textvariable=self.var_a)
        ent_a.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(pad, pad))
        tk.Button(row_a, text="Обзор...", command=self._choose_a).pack(side=tk.RIGHT)

        # Row B
        row_b = tk.Frame(frm)
        row_b.pack(fill=tk.X, pady=(0, pad))
        tk.Label(row_b, text="Документ B:").pack(side=tk.LEFT)
        self.var_b = tk.StringVar()
        ent_b = tk.Entry(row_b, textvariable=self.var_b)
        ent_b.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(pad, pad))
        tk.Button(row_b, text="Обзор...", command=self._choose_b).pack(side=tk.RIGHT)

        # Actions
        actions = tk.Frame(frm)
        actions.pack(fill=tk.X, pady=(pad, 0))
        tk.Button(actions, text="Сгенерировать HTML отчет", command=self._generate).pack(side=tk.LEFT)
        tk.Button(actions, text="Выход", command=self.root.quit).pack(side=tk.RIGHT)

        hint = tk.Label(frm, fg="#6b7280", text="Поддерживаются файлы .txt и .docx (текст извлекается из параграфов)")
        hint.pack(anchor=tk.W, pady=(pad, 0))

    def _choose_a(self) -> None:
        path = filedialog.askopenfilename(
            title="Выберите Документ A",
            filetypes=[("Text", "*.txt"), ("Word", "*.docx"), ("All files", "*.*")],
        )
        if path:
            self.file_a = path
            self.var_a.set(path)

    def _choose_b(self) -> None:
        path = filedialog.askopenfilename(
            title="Выберите Документ B",
            filetypes=[("Text", "*.txt"), ("Word", "*.docx"), ("All files", "*.*")],
        )
        if path:
            self.file_b = path
            self.var_b.set(path)

    def _generate(self) -> None:
        if not self.file_a or not self.file_b:
            messagebox.showwarning("Недостаточно данных", "Пожалуйста, выберите оба файла.")
            return
        try:
            text_a = load_text_from_file(self.file_a)
            text_b = load_text_from_file(self.file_b)

            html_a, html_b = build_dual_highlighted_html(text_a, text_b)
            report_html = generate_html_report(os.path.basename(self.file_a), os.path.basename(self.file_b), html_a, html_b)

            save_path = filedialog.asksaveasfilename(
                title="Сохранить отчет как...",
                defaultextension=".html",
                filetypes=[("HTML", "*.html")],
                initialfile="diff_report.html",
            )
            if not save_path:
                return
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(report_html)

            messagebox.showinfo("Готово", f"Отчет сохранен: {save_path}")
            try:
                webbrowser.open(f"file://{save_path}")
            except Exception:
                pass
        except Exception as exc:
            messagebox.showerror("Ошибка", str(exc))


def main() -> None:
    root = tk.Tk()
    app = DiffApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
