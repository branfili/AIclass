from networkLayers import *
from transferFunctions import *

class NeuralNetwork(object):
	"""
		A class which streamlines the output through layers and error calculation.
	"""

	def __init__(self):
		"""
			Initialize the layers of the neural network to an empty array.
		"""
		self.layers = []

	def addLayer(self, layer):
		"""
			Add a layer to the neural network in sequential fashion.
		"""
		self.layers.append(layer)

	def output(self, x):
		"""
			Calculate the output for a single input instance x (one row from
			the training or test set)
		"""

		# For each layer - calcuate the output of that layer and use it
		# as input to the following layer. The method should return the
		# output of the last layer. The input to the first layer is the
		# vector x.

                y = x

                for layer in self.layers:
                    y = layer.output(y)

                return y

	def outputs(self, X):
		"""
			For a given vector of input instances X (the training or test set),
			return the vector of outputs for all the input instances.
		"""

		# Input: vector X (train / test set)
		# Output: vector y_pred (predicted output values of the target function)

		y_pred = self.output(X[0])

                for i in range(1, X.shape[0]):
                    y_pred = np.vstack([y_pred, self.output(X[i])])

                return y_pred

	def error(self, prediction, y):
		"""
			Calculates the error for a single example in the train/test set.
			The default error is MSE (mean square error).
		"""

		# Return the square error for a single example (the mean square error)
		# is calculated over all the training instances

		return 0.5 * ((prediction - y) ** 2).sum()


	def total_error(self, predictions, Y):
		"""
			Calculates the total error for ALL the examples in the train/test set.
		"""

		# Input: vector of predicted values (predictions)
		#        vector of actual values (Y) from the training / test set
		# Output: The Mean Square Error for all the instances

                error = 0.0

                for i in range(predictions.shape[0]):
                    y1 = predictions[i]
                    y2 = Y[i]

                    error += self.error(y1, y2)

                return error

	def forwardStep(self, X, Y):
		"""
			Run the inputs X (train/test set) through the network, and calculate
			the error on the given true target function values Y
		"""

		return self.total_error(self.outputs(X), Y)

	def size(self):
		"""
			Return the total number of weights in the network
		"""
		totalSize = 0
		for layer in self.layers:
			totalSize += layer.size()
		return totalSize

	def getWeightsFlat(self):
		"""
			Return a 1-d representation of all the weights in the network
		"""
		flatWeights = np.array([])
		for layer in self.layers:
			flatWeights = np.append(flatWeights, layer.getWeightsFlat())
		return flatWeights

	def setWeights(self, flat_vector):
		"""
			Set the weights for all layers in the network
		"""
		# first layers come first in the flat vector
		for layer in self.layers:
			layer_weights = flat_vector[:layer.size()]
			layer.setWeights(layer_weights)
			flat_vector = flat_vector[layer.size():]
