import os
import subprocess
import sys
import numpy as np
import pathlib
import tarfile

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    
    install('tensorflow==2.3.1')
    model_path = f"/opt/ml/processing/model/model.tar.gz"
    with tarfile.open(model_path, 'r:gz') as tar:
        tar.extractall('./model')
    import tensorflow as tf
    model = tf.keras.models.load_model('./model/1')
    test_path = "/opt/ml/processing/test/"
    x_test = np.load(os.path.join(test_path, 'x_test.npy'))
    y_test = np.load(os.path.join(test_path, 'y_test.npy'))
    scores = model.evaluate(x_test, y_test, verbose=2)
    print("\nTest MSE :", scores)
    
    output_dir = "/opt/ml/processing/batch"
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
    evaluation_path = f"{output_dir}/score-report.txt"
    with open(evaluation_path, 'w') as writer:
         writer.write(f"Test MSE : {scores}")