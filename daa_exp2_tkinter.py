"""DAA Experiment 2: String-matching algorithm comparison GUI."""

import random
import time
import tkinter as tk
from tkinter import messagebox, ttk


def naive_search(text, pattern):
    matches, comparisons = [], 0
    for start in range(len(text) - len(pattern) + 1):
        for offset in range(len(pattern)):
            comparisons += 1
            if text[start + offset] != pattern[offset]:
                break
        else:
            matches.append(start)
    return matches, comparisons


def compute_lps(pattern):
    lps = [0] * len(pattern)
    length = 0
    index = 1
    while index < len(pattern):
        if pattern[index] == pattern[length]:
            length += 1
            lps[index] = length
            index += 1
        elif length:
            length = lps[length - 1]
        else:
            index += 1
    return lps


def kmp_search(text, pattern):
    lps = compute_lps(pattern)
    matches, comparisons = [], 0
    text_index = pattern_index = 0
    while text_index < len(text):
        comparisons += 1
        if text[text_index] == pattern[pattern_index]:
            text_index += 1
            pattern_index += 1
        if pattern_index == len(pattern):
            matches.append(text_index - pattern_index)
            pattern_index = lps[pattern_index - 1]
        elif text_index < len(text) and text[text_index] != pattern[pattern_index]:
            pattern_index = lps[pattern_index - 1] if pattern_index else 0
            if pattern_index == 0 and text[text_index] != pattern[0]:
                text_index += 1
    return matches, comparisons


def rabin_karp(text, pattern, modulus=101):
    alphabet_size = 256
    pattern_length = len(pattern)
    high_order = pow(alphabet_size, pattern_length - 1, modulus)
    pattern_hash = text_hash = 0
    matches, comparisons = [], 0
    for index in range(pattern_length):
        pattern_hash = (alphabet_size * pattern_hash + ord(pattern[index])) % modulus
        text_hash = (alphabet_size * text_hash + ord(text[index])) % modulus
    for start in range(len(text) - pattern_length + 1):
        if pattern_hash == text_hash:
            for offset in range(pattern_length):
                comparisons += 1
                if text[start + offset] != pattern[offset]:
                    break
            else:
                matches.append(start)
        if start < len(text) - pattern_length:
            text_hash = (alphabet_size * (text_hash - ord(text[start]) * high_order) + ord(text[start + pattern_length])) % modulus
    return matches, comparisons


class StringMatchingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("String Matching Algorithm Comparison")
        self.geometry("820x575")
        self.minsize(720, 520)
        frame = ttk.Frame(self, padding=18)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(5, weight=1)

        ttk.Label(frame, text="String Matching Algorithm Comparison", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 14))
        ttk.Label(frame, text="Text:").grid(row=1, column=0, sticky="nw", pady=5)
        self.text_entry = tk.Text(frame, height=4, wrap="word", font=("Segoe UI", 10))
        self.text_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=5)
        self.text_entry.insert("1.0", "AABAACAADAABAABA")
        ttk.Label(frame, text="Pattern:").grid(row=2, column=0, sticky="w", pady=5)
        self.pattern_entry = ttk.Entry(frame)
        self.pattern_entry.grid(row=2, column=1, columnspan=2, sticky="ew", pady=5)
        self.pattern_entry.insert(0, "AABA")

        controls = ttk.Frame(frame)
        controls.grid(row=3, column=0, columnspan=3, sticky="w", pady=14)
        ttk.Button(controls, text="Find Matches", command=self.run_searches).pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Run Performance Analysis", command=self.performance_analysis).pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Clear Results", command=self.clear_results).pack(side="left")
        ttk.Label(frame, text="Results:", font=("Segoe UI", 11, "bold")).grid(row=4, column=0, sticky="w")
        self.results = tk.Text(frame, wrap="word", font=("Consolas", 10))
        self.results.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(5, 0))

    def write(self, line):
        self.results.insert("end", line + "\n")
        self.results.see("end")

    def clear_results(self):
        self.results.delete("1.0", "end")

    def get_input(self):
        text = self.text_entry.get("1.0", "end-1c")
        pattern = self.pattern_entry.get()
        if not text:
            raise ValueError("Enter text to search.")
        if not pattern:
            raise ValueError("Enter a pattern to search for.")
        if len(pattern) > len(text):
            raise ValueError("The pattern cannot be longer than the text.")
        return text, pattern

    def run_searches(self):
        try:
            text, pattern = self.get_input()
        except ValueError as error:
            messagebox.showerror("Invalid input", str(error))
            return
        self.clear_results()
        self.write(f"Text:    {text}")
        self.write(f"Pattern: {pattern}\n")
        for name, algorithm in (("Naive Search", naive_search), ("KMP Search", kmp_search), ("Rabin-Karp", rabin_karp)):
            start = time.perf_counter()
            matches, comparisons = algorithm(text, pattern)
            elapsed = (time.perf_counter() - start) * 1000
            displayed_matches = matches if matches else "No matches"
            self.write(f"{name:<14} Matches: {displayed_matches} | Comparisons: {comparisons} | Time: {elapsed:.5f} ms")

    def performance_analysis(self):
        text = "".join(random.choices("ABCD", k=10000))
        patterns = ("AB", "ABCD", "ABCDAB", "ABCDABCD")
        self.clear_results()
        self.write("Performance analysis: random text of 10,000 characters\n")
        self.write(f"{'Pattern':<14} {'Naive':>12} {'KMP':>12} {'Rabin-Karp':>14}")
        self.write("-" * 58)
        for pattern in patterns:
            _, naive_count = naive_search(text, pattern)
            _, kmp_count = kmp_search(text, pattern)
            _, rk_count = rabin_karp(text, pattern)
            self.write(f"{pattern:<14} {naive_count:>12} {kmp_count:>12} {rk_count:>14}")
            self.update_idletasks()


if __name__ == "__main__":
    StringMatchingApp().mainloop()
