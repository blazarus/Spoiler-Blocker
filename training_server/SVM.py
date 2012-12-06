import numpy as np
from cvxopt import matrix, solvers
import math
import pdb

def linear_K(x, z, args):
	return np.dot(x, z)

def second_order_K(x, z, args):
	c = 1.0
	if 'c' in args:
		c = args.get('c')
	return (np.dot(x, z) + c)**2

def gaussian_K(x, z, args):
	beta = 1.0
	if 'beta' in args:
		beta = args.get('beta')
	return math.exp(-beta * np.dot(x-z, x-z))


class SVM:

	def __init__(self, C=1.0, K=linear_K, args={}):
		self.K = K
		self.C = C * 1.0
		self.args = args

	def train_primal(self, X, Y):
		"""
		Trains weights W using the primal form
		"""
		if self.K != linear_K:
			raise Exception("To train with primal form, must have a linear kernel.")

		d = len(X[0])
		n = len(X)

		# x is [W w_0 slack_vars].T

		P = matrix(0.0, (n+d+1, n+d+1))
		for i in range(d):
			P[i,i] = 1.0

		q = matrix(0.0, (n+d+1, 1))
		for i in range(d+1, n+d+1):
			q[i] = self.C

		G = matrix(0.0, (n+n, n+d+1))
		for i in range(n):
			G[i,:d] = -Y[i]*X[i]
			G[i,d] = -Y[i]
			G[i,d+1+i] = -1.0

		for i in range(n, 2*n):
			G[i,d+1+i-n] = -1.0

		h = matrix(0.0, (n+n,1))
		h[:n] = -1.0


		result = solvers.qp(P,q,G,h)

		self.W, self.w_0, slack = np.array(result['x'][:d]).ravel(), result['x'][d], result['x'][d+1:]
		print "W:", self.W
		print "w_0:", self.w_0

	def train_dual(self, X, Y):
		"""
		Trains weights W using the dual form
		"""
		(n, d) = X.shape
		print "N:", n
		print "D:", d

		# x are alphas

		P = matrix(0.0, (n,n))
		for i in range(n):
			for j in range(n):
				P[i, j] = 1.0*Y[i]*Y[j]*self.K(X[i],X[j], self.args)

		q = matrix(-1.0, (n,1))

		h = matrix(0.0, (n+n,1))
		h[n:] = self.C

		G = matrix(0.0, (n+n, n))
		for i in range(n):
			G[i,i] = -1.0
			G[n+i,i] = 1.0

		A = matrix(0.0, (1,n))
		for i in range(n):
			A[i] = Y[i]

		b = matrix(0.0, (1,1))

		result = solvers.qp(P,q,G,h,A,b)

		basicallyzero = 1e-5
		self.alphas = np.array(result['x']).ravel()
		self.support_alphas = self.alphas[self.alphas>basicallyzero]
		self.support_vectors = X[self.alphas>basicallyzero]
		self.support_vector_labels = Y[self.alphas>basicallyzero]

		if self.K != linear_K:
			self.W = None
		else:
			self.W = np.zeros(d)
			for i in range(n):
				self.W += self.alphas[i] * Y[i] * X[i]

		print "W:", self.W

		# Set of indices (in support vectors) for which 0 < alpha < C
		M = [i for i in range(len(self.support_alphas)) if self.support_alphas[i] < self.C - basicallyzero]

		if len(M) == 0:
			print self.C - basicallyzero
			print self.support_alphas
		self.w_0 = 0.0
		for j in M:
			for i in range(len(self.support_vectors)):
				self.w_0 -= self.support_alphas[i]*self.support_vector_labels[i]\
							*self.K(self.support_vectors[j],self.support_vectors[i], self.args)
			self.w_0 += self.support_vector_labels[j]
		self.w_0 = self.w_0 / len(M) 

		print "w_0:", self.w_0


	def predict(self, x):
		"""
		test_x -> a new data point to test against our SVM to precict its class
		"""
		if self.K == linear_K:
			return np.sign(np.dot(self.W,x) + self.w_0)
		else:
			# We are dealing with kernels and so we predict 
			# without explicity using weights to avoid computing feature vectors
			s = 0.0
			for i in range(len(self.support_vectors)):
				s += self.support_alphas[i] * self.support_vector_labels[i] \
											* self.K(x,self.support_vectors[i], self.args)
			return np.sign(s + self.w_0)

	def num_incorrect(self, X, Y):
		"""
		Count the number of incorrect classifications
		"""
		count = 0
		for i in range(len(X)):
			if self.predict(X[i]) != Y[i]:
				count += 1

		return count