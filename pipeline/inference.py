import numpy as np
import torch

from pipeline.model import Classificator, Regression

DEVICE = "cuda"

classificator = Classificator()
regressor_nhyp = Regression()
regressor_nap = Regression()


def init_models():
    classificator.load_state_dict(torch.load("./pipeline/classificator.pt"))
    classificator.eval()

    regressor_nhyp.load_state_dict(torch.load("./pipeline/regression_nhyp.pt"))
    regressor_nhyp.eval()
    regressor_nap.load_state_dict(torch.load("./pipeline/regression_nap.pt"))
    regressor_nap.eval()


def predict(table_data: np.ndarray, channels: np.ndarray):
    table_data = torch.tensor(table_data).to(torch.float32)
    channels = torch.tensor(channels[:6, :5*10**6]).to(torch.float32)
    with torch.no_grad():
        confidence = classificator(table_data, channels).item()
        has_apnoea = confidence >= 0.5
        if not has_apnoea:
            return {"RESULT": has_apnoea, "APNEA_COUNT": 0, "HYPOPNEA_COUNT": 0}

        NAp = int(regressor_nap(table_data, channels).item())
        NHyp = int(regressor_nhyp(table_data, channels).item())

        return {"RESULT": has_apnoea, "APNEA_COUNT": NAp, "HYPOPNEA_COUNT": NHyp, "CONFIDENCE": confidence}
