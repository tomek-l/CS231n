from builtins import range
from builtins import object
import numpy as np

from cs231n.layers import *
from cs231n.layer_utils import *


class TwoLayerNet(object):
    """
    A two-layer fully-connected neural network with ReLU nonlinearity and
    softmax loss that uses a modular layer design. We assume an input dimension
    of D, a hidden dimension of H, and perform classification over C classes.

    The architecure should be affine - relu - affine - softmax.

    Note that this class does not implement gradient descent; instead, it
    will interact with a separate Solver object that is responsible for running
    optimization.

    The learnable parameters of the model are stored in the dictionary
    self.params that maps parameter names to numpy arrays.
    """

    def __init__(self, input_dim=3*32*32, hidden_dim=100, num_classes=10,
                 weight_scale=1e-3, reg=0.0):
        """
        Initialize a new network.

        Inputs:
        - input_dim: An integer giving the size of the input
        - hidden_dim: An integer giving the size of the hidden layer
        - num_classes: An integer giving the number of classes to classify
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - reg: Scalar giving L2 regularization strength.
        """
        ############################################################################
        # TODO: Initialize the weights and biases of the two-layer net. Weights    #
        # should be initialized from a Gaussian centered at 0.0 with               #
        # standard deviation equal to weight_scale, and biases should be           #
        # initialized to zero. All weights and biases should be stored in the      #
        # dictionary self.params, with first layer weights                         #
        # and biases using the keys 'W1' and 'b1' and second layer                 #
        # weights and biases using the keys 'W2' and 'b2'.                         #
        ############################################################################
        
        self.params = {}
        self.reg = reg
        
        self.params['W1'] = weight_scale * np.random.randn(input_dim, hidden_dim)
        self.params['W2'] = weight_scale * np.random.randn(hidden_dim, num_classes)
        
        self.params['b1'] = np.zeros(hidden_dim)
        self.params['b2'] = np.zeros(num_classes)
        
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################


    def loss(self, X, y=None):
        """
        Compute loss and gradient for a minibatch of data.

        Inputs:
        - X: Array of input data of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

        Returns:
        If y is None, then run a test-time forward pass of the model and return:
        - scores: Array of shape (N, C) giving classification scores, where
          scores[i, c] is the classification score for X[i] and class c.

        If y is not None, then run a training-time forward and backward pass and
        return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping parameter
          names to gradients of the loss with respect to those parameters.
        """
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the two-layer net, computing the    #
        # class scores for X and storing them in the scores variable.              #
        ############################################################################
        #     The architecure should be affine - relu - affine - softmax.
        W1, W2, b1, b2 = self.params['W1'], self.params['W2'], \
        self.params['b1'], self.params['b2']
        
        L1, L1_cache = affine_relu_forward(X, W1, b1)
        L2, L2_cache = affine_forward(L1, W2, b2)
        
        scores = L2
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If y is None then we are in test mode so just return scores
        if y is None:
            return scores

        loss, dscores = softmax_loss(L2, y)
        loss += 0.5 * self.reg * ( np.sum(W1*W1) + np.sum(W2*W2))
       
        
        ############################################################################
        # TODO: Implement the backward pass for the two-layer net. Store the loss  #
        # in the loss variable and gradients in the grads dictionary. Compute data #
        # loss using softmax, and make sure that grads[k] holds the gradients for  #
        # self.params[k]. Don't forget to add L2 regularization!                   #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        
        grads = {}
        dL2, grads['W2'], grads['b2'] = affine_backward(dscores, L2_cache) # returns dx, dw, db
        _, grads['W1'], grads['b1'] = affine_relu_backward(dL2, L1_cache)
        
        grads['W1'] += self.reg * W1
        grads['W2'] += self.reg * W2
        
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################
        
        return loss, grads


