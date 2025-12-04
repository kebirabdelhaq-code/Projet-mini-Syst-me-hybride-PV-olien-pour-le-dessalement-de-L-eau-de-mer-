import math
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

PUISSANCE_PV_WP_DEFAUT = 245.0
PUISSANCE_EO_W_DEFAUT = 850000.0
PRIX_PANNEAU_EUR = 345.0
PRIX_EOLIENNE_EUR = 95000

CONSOMMATION_PROCEDES = {
    "RO (Osmose inverse)": 3.5,
    "MED": 15.0,
    "MSF": 22.0
}

def dimensionnement_scenario(
    eau_m3_j,
    procede,
    fraction_pv,
    puissance_pv_wp,
    puissance_eo_w,
    h_sun,
    h_wind,
    prix_panneau,
    prix_eolienne
):
    e_m3 = CONSOMMATION_PROCEDES[procede]
    e_totale = eau_m3_j * e_m3
    e_pv = e_totale * fraction_pv
    e_eo = e_totale * (1.0 - fraction_pv)
    e_par_panneau = puissance_pv_wp * h_sun / 1000.0
    e_par_eolienne = puissance_eo_w * h_wind
    n_pv = math.ceil(e_pv / e_par_panneau) if e_pv > 0 else 0
    n_eo = math.ceil(e_eo / e_par_eolienne) if e_eo > 0 else 0
    cout_pv = n_pv * prix_panneau
    cout_eo = n_eo * prix_eolienne
    cout_total = cout_pv + cout_eo
    return {
        "fraction_pv": fraction_pv,
        "e_totale": e_totale,
        "e_pv": e_pv,
        "e_eo": e_eo,
        "n_pv": n_pv,
        "n_eo": n_eo,
        "e_par_panneau": e_par_panneau,
        "e_par_eolienne": e_par_eolienne,
        "cout_total": cout_total,
        "cout_pv": cout_pv,
        "cout_eo": cout_eo
    }

