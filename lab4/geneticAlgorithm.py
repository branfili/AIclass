import numpy as np

class GeneticAlgorithm(object):
	"""
		Implement a simple generationl genetic algorithm as described in the instructions
	"""

	def __init__(	self, chromosomeShape,
					errorFunction,
					elitism = 1,
					populationSize = 25,
					mutationProbability  = .1,
					mutationScale = .5,
					numIterations = 10000,
					errorThreshold = 1e-6
					):

		self.populationSize = populationSize # size of the population of units
		self.p = mutationProbability # probability of mutation
		self.numIter = numIterations # maximum number of iterations
		self.e = errorThreshold # threshold of error while iterating
		self.f = errorFunction # the error function (reversely proportional to fitness)
		self.keep = elitism  # number of units to keep for elitism
		self.k = mutationScale # scale of the gaussian noise

                self.fit = lambda x: -x

		self.i = 0 # iteration counter

		# initialize the population randomly from a gaussian distribution
		# with noise 0.1 and then sort the values and store them internally

		self.population = []
		for _ in range(populationSize):
			chromosome = np.random.randn(chromosomeShape) * 0.1
			fitness = self.calculateFitness(chromosome)

                        self.population.append((chromosome, fitness))

		# sort descending according to fitness (larger is better)
		self.population = sorted(self.population, key=lambda t: -t[1])

	def step(self):
		"""
			Run one iteration of the genetic algorithm. In a single iteration,
			you should create a whole new population by first keeping the best
			units as defined by elitism, then iteratively select parents from
			the current population, apply crossover and then mutation.

			The step function should return, as a tuple:

			* boolean value indicating should the iteration stop (True if
				the learning process is finished, False othwerise)
			* an integer representing the current iteration of the
				algorithm
			* the weights of the best unit in the current iteration

		"""

		self.i += 1

		newPopulation = self.bestN(self.keep)

                for i in range(self.keep, self.populationSize):
                    (p1, p2) = self.selectParents()

                    newChromosome = self.mutate(self.crossover(p1, p2))
                    fitness = self.calculateFitness(newChromosome)

                    newPopulation.append((newChromosome, fitness))

                self.population = sorted(newPopulation, key=lambda t: -t[1])

                bestUnit = self.best()

                return (bestUnit[1] > self.fit(self.e) or self.i >= self.numIter,
                        self.i,
                        bestUnit[0])

	def calculateFitness(self, chromosome):
		"""
			Implement a fitness metric as a function of the error of
			a unit. Remember - fitness is larger as the unit is better!
		"""
		chromosomeError = self.f(chromosome)

                return self.fit(chromosomeError)

	def bestN(self, n):
		"""
			Return the best n units from the population
		"""

                return self.population[:n]

	def best(self):
		"""
			Return the best unit from the population
		"""
		return self.bestN(1)[0]

        def selectParent(self, blacklist = None):
            total = 0.0
            n = self.populationSize - (0 if blacklist is None else 1)

            for unit in self.population:
                if blacklist is not None and \
                   all(unit[0] == blacklist[0]):
                    continue

                total += unit[1]

            r = np.random.random()
            z = 0.0

            for unit in self.population:
                if blacklist is not None and \
                   all(unit[0] == blacklist[0]):
                    continue

                p = (total - unit[1]) / (total * (n - 1))

                z += p

                if (z >= r):
                    return unit

	def selectParents(self):
		"""
			Select two parents from the population with probability of
			selection proportional to the fitness of the units in the
			population
		"""
		parent1 = self.selectParent()

                parent2 = self.selectParent(parent1)

                return (parent1, parent2)

	def crossover(self, p1, p2):
		"""
			Given two parent units p1 and p2, do a simple crossover by
			averaging their values in order to create a new child unit
		"""

                child = np.array([])

                for i in range(p1[0].size):
                    x1 = p1[0][i]
                    x2 = p2[0][i]

                    child = np.append(child, (x1 + x2) / 2.0)

                return child

	def mutate(self, chromosome):
		"""
			Given a unit, mutate its values by applying gaussian noise
			according to the parameter k
		"""

                for i in range(chromosome.size):
                    if (np.random.random() < self.p):
                        chromosome[i] += np.random.standard_normal() * self.k

                return chromosome