class FullyConnectedNet(object):
    """
    A fully-connected neural network with an arbitrary number of hidden layers,
    ReLU nonlinearities, and a softmax loss function. This will also implement
    dropout and batch/layer normalization as options. For a network with L layers,
    the architecture will be

    {affine - [batch/layer norm] - relu - [dropout]} x (L - 1) - affine - softmax

    where batch/layer normalization and dropout are optional, and the {...} block is
    repeated L - 1 times.

    Similar to the TwoLayerNet above, learnable parameters are stored in the
    self.params dictionary and will be learned using the Solver class.
    """

    def __init__(self, hidden_dims, input_dim=3*32*32, num_classes=10,
                 dropout=1, normalization=None, reg=0.0,
                 weight_scale=1e-2, dtype=np.float32, seed=None):
        """
        Initialize a new FullyConnectedNet.

        Inputs:
        - hidden_dims: A list of integers giving the size of each hidden layer.
        - input_dim: An integer giving the size of the input.
        - num_classes: An integer giving the number of classes to classify.
        - dropout: Scalar between 0 and 1 giving dropout strength. If dropout=1 then
          the network should not use dropout at all.
        - normalization: What type of normalization the network should use. Valid values
          are "batchnorm", "layernorm", or None for no normalization (the default).
        - reg: Scalar giving L2 regularization strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - dtype: A numpy datatype object; all computations will be performed using
          this datatype. float32 is faster but less accurate, so you should use
          float64 for numeric gradient checking.
        - seed: If not None, then pass this random seed to the dropout layers. This
          will make the dropout layers deteriminstic so we can gradient check the
          model.
        """
        self.normalization = normalization
        self.use_dropout = dropout != 1
        self.reg = reg
        self.num_layers = 1 + len(hidden_dims)
        self.dtype = dtype
        self.params = {}
        self.hidden_dims = hidden_dims


        # When using batch normalization, store scale and shift parameters for the #
        # first layer in gamma1 and beta1; for the second layer use gamma2 and     #
        # beta2, etc. Scale parameters should be initialized to ones and shift     #
        # parameters should be initialized to zeros.                               #
        
        self.C = num_classes
        self.L = self.num_layers
        
        dims = [input_dim] + hidden_dims + [num_classes]
        
        for i in range(1, len(dims)):
            l = str(i)
            #the first layer's weights are 
            self.params['W'+l] = weight_scale * np.random.randn(dims[i-1], dims[i])
            self.params['b'+l] = np.zeros(dims[i])
            
            if self.normalization =='batchnorm':
                self.params['gamma'+l] = np.random.randn(dims[i-1])
                self.params['beta'+l] = np.random.randn(dims[i-1])

        # When using dropout we need to pass a dropout_param dictionary to each
        # dropout layer so that the layer knows the dropout probability and the mode
        # (train / test). You can pass the same dropout_param to each dropout layer.
        self.dropout_param = {}
        if self.use_dropout:
            self.dropout_param = {'mode': 'train', 'p': dropout}
            if seed is not None:
                self.dropout_param['seed'] = seed

        # With batch normalization we need to keep track of running means and
        # variances, so we need to pass a special bn_param object to each batch
        # normalization layer. You should pass self.bn_params[0] to the forward pass
        # of the first batch normalization layer, self.bn_params[1] to the forward
        # pass of the second batch normalization layer, etc.
        
        self.bn_params_list = [] # list of bn_params dictionaries 
        
        if self.normalization=='batchnorm':
            self.bn_params_list = [{'mode': 'train',
                                   'running_mean': np.zeros(dims[i]),
                                   'running_var': np.zeros(dims[i])} for i in range(self.num_layers)]
            
        if self.normalization=='layernorm':
            self.bn_params_list = [{} for i in range(self.num_layers - 1)]

        # Cast all parameters to the correct datatype
        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)
    

    def loss(self, X, y=None):
        """
        Compute loss and gradient for the fully-connected net.

        Input / output: Same as TwoLayerNet above.
        """
        x = X.astype(self.dtype)
        N = x.shape[0]
        x = x.reshape(N,-1)
        D = x.shape[1]
        
        #Silly mode detection stuff
        mode = 'test' if y is None else 'train'
        
        # Set train/test mode for batchnorm params and dropout param since they
        # behave differently during training and testing.
        
        if self.use_dropout:
            self.dropout_param['mode'] = mode
        #When using dropout, you'll need to pass self.dropout_param to each dropout forward pass.
        
        if self.normalization=='batchnorm':
            for bn_param in self.bn_params_list:
                bn_param['mode'] = mode 
                        
        self.cache = {} #cache are the parameters for backprop
        
        #iterate over ALL LAYERS but the output layer
        for i in range(self.L-1):

            l = str(i+1) #layer no as string
            w = self.params['W'+l]
            b = self.params['b'+l]

            #BATCHNORM
            if self.normalization =='batchnorm':
                gamma = self.params['gamma'+l]
                beta = self.params['beta'+l]
                # Actual forward pass
                x, self.cache['batchnorm'+l] = batchnorm_forward(x, gamma, beta, self.bn_params_list[i])

            #RELU
            x, self.cache['c'+l] = affine_relu_forward(x, w, b) #cache stored as c1, c2, etc.
            
            #DROPOUT
            if self.use_dropout:
                x, self.cache['dropout'+l] = dropout_forward(x, self.dropout_param)


        #LAST LAYER (sofmax instead of ReLU)
        #BATCHNORM
        if self.normalization =='batchnorm':
            gamma = self.params['gamma'+str(self.L)]
            beta = self.params['beta'+str(self.L)]
            x, self.cache['batchnorm'+str(self.L)] = batchnorm_forward(x, gamma, beta, self.bn_params_list[self.L-1])
        
        #fully connected
        lw, lb = self.params['W'+str(self.L)], self.params['b'+str(self.L)] #last layer's weights
        scores, self.cache['c'+str(self.L)] = affine_forward(x, lw, lb)
        
        # If test mode return early
        if mode == 'test':
            return scores
        
        # When using batch/layer normalization, you don't need to regularize the scale
        # and shift parameters
        self.grads = {}
        grads = self.grads
        
        #compute loss
        loss, dscores = softmax_loss(scores, y)
        
        
        #backpropagate through the last affine layer
        l=str(self.L)
        dout, grads['W'+l], grads['b'+l] = affine_backward(dscores, self.cache['c'+l])
        
        if self.normalization =='batchnorm':
            dout, grads['gamma'+l], grads['beta'+l], _ = batchnorm_backward(dout, self.cache['batchnorm'+l])
        
        for i in range(self.L-1, 0, -1): #iterate over all layers but the output layer
            l = str(i) #layer no as string
            
            #BACKPROP DROPOUT
            if self.use_dropout:
                dout = dropout_backward(dout, self.cache['dropout'+l])
            
            #BACKPROP AFFINE RELU
            dout, grads['W'+l], grads['b'+l] = affine_relu_backward(dout, self.cache['c'+l])
            
            if self.normalization =='batchnorm':
                dout, grads['gamma'+l], grads['beta'+l], _ = batchnorm_backward(dout, self.cache['batchnorm'+l])
        
        #L2 regularization
        reg_loss = 0
        for par in self.params:
            reg_loss += 0.5 * self.reg * np.sum(self.params[par]**2) #TODO: wywal

        return loss, grads