class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Projet mini – Système hybride PV–Éolien pour le dessalement de L'eau de mer ")
        self.root.geometry("1100x780")

        self.mode_systeme = tk.StringVar(value="defaut")
        self.procede_var = tk.StringVar(value="RO (Osmose inverse)")
        self.eau_var = tk.DoubleVar(value=100.0)
        self.puissance_pv_wp = tk.DoubleVar(value=PUISSANCE_PV_WP_DEFAUT)
        self.puissance_eo_w = tk.DoubleVar(value=PUISSANCE_EO_W_DEFAUT)
        self.h_sun_var = tk.DoubleVar(value=5.0)
        self.h_wind_var = tk.DoubleVar(value=8.0)
        self.prix_pv_var = tk.DoubleVar(value=PRIX_PANNEAU_EUR)
        self.prix_eo_var = tk.DoubleVar(value=PRIX_EOLIENNE_EUR)

        self.scenarios = []

        self._build_ui()

    def _build_ui(self):
        titre = tk.Label(
            self.root,
            text="💧 Dimensionnement d’un système hybride PV–Éolien pour le dessalement de L'eau de mer 💧",
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        titre.pack(fill="x", pady=5)

        frame_entrees = ttk.LabelFrame(self.root, text="Paramètres d’entrée", padding=10)
        frame_entrees.pack(fill="x", padx=15, pady=10)

        ttk.Label(frame_entrees, text="Données du système :").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(
            frame_entrees, text="Système par défaut (Yingli 245 W, Gamesa 850 W)",
            variable=self.mode_systeme, value="defaut",
            command=self._maj_mode
        ).grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ttk.Radiobutton(
            frame_entrees, text="Système personnalisé",
            variable=self.mode_systeme, value="perso",
            command=self._maj_mode
        ).grid(row=0, column=2, sticky="w", padx=5, pady=2)

        ttk.Label(frame_entrees, text="Puissance d’un module PV (Wc) :").grid(row=1, column=0, sticky="w", pady=3)
        self.ent_puiss_pv = ttk.Entry(frame_entrees, textvariable=self.puissance_pv_wp, width=10)
        self.ent_puiss_pv.grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(frame_entrees, text="Puissance d’une éolienne (W) :").grid(row=2, column=0, sticky="w", pady=3)
        self.ent_puiss_eo = ttk.Entry(frame_entrees, textvariable=self.puissance_eo_w, width=10)
        self.ent_puiss_eo.grid(row=2, column=1, sticky="w", padx=5)

        ttk.Label(frame_entrees, text="Heures solaires équivalentes (h/j) :").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Entry(frame_entrees, textvariable=self.h_sun_var, width=10).grid(row=3, column=1, sticky="w", padx=5)

        ttk.Label(frame_entrees, text="Heures de vent équivalentes (h/j) :").grid(row=4, column=0, sticky="w", pady=3)
        ttk.Entry(frame_entrees, textvariable=self.h_wind_var, width=10).grid(row=4, column=1, sticky="w", padx=5)

        ttk.Label(frame_entrees, text="Procédé de dessalement :").grid(row=1, column=2, sticky="w", pady=3)
        combo_proc = ttk.Combobox(
            frame_entrees,
            textvariable=self.procede_var,
            values=list(CONSOMMATION_PROCEDES.keys()),
            state="readonly",
            width=22
        )
        combo_proc.grid(row=1, column=3, padx=5, sticky="w")

        ttk.Label(frame_entrees, text="Débit d’eau à dessaler (m³/jour) :").grid(row=2, column=2, sticky="w", pady=3)
        ttk.Entry(frame_entrees, textvariable=self.eau_var, width=12).grid(row=2, column=3, sticky="w", padx=5)

        ttk.Label(frame_entrees, text="Prix d’un module PV (€) :").grid(row=3, column=2, sticky="w", pady=3)
        ttk.Entry(frame_entrees, textvariable=self.prix_pv_var, width=12).grid(row=3, column=3, sticky="w", padx=5)

        ttk.Label(frame_entrees, text="Prix d’une éolienne (€) :").grid(row=4, column=2, sticky="w", pady=3)
        ttk.Entry(frame_entrees, textvariable=self.prix_eo_var, width=12).grid(row=4, column=3, sticky="w", padx=5)

        frame_btn = tk.Frame(self.root)
        frame_btn.pack(pady=5)

        btn_calc = ttk.Button(frame_btn, text="Lancer le calcul des scénarios", command=self.calculer_scenarios)
        btn_calc.pack(side="left", padx=10)

        btn_plots = ttk.Button(frame_btn, text="Afficher les courbes horaires", command=self.afficher_courbes)
        btn_plots.pack(side="left", padx=10)

        frame_res = ttk.LabelFrame(self.root, text="Résultats et scénarios", padding=10)
        frame_res.pack(fill="both", expand=True, padx=15, pady=(5, 5))

        self.txt_res = tk.Text(frame_res, height=10, wrap="word")
        self.txt_res.pack(fill="both", expand=True)

        frame_opt = ttk.LabelFrame(self.root, text="Scénario optimal – Production horaire", padding=10)
        frame_opt.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.fig_opt, self.ax_opt = plt.subplots(figsize=(6, 3))
        self.canvas_opt = FigureCanvasTkAgg(self.fig_opt, master=frame_opt)
        self.canvas_opt.get_tk_widget().pack(fill="both", expand=True)

        self._maj_mode()

    def _maj_mode(self):
        if self.mode_systeme.get() == "defaut":
            self.puissance_pv_wp.set(PUISSANCE_PV_WP_DEFAUT)
            self.puissance_eo_w.set(PUISSANCE_EO_W_DEFAUT)
            self.ent_puiss_pv.config(state="disabled")
            self.ent_puiss_eo.config(state="disabled")
        else:
            self.ent_puiss_pv.config(state="normal")
            self.ent_puiss_eo.config(state="normal")

    def calculer_scenarios(self):
        try:
            eau = float(self.eau_var.get())
            h_sun = float(self.h_sun_var.get())
            h_wind = float(self.h_wind_var.get())
            puiss_pv = float(self.puissance_pv_wp.get())
            puiss_eo = float(self.puissance_eo_w.get())
            prix_pv = float(self.prix_pv_var.get())
            prix_eo = float(self.prix_eo_var.get())
            procede = self.procede_var.get()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez vérifier les valeurs numériques.")
            return

        if eau <= 0 or h_sun <= 0 or h_wind <= 0 or puiss_pv <= 0 or puiss_eo <= 0:
            messagebox.showerror("Erreur", "Toutes les valeurs doivent être positives.")
            return

        fractions = [1.0, 0.0, 0.5, 0.7, 0.3]
        self.scenarios = []

        for f in fractions:
            sc = dimensionnement_scenario(
                eau_m3_j=eau,
                procede=procede,
                fraction_pv=f,
                puissance_pv_wp=puiss_pv,
                puissance_eo_w=puiss_eo,
                h_sun=h_sun,
                h_wind=h_wind,
                prix_panneau=prix_pv,
                prix_eolienne=prix_eo
            )
            self.scenarios.append(sc)

        scenario_opt = min(self.scenarios, key=lambda s: s["cout_total"])

        sc_5050 = next((s for s in self.scenarios if abs(s["fraction_pv"] - 0.5) < 1e-6), None)
        sc_7030 = next((s for s in self.scenarios if abs(s["fraction_pv"] - 0.7) < 1e-6), None)
        sc_3070 = next((s for s in self.scenarios if abs(s["fraction_pv"] - 0.3) < 1e-6), None)

        candidats = [scenario_opt]
        if sc_5050 is not None:
            candidats.append(sc_5050)
        if sc_7030 is not None:
            candidats.append(sc_7030)
        if sc_3070 is not None:
            candidats.append(sc_3070)

        scenario_opt = min(candidats, key=lambda s: s["cout_total"])


        self.txt_res.delete("1.0", tk.END)
        self.txt_res.insert(tk.END, f"Procédé : {procede}\n")
        self.txt_res.insert(tk.END, f"Débit d'eau dessalée : {eau:.1f} m³/jour\n")
        self.txt_res.insert(tk.END, f"Heures solaires équivalentes : {h_sun:.1f} h/j\n")
        self.txt_res.insert(tk.END, f"Heures de vent équivalentes : {h_wind:.1f} h/j\n")
        self.txt_res.insert(tk.END, "-"*60 + "\n\n")

        for sc in self.scenarios:
            part_pv = int(sc["fraction_pv"] * 100)
            part_eo = 100 - part_pv
            self.txt_res.insert(tk.END, f"Scénario {part_pv}% PV / {part_eo}% Éolien\n")
            self.txt_res.insert(tk.END, f"  Énergie totale requise : {sc['e_totale']:.1f} kWh/j\n")
            self.txt_res.insert(tk.END, f"  Énergie PV : {sc['e_pv']:.1f} kWh/j -> {sc['n_pv']} panneaux\n")
            self.txt_res.insert(tk.END, f"  Énergie Éolien : {sc['e_eo']:.1f} kWh/j -> {sc['n_eo']} éoliennes\n")
            self.txt_res.insert(tk.END, f"  Coût PV estimé : {sc['cout_pv']:.0f} €\n")
            self.txt_res.insert(tk.END, f"  Coût Éolien estimé : {sc['cout_eo']:.0f} €\n")
            self.txt_res.insert(tk.END, f"  Coût total estimé : {sc['cout_total']:.0f} €\n")
            self.txt_res.insert(tk.END, "-"*50 + "\n")

        self.txt_res.insert(tk.END, "\n>>> Scénario optimal (coût minimal) :\n")
        part_pv_opt = int(scenario_opt["fraction_pv"] * 100)
        part_eo_opt = 100 - part_pv_opt
        self.txt_res.insert(
            tk.END,
            f"    {part_pv_opt}% PV / {part_eo_opt}% Éolien, "
            f"Coût total ≈ {scenario_opt['cout_total']:.0f} €\n"
        )

        heures, solaire_opt, eolien_opt, total_opt = self._courbes_horaires_pour_scenario(scenario_opt)
        self.ax_opt.clear()
        self.ax_opt.plot(heures, solaire_opt, label="Solaire (W)", color="orange")
        self.ax_opt.plot(heures, eolien_opt, label="Éolien (W)", color="blue")
        self.ax_opt.plot(heures, total_opt, label="Total (W)", color="red", linestyle="--")
        self.ax_opt.set_title(
            f"Scénario optimal {part_pv_opt}% PV / {part_eo_opt}% Éolien – Production horaire"
        )
        self.ax_opt.set_xlabel("Heure (h)")
        self.ax_opt.set_ylabel("Puissance (W)")
        self.ax_opt.grid(True, alpha=0.3)
        self.ax_opt.legend(loc="upper right", fontsize=8)
        self.fig_opt.tight_layout()
        self.canvas_opt.draw()

    def _courbes_horaires_pour_scenario(self, sc):
        heures = np.arange(0, 24, 1)
        irradiance = np.maximum(0, np.sin((heures - 6) / 12 * np.pi))
        solaire = irradiance / irradiance.max() * sc["e_pv"] if irradiance.max() > 0 else np.zeros_like(heures)
        base_wind = np.full_like(heures, sc["e_eo"] / len(heures))
        bruit = 0.4 * base_wind * (np.random.rand(len(heures)) - 0.5)
        eolien = np.maximum(0, base_wind + bruit)
        total = solaire + eolien
        return heures, solaire, eolien, total

    def afficher_courbes(self):
        if not self.scenarios:
            messagebox.showwarning("Attention", "Veuillez d’abord lancer le calcul des scénarios.")
            return

        win = tk.Toplevel(self.root)
        win.title("Courbes horaires pour tous les scénarios")
        win.geometry("1100x800")

        fig, axes = plt.subplots(len(self.scenarios), 1, figsize=(9, 2.5 * len(self.scenarios)), sharex=True)
        if len(self.scenarios) == 1:
            axes = [axes]

        for ax, sc in zip(axes, self.scenarios):
            heures, solaire, eolien, total = self._courbes_horaires_pour_scenario(sc)
            part_pv = int(sc["fraction_pv"] * 100)
            part_eo = 100 - part_pv

            ax.plot(heures, solaire, label="Solaire (W)", color="orange")
            ax.plot(heures, eolien, label="Éolien (W)", color="blue")
            ax.plot(heures, total, label="Total (W)", color="red", linestyle="--")
            ax.set_ylabel("Puissance (W)")
            ax.set_title(f"Scénario {part_pv}% PV / {part_eo}% Éolien")
            ax.grid(True, alpha=0.3)
            ax.legend(loc="upper right", fontsize=8)

        axes[-1].set_xlabel("Heure (h)")
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
