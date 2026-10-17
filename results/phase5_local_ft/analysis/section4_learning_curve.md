## Section 4 — Data-size hypothesis

Cross-target (5 targets, MARBERT, S2, full data): Pearson r(F1, positives)=0.945 (p=0.015), r(AUC, positives)=-0.322 (p=0.597).
Power-law fit F1 = a*x^b on the 5 points: {'a': 0.009575220461355656, 'b': 0.5886359804531801, 'r2': 0.8641740736526438}
Power-law fit AUC = a*x^b on the 5 points: {'a': 0.9956923238579086, 'b': -0.0725616275846897, 'r2': 0.16327455402869628}

**easy learning curve** (n=12 runs: 4 fractions x 3 seeds):
- power-law fit F1: {'a': 0.15304043657750943, 'b': 0.03091508997295802, 'r2': 0.02021334198216851}
- saturating fit F1 = c*(1-exp(-x/tau)): {'c': 0.18348697503832537, 'tau': 6.829811247231841, 'r2': 0.03482147252092238}
- Pearson r (within-target, F1 vs positives): [np.float64(0.20807177904351876), np.float64(0.5163784380511198)]
**medium learning curve** (n=12 runs: 4 fractions x 3 seeds):
- power-law fit F1: {'a': 0.525992539894963, 'b': 0.006276715795942624, 'r2': 0.06518419688796762}
- saturating fit F1 = c*(1-exp(-x/tau)): {'c': 0.5463245490480323, 'tau': 17.387876639396186, 'r2': 0.04276864646334011}
- Pearson r (within-target, F1 vs positives): [np.float64(0.3258769873716785), np.float64(0.3012750540053163)]