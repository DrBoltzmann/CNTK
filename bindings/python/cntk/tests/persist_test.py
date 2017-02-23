# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root
# for full license information.
# ==============================================================================

import numpy as np

import cntk as C
from cntk.debugging import save_as_legacy_model

# TODO: a test for restore_model?

def test_load_save_constant(tmpdir):
    c = C.constant(value=[1,3])
    root_node = c * 5

    result = root_node.eval()
    expected = [[[[5,15]]]]
    assert np.allclose(result, expected)

    filename = str(tmpdir / 'c_plus_c.mod')
    root_node.save(filename)

    loaded_node = C.Function.load(filename)
    loaded_result = loaded_node.eval()
    assert np.allclose(loaded_result, expected)

    filename = filename + '.legacy'
    save_as_legacy_model(root_node, filename)
    loaded_node = C.Function.load(filename)
    loaded_result = loaded_node.eval()
    assert np.allclose(loaded_result, expected)

def test_load_save_input_legacy_names(tmpdir):
    i1 = C.input_variable((1,2), name='i1')
    root_node = abs(i1)
    input1 = [[[-1,2]]]

    result = root_node.eval({i1: input1})
    expected = [[[[1,2]]]]
    assert np.allclose(result, expected)

    filename = str(tmpdir / 'i_plus_c_0.mod')
    root_node.save(filename)

    loaded_node = C.Function.load(filename)

    # Test specifying the input node names by order
    loaded_result = loaded_node.eval([input1])
    assert np.allclose(loaded_result, expected)

    filename = filename + '.legacy'
    save_as_legacy_model(root_node, filename)
    loaded_node = C.Function.load(filename)
    loaded_result = loaded_node.eval([input1])
    assert np.allclose(loaded_result, expected)

def test_load_save_inputs(tmpdir):
    i1 = C.input_variable((1,2), name='i1')
    i2 = C.input_variable((2,1), name='i2')
    root_node = C.plus(i1, i2)
    input1 = [[[1,2]]]
    input2 = [[[[1],[2]]]]

    result = root_node.eval({i1: input1, i2: input2})
    expected = [[[[2,3],[3,4]]]]
    assert np.allclose(result, expected)

    filename = str(tmpdir / 'i_plus_i_0.mod')
    root_node.save(filename)

    loaded_node = C.Function.load(filename)

    # Test specifying the input nodes by name
    loaded_result = loaded_node.eval({'i1': input1, 'i2': input2})
    assert np.allclose(loaded_result, expected)

    filename = filename + '.legacy'
    save_as_legacy_model(root_node, filename)
    loaded_node = C.Function.load(filename)
    loaded_result = loaded_node.eval({'i1': input1, 'i2': input2})
    assert np.allclose(loaded_result, expected)

def test_load_save_unique_input(tmpdir):
    i1 = C.input_variable((1,2), name='i1')
    root_node = C.softmax(i1)

    input1 = [[[1,2]]]
    result = root_node.eval(input1)
    expected = [[[[ 0.268941,  0.731059]]]]
    assert np.allclose(result, expected)

    filename = str(tmpdir / 'i_plus_0.mod')
    root_node.save(filename)

    loaded_node = C.Function.load(filename)

    # Test specifying the only value for a unique input
    loaded_result = loaded_node.eval(input1)
    assert np.allclose(loaded_result, expected)

    filename = filename + '.legacy'
    save_as_legacy_model(root_node, filename)
    loaded_node = C.Function.load(filename)
    loaded_result = loaded_node.eval(input1)
    assert np.allclose(loaded_result, expected)


def test_large_model_serialization_float(tmpdir):
    import os; 
    from cntk.layers import Recurrence, LSTM, Dense

    type_size = np.dtype(np.float32).itemsize
    two_gb = 2**31
    size = (2097152 + 4, 256, 512, 4096)
    assert size[0] * size[1] * type_size > two_gb

    device = C.device.cpu()
    i = C.sequence.input(size[0])
    w = C.Parameter((size[0], size[1]), init=C.uniform(3.0, seed=12345),
        device=device)
    e = C.times(i, w)
                                    
    h_fwd = Recurrence(LSTM(size[2]))(e)
    h_bwd = Recurrence(LSTM(size[2]), go_backwards=True)(e)
    h_last_fwd = C.sequence.last(h_fwd)
    h_first_bwd = C.sequence.first(h_bwd)
    t = C.splice(h_last_fwd, h_first_bwd)

    z1 = Dense(size[2], activation=C.relu)(t)     
    z = Dense(2, activation=None)(z1)  

    filename = str(tmpdir / 'test_large_model_serialization_float.out')
    z.save(filename)

    assert os.path.getsize(filename) > two_gb

    y = C.Function.load(filename, device=device)

    assert (len(z.parameters) == len(y.parameters))

    for param_pair in zip(z.parameters, y.parameters):
        assert param_pair[0].shape == param_pair[1].shape
        assert np.allclose(param_pair[0].value, param_pair[1].value)


# TODO: once layers lib understands dtype parameter, 
# this should be merge with the test above:
# for dtype in [np.float32, np.float64]:
#    ....
def test_large_model_serialization_double(tmpdir):
    import os; 

    two_gb = 2**31
    type_size = np.dtype(np.float64).itemsize
    size = two_gb /  type_size + 10

    assert size * type_size > two_gb

    device = C.device.cpu()
    i = C.sequence.input(size, dtype=np.float64)
    w = C.Parameter((size,), dtype=np.float64, 
        init=C.uniform(3.0, seed=12345), device=device)
    z = C.times(i, w)

    filename = str(tmpdir / 'test_large_model_serialization_double.out')
    z.save(filename)

    assert os.path.getsize(filename) > two_gb

    y = C.Function.load(filename, device=device)

    assert (len(z.parameters) == len(y.parameters))

    for param_pair in zip(z.parameters, y.parameters):
        assert param_pair[0].shape == param_pair[1].shape
        assert np.allclose(param_pair[0].value, param_pair[1].value)

