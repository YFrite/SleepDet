import os

import numpy as np
import torch

from flask_app.scripts.pipeline.model import Classificator, Regression

DEVICE = "cpu"

classificator = Classificator()
regressor_nhyp = Regression()
regressor_nap = Regression()


def init_models():
    map_location = torch.device(DEVICE)
    print()
    classificator.load_state_dict(torch.load("./scripts/pipeline/classificator.pt", map_location))
    classificator.eval()

    regressor_nhyp.load_state_dict(torch.load("./scripts/pipeline/regression_nhyp.pt", map_location))
    regressor_nhyp.eval()
    regressor_nap.load_state_dict(torch.load("./scripts/pipeline/regression_nap.pt", map_location))
    regressor_nap.eval()


def predict(table_data: np.ndarray, channels: np.ndarray):
    table_data = torch.tensor(table_data).to(torch.float32)
    channels = torch.tensor(channels[:6, :5*10**6]).to(torch.float32)
    with torch.no_grad():
        confidence = classificator(table_data, channels).item()
        has_apnoea = confidence >= 0.5
        if not has_apnoea:
            return {"RESULT": has_apnoea, "APNEA_COUNT": 0, "HYPOPNEA_COUNT": 0, "CONFIDENCE": confidence}

        NAp = int(regressor_nap(table_data, channels).item())
        NHyp = int(regressor_nhyp(table_data, channels).item())

        return {"RESULT": has_apnoea, "APNEA_COUNT": NHyp, "HYPOPNEA_COUNT": NAp, "CONFIDENCE": confidence}
