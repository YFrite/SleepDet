AVAILABLE = ["Fp1-M2", "C3-M2", "O1-M2", "Fp2-M1", "C4-M1", "O2-M1"]


def create_dashboards(channels, data):
    for ch, arr in zip(AVAILABLE, data):
        if ch in channels:
            create_dashboard(ch, data)


def create_dashboard(ch):
    return
