import os
import shutil

import numpy as np
import matplotlib.pyplot as plt

AVAILABLE = ["Fp1-M2", "C3-M2", "O1-M2", "Fp2-M1", "C4-M1", "O2-M1"]
CM = 1/2.54
FOLDER = "uploads/images"


def clear_images_dir():
    for filename in os.listdir(FOLDER):
        file_path = os.path.join(FOLDER, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def create_dashboards(channels, data):

    clear_images_dir()
    images = {}
    for ch, arr in zip(AVAILABLE, data):
        if ch in channels:
            create_dashboard(ch, arr)
    return


def average_blocks(data, block_size):
    # Определяем количество блоков
    num_blocks = len(data) // block_size

    # Создаем новый массив для средних значений
    averaged_data = np.zeros(num_blocks)

    # Вычисляем средние значения для каждого блока
    for i in range(num_blocks):
        block = data[i * block_size: (i + 1) * block_size]
        averaged_data[i] = np.mean(block)

    return averaged_data


def create_dashboard(name, ch):

    WINDOW = 2000
    y_data = average_blocks(ch, WINDOW)  # Замени на свои данные длины n
    n = y_data.shape[0]

    x_data = np.arange(0, n, 1)

    plt.figure(figsize=(10 * CM, 5 * CM), dpi=600)
    plt.plot(x_data, y_data, color='b', label='Data')

    # Добавляем подписи и заголовок
    plt.xlabel('t=10сек')
    plt.ylabel('Значение')
    plt.title(f'График {name}')
    plt.legend()
    plt.grid(True)
    image_path = "./uploads/images/IMAGE_" + name + ".png"
    plt.savefig(image_path)
    plt.close()

