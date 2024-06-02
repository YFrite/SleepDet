def get_seq(data, seq_length, step):
    x = []

    for i in range(0, len(data) - seq_length, step):
        x.append(data[i:i + seq_length])

    return x
