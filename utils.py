from tkinter import filedialog
import os

def save_file(file_name, x, y):
    os.makedirs("saved output", exist_ok=True)
    file_path = os.path.join("saved output", file_name + ".txt")

    with open(file_path, "w") as file:
        file.write(f"0\n0\n{len(x)}\n")
        for xi, yi in zip(x, y):
            file.write(f"{xi},{yi}\n")


def browse_file(file_label, x_input, idx, readBoth=False):
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        file_label.config(text="Selected File: " + file_path)
        if readBoth:
            x_input[idx] = [], []
        else:
            x_input[idx] = []

        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) == 2:
                    if readBoth:
                        x_input[idx][0].append(float(parts[0]))
                        x_input[idx][1].append(float(parts[1]))
                    else:
                        x_input[idx].append(float(parts[1]))


def Compare_Signals(file_name,Your_indices,Your_samples):
    if not os.path.isfile(file_name):
        print(f"File '{file_name}' does not exist.")
        return
    expected_indices=[]
    expected_samples=[]
    with open(file_name, 'r') as f:
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        while line:
            # process line
            L=line.strip()
            if len(L.split(' '))==2:
                L=line.split(' ')
                V1=int(L[0])
                V2=float(L[1])
                expected_indices.append(V1)
                expected_samples.append(V2)
                line = f.readline()
            else:
                break
    print("Current Output Test file is: ")
    print(file_name)
    print("\n")
    if (len(expected_samples)!=len(Your_samples)) and (len(expected_indices)!=len(Your_indices)):
        print("Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if(Your_indices[i]!=expected_indices[i]):
            print("Test case failed, your signal have different indicies from the expected one")
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Test case failed, your signal have different values from the expected one")
            return
    print("Test case passed successfully")


def SignalSamplesAreEqual(file_name, samples):
    if not os.path.isfile(file_name):
        print(f"File '{file_name}' does not exist.")
        return
    expected_indices = []
    expected_samples = []
    with open(file_name, 'r') as f:
        line = f.readline()
        line = f.readline()
        line = f.readline()
        line = f.readline()
        while line:
            # process line
            L = line.strip()
            if len(L.split(' ')) == 2:
                L = line.split(' ')
                V1 = int(L[0])
                V2 = float(L[1])
                expected_indices.append(V1)
                expected_samples.append(V2)
                line = f.readline()
            else:
                break

    if len(expected_samples) != len(samples):
        print("Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(expected_samples)):
        if abs(samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Test case failed, your signal have different values from the expected one")
            return
    print("Test case passed successfully")


def ConvTest(Your_indices, Your_samples):
    """
    Test inputs
    InputIndicesSignal1 =[-2, -1, 0, 1]
    InputSamplesSignal1 = [1, 2, 1, 1 ]

    InputIndicesSignal2=[0, 1, 2, 3, 4, 5 ]
    InputSamplesSignal2 = [ 1, -1, 0, 0, 1, 1 ]
    """

    expected_indices = [-2, -1, 0, 1, 2, 3, 4, 5, 6]
    expected_samples = [1, 1, -1, 0, 0, 3, 3, 2, 1]

    if (len(expected_samples) != len(Your_samples)) and (len(expected_indices) != len(Your_indices)):
        print("Conv Test case failed, your signal have different length from the expected one")
        return
    for i in range(len(Your_indices)):
        if (Your_indices[i] != expected_indices[i]):
            print("Conv Test case failed, your signal have different indicies from the expected one")
            return
    for i in range(len(expected_samples)):
        if abs(Your_samples[i] - expected_samples[i]) < 0.01:
            continue
        else:
            print("Conv Test case failed, your signal have different values from the expected one")
            return
    print("Conv Test case passed successfully")