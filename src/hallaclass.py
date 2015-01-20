"""
HAllA class  
"""
# # structural packages 
# # internal dependencies
# from pandas import *
'''from rpy2.robjects.packages import importr
import rpy2.robjects as ro
import pandas.rpy.common as com
import rpy2.robjects.numpy2ri'''

import csv
import itertools
from numpy import *
import os
import shutil 
import sys
import time

import distance
import hierarchy
import numpy as np
import scipy as sp
import stats


class HAllA():
	
	def __init__(self, args, aOutX, aOutY): 
		
		#==================================================================#
		# Parameters  
		#==================================================================#

		#----------------------------------#
		# Single and cross-decomposition 
		#----------------------------------#

		self.distance = distance.adj_mi 
		self.reduce_method = "pca" 
		

		#----------------------------------#
		# Step and jump methods 
		#----------------------------------#
		
		self.exploration_function = "default"
			# #{"layerwise", "greedy", "default"}

		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
		# delta 
		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

		self.step_parameter = 1.0  # # a value between 0.0 and 1.0; a fractional value of the layers to be tested 

		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
		# sigma  
		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

		#------------------------------------------------#
		# Randomization and multiple correction  methods 
		#------------------------------------------------#

		self.q = 0.2  # ## Between covariance cut-off value
		self.iterations = 1000
		self.p_adjust_method = "BH"
		self.randomization_method = "permutation"  # method to generate error bars 
		# self.outcome = []
		#------------------------------------------------------------------#
		# Discretization  
		#------------------------------------------------------------------#

		self.meta_disc_skip = None  # which indices to skip when discretizing? 

		#------------------------------------------------------------------#
		# Feature Normalization   
		#------------------------------------------------------------------#

		# # Beta warping, copulas? 

		#------------------------------------------------------------------#
		# Output Parameters    
		#------------------------------------------------------------------#

		self.summary_method = "final"
			# # {"all","final"}
		self.verbose = False 

		#==================================================================#
		# Static Objects  
		#==================================================================#

		self.__description__ 	 = """
		  _    _          _ _          
		 | |  | |   /\   | | |   /\    
		 | |__| |  /  \  | | |  /  \   
		 |  __  | / /\ \ | | | / /\ \  
		 | |  | |/ ____ \| | |/ ____ \ 
		 |_|  |_/_/    \_\_|_/_/    \_\
		                               

		HAllA Object for hierarchical all-against-all association testing 
		"""

		self.__doc__			 = __doc__ 
		self.__version__ 		 = "0.1.0"
		self.__author__			 = ["Gholamali.Rahnavard", "YS Joseph Moon", "Curtis Huttenhower"]
		self.__contact__		 = "gholamali.rahnavard@gmail.com"

		self.hash_reduce_method = {"pca"	: stats.pca }

		self.hash_metric 		 = distance.c_hash_metric 

		self.keys_attribute = ["__description__", "__version__", "__author__", "__contact__", "q", "distance", "iterations", "reduce_method", "p_adjust_method", "randomization_method"]

		#==================================================================#
		# Presets
		#==================================================================#

		self.hash_preset = 	{"default"		: self.__preset_default, "HAllA": self.__preset_default, "HAllA-PCA-NMI": self.__preset_default,
								"time"		: self.__preset_time,
								"accuracy"	: self.__preset_accuracy,
								"parallel"	: self.__preset_parallel,
								"layerwise" : self.__preset_layerwise,
								"naive" 	: self.__preset_naive, "AllA" 	: self.__preset_naive, "AllA-NMI" 	: self.__preset_naive,
								"MIC"	: self.__preset_mic, "AllA-MIC"	: self.__preset_mic,
								"HAllA-PCA-MIC"	: self.__preset_pca_mic,
								"HAllA-PCA-AMI" : self.__preset_pca_adj_mi,
								"HAllA-ICA-NMI" : self.__preset_ica_norm_mi,
								"HAllA-ICA-MIC" : self.__preset_ica_mic,
								"kpca_norm_mi": self.__preset_kpca_norm_mi, "HAllA-KPCA-NMI": self.__preset_kpca_norm_mi,
								"kpca_pearson": self.__preset_kpca_pearson, "HAllA-KPCA-Pearson": self.__preset_kpca_pearson,
								"cca_pearson": self.__preset_cca_pearson, "HAllA-CCA-Pearson": self.__preset_cca_pearson,
								"cca_norm_mi": self.__preset_cca_norm_mi, "HAllA-CCA-NMI": self.__preset_cca_norm_mi,
								"pls_norm_mi": self.__preset_pls_norm_mi, "HAllA-PLS-NMI": self.__preset_pls_norm_mi,
								"pls_pearson": self.__preset_pls_pearson, "HAllA-PLS-Pearson": self.__preset_pls_pearson,
								"plsc_pearson": None,
								"plsc_norm_mi": None,
								"medoid_pearson": None,
								"medoid_norm_mi": self.__preset_medoid_norm_mi, "HAllA-Meoid-NMI": self.__preset_medoid_norm_mi,
								"full"		: self.__preset_full,
								"full_cca"	: self.__preset_full_cca,
								"full_kpca_norm_mi": self.__preset_full_kpca_norm_mi,
								"full_kpca_pearson": self.__preset_full_kpca_pearson,
								"multiple_representative": self.__preset_multiple_representative,
								"parametric_multiple_representative": self.__preset_parametric_multiple_representative,
								"parametric_test_by_representative": self.__preset_parametric_rep,
							}

		#==================================================================#
		# Global Defaults 
		#==================================================================#

		#==================================================================#
		# Mutable Meta Objects  
		#==================================================================#
		self.args = args
		(self.aDataSet1, self.aOutName1, self.aOutType1, self.aOutHead1) = aOutX 
		(self.aDataSet2, self.aOutName2, self.aOutType2, self.aOutHead2) = aOutY
		self.meta_array = array([None, None])
		self.meta_array[0] = array(self.aDataSet1)  # .append(X)
		self.meta_array[1] = array(self.aDataSet2)  # .append(Y)
		self.xlabels = self.aOutName1
		self.ylabels = self.aOutName2
		# print self.meta_array[0]
		# print self.meta_array[1]
		self.meta_feature = None
		self.meta_threshold = None 
		self.meta_data_tree = [] 
		self.meta_hypothesis_tree = None 
		self.meta_alla = None  # results of all-against-all
		self.meta_out = None  # final output array; some methods (e.g. all_against_all) have multiple outputs piped to both self.meta_alla and self.meta_out 
		self.meta_summary = None  # summary statistics 
		self.meta_report = None  # summary report 
		self.aOut = None  # summary output for naive approaches_

		# # END INIT 

	#==================================================================#
	# Type Checking
	#==================================================================#

	def _check(self, pObject, pType, pFun=isinstance, pClause="or"):
		"""
		Wrapper for type checking 
		"""

		if (isinstance(pType, list) or isinstance(pType, tuple) or isinstance(pType, np.ndarray)):
			aType = pType 
		else:
			aType = [pType]

		return reduce(lambda x, y: x or y, [isinstance(pObject, t) for t in aType], False)

	def _cross_check(self, pX, pY, pFun=len):
		"""
		Checks that pX and pY are consistent with each other, in terms of specified function pFun. 
		"""

	def _is_meta(self, pObject):
		"""	
		Is pObject an iterable of iterable? 
		"""

		try: 
			pObject[0]
			return self._is_iter(pObject[0])	
		except IndexError:
			return False 

	def _is_empty(self, pObject):
		"""
		Wrapper for both numpy arrays and regular lists 
		"""
		
		aObject = array(pObject)

		return not aObject.any()

	# ## These functions are absolutely unncessary; get rid of them! 
	def _is_list(self, pObject):
		return self._check(pObject, list)

	def _is_tuple(self, pObject):
		return self._check(pObject, tuple)

	def _is_str(self, pObject):
		return self._check(pObject, str)

	def _is_int(self, pObject):
		return self._check(pObject, int)    

	def _is_array(self, pObject):
		return self._check(pObject, np.ndarray)

	def _is_1d(self, pObject):
		"""
		>>> import strudel 
		>>> s = strudel.Strudel( )
		>>> s._is_1d( [] )
		"""

		strErrorMessage = "Object empty; cannot determine type"
		bEmpty = self._is_empty(pObject)

		# # Enforce non-empty invariance 
		if bEmpty:
			raise Exception(strErrorMessage)

		# # Assume that pObject is non-empty 
		try:
			iRow, iCol = pObject.shape 
			return(iRow == 1) 
		except ValueError:  # # actual arrays but are 1-dimensional
			return True
		except AttributeError:  # # not actual arrays but python lists 
			return not self._is_iter(pObject[0])

	def _is_iter(self, pObject):
		"""
		Is the object a list or tuple? 
		Disqualify string as a true "iterable" in this sense 
		"""

		return self._check(pObject, [list, tuple, np.ndarray])

	#==========================================================#
	# Static Methods 
	#==========================================================# 

	@staticmethod 
	def m(pArray, pFunc, axis=0):
		""" 
		Maps pFunc over the array pArray 
		"""

		if bool(axis): 
			pArray = pArray.T
			# Set the axis as per numpy convention 
		if isinstance(pFunc , np.ndarray):
			return pArray[pFunc]
		else:  # generic function type
			# print pArray.shape
			return array([pFunc(item) for item in pArray]) 

	@staticmethod 
	def bp(pArray, pFunc, axis=0):
		"""
		Map _by pairs_ ; i.e. apply pFunc over all possible pairs in pArray 
		"""

		if bool(axis): 
			pArray = pArray.T

		pIndices = itertools.combinations(range(pArray.shape[0]), 2)

		return array([pFunc(pArray[i], pArray[j]) for i, j in pIndices])

	@staticmethod 
	def bc(pArray1, pArray2, pFunc, axis=0):
		"""
		Map _by cross product_ for ; i.e. apply pFunc over all possible pairs in pArray1 X pArray2 
		"""

		if bool(axis): 
			pArray1, pArray2 = pArray1.T, pArray2.T

		pIndices = itertools.product(range(pArray1.shape[0]), range(pArray2.shape[0]))

		return array([pFunc(pArray1[i], pArray2[j]) for i, j in pIndices])

	@staticmethod 
	def r(pArray, pFunc, axis=0):
		"""
		Reduce over array 

		pFunc is X x Y -> R 

		"""
		if bool(axis):
			pArray = pArray.T

		return reduce(pFunc, pArray)

	@staticmethod 
	def rd():
		"""
		General reduce-dimension method 
		"""
		pass 

	#==========================================================#
	# Helper Functions 
	#==========================================================# 

	def _discretize(self):
		self.meta_feature = self.m(self.meta_array, stats.discretize)
		# Should do a better job at detecting whether dataset is categorical or continuous
		# Take information from the parser module 
		return self.meta_feature

	def _featurize(self, strMethod="_discretize"):
		pMethod = None 
		try:
			pMethod = getattr(self, strMethod)
		except AttributeError:
			raise Exception("Invalid Method.")

		if pMethod:
			return pMethod()

	def _hclust(self):
		# print self.meta_feature
		self.meta_data_tree.append(hierarchy.hclust(self.meta_feature[0] , labels=self.xlabels, bTree=True))
		self.meta_data_tree.append(hierarchy.hclust(self.meta_feature[1] , labels=self.ylabels, bTree=True))
		# self.meta_data_tree = self.m( self.meta_feature, lambda x: hclust(x , bTree=True) )
		# print self.meta_data_tree
		return self.meta_data_tree 

	def _couple(self):
		# self.meta_hypothesis_tree = self.m( 
		 # self.bp( 
		  # self.m(self.meta_data_tree, lambda x: [x]), 
		   # couple_tree ), 
			# lambda y: y[0] ) 
		
		self.meta_hypothesis_tree = hierarchy.couple_tree(apClusterNode1=[self.meta_data_tree[0]],
				apClusterNode2=[self.meta_data_tree[1]],
				pArray1=self.meta_feature[0], pArray2=self.meta_feature[1], func=self.distance)[0]
		
		# # remember, `couple_tree` returns object wrapped in list 
		return self.meta_hypothesis_tree 

	def _naive_all_against_all(self, iIter=100):
		self.meta_alla = hierarchy.naive_all_against_all(self.meta_array[0], self.meta_array[1], iIter=iIter)
		return self.meta_alla 
	def _all_against_all(self, strMethod="permutation_test_by_representative", iIter=None):
		if not iIter:
			iIter = self.iterations 

		assert(type(iIter) == int)
		fQ = self.q
		
		if self.verbose:
			print ("HAllA PROMPT: q value", fQ)
			print ("q value is", fQ)
		self.meta_alla = hierarchy.all_against_all(self.meta_hypothesis_tree, self.meta_feature[0], self.meta_feature[1], method=strMethod, fQ=self.q, bVerbose=self.verbose) 
		# # Choose to keep to 2 arrays for now -- change later to generalize 
		return self.meta_alla 
	
	def _naive_all_against_all_mic(self, iIter=100):
		self.meta_alla = hierarchy.naive_all_against_all(self.meta_array[0], self.meta_array[1], strMethod="permutation_test_by_representative_mic", iIter=iIter)
		return self.meta_alla

	def _layerwise_all_against_all(self):

		X, Y = self.meta_array[0], self.meta_array[1]
		dX, dY = self.meta_feature[0], self.meta_feature[1]
		tX, tY = self.meta_data_tree[0], self.meta_data_tree[1]
		iX, iY = X.shape[0], Y.shape[0]

		aOut = filter(bool, list(hierarchy.layerwise_all_against_all(tX, tY, X, Y)))

		aMetaOut = [] 

		def _layer(Z):

			S = -1 * np.ones((iX, iY))  # # matrix of all associations; symmetric if using a symmetric measure of association  

			def __add_pval_product_wise(_x, _y, _fP):
				S[_x][_y] = _fP ; S[_y][_x] = _fP 

			def __get_pval_from_bags(_Z, _strMethod='final'):
				"""
				
				_strMethod: str 
					{"default",}

				The default option does the following: go through the bags, treating the p-value for each bag pair as applying to all the variables inside the bag. 
				If new instance arises (e.g. [[3],[5]] following [[3,5,6],[3,5,6]] ), override the p-value to the one with more precision. 
				"""

				for aLine in _Z:
					if self.verbose:
						print (aLine) 
					# break
					aaBag, fAssoc = aLine
					aBag1, aBag2 = aaBag 
					aBag1, aBag2 = array(aBag1), array(aBag2)
					self.bc(aBag1, aBag2, pFunc=lambda x, y: __add_pval_product_wise(_x=x, _y=y, _fP=fAssoc))

			__get_pval_from_bags(Z)
			return S 		

		for Z in aOut:
			aMetaOut.append(_layer(Z))

		return aMetaOut
	def _naive_summary_statistics(self):
		_, p_values = zip(*self.aOut[0])
		self.meta_summary = []
		self.meta_summary.append(np.reshape([p_values], (int(math.sqrt(len(p_values))), int(math.sqrt(len(p_values))))))


	def _summary_statistics(self, strMethod=None): 
		"""
		provides summary statistics on the output given by _all_against_all 
		"""

		if not strMethod:
			strMethod = self.summary_method
		# print('meta array:')
		# print(self.meta_array[0])
		# print(self.meta_array[1])	
		X = self.meta_array[0]
		Y = self.meta_array[1]
		iX, iY = X.shape[0], Y.shape[0]
		
		S = -1 * np.ones((iX, iY , 2))  # # matrix of all associations; symmetric if using a symmetric measure of association  
		
		Z = self.meta_alla 
		Z_final, Z_all = map(array, Z)  # # Z_final is the final bags that passed criteria; Z_all is all the associations delineated throughout computational tree
				
		# ## Sort the final Z to make sure p-value consolidation happens correctly 
		Z_final_dummy = [-1.0 * (len(line[0][0]) + len(line[0][1])) for line in Z_final]
		args_sorted = np.argsort(Z_final_dummy)
		Z_final = Z_final[args_sorted]
		if self.verbose:
			print (Z_final) 
		# assert( Z_all.any() ), "association bags empty." ## Technically, Z_final could be empty 
		'''
		self.outcome = np.zeros((len(self.meta_feature[0]),len(self.meta_feature[1])))
		#print(self.outcome)
		for l in range(len(Z_final)):
			#print(Z_final[l][0][0],Z_final[l][0][0], Z_final[l][1])
			if Z_final[l][1] < self.q:
				for i, j in product(Z_final[l][0][0], Z_final[l][0][1]):
					#for j in Z_final[l][0][1]:
					self.outcome[i][j] = 1
		#print(self.outcome)
		'''
		def __add_pval_product_wise(_x, _y, _fP, _fP_adjust):
			S[_x][_y][0] = _fP
			S[_x][_y][1] = _fP_adjust  

		def __get_conditional_pval_from_bags(_Z, _strMethod=None):
			"""
			
			_strMethod: str 
				{"default",}

			The default option does the following: go through the bags, treating the p-value for each bag pair as applying to all the variables inside the bag. 
			If new instance arises (e.g. [[3],[5]] following [[3,5,6],[3,5,6]] ), override the p-value to the one with more precision. 
			"""

			for aLine in _Z:
				if self.verbose:
					print (aLine) 
				
				aaBag, fAssoc, fP_adjust = aLine
				listBag1, listBag2 = aaBag 
				aBag1, aBag2 = array(listBag1), array(listBag2)
				
				for i, j in itertools.product(listBag1, listBag2):
					S[i][j][0] = fAssoc 
					S[i][j][1] = fP_adjust

		def __get_pval_from_bags(_Z, _strMethod='final'):
			"""
			
			_strMethod: str 
				{"default",}

			The default option does the following: go through the bags, treating the p-value for each bag pair as applying to all the variables inside the bag. 
			If new instance arises (e.g. [[3],[5]] following [[3,5,6],[3,5,6]] ), override the p-value to the one with more precision. 
			"""

			for aLine in _Z:
				if self.verbose:
					print (aLine) 
				
				aaBag, fAssoc, P_adjust = aLine
				aBag1, aBag2 = aaBag 
				aBag1, aBag2 = array(aBag1), array(aBag2)
				self.bc(aBag1, aBag2, pFunc=lambda x, y: __add_pval_product_wise(_x=x, _y=y, _fP=fAssoc, _fP_adjust=P_adjust))

		if strMethod == "final":
			if self.verbose:
				print ("Using only final p-values")
			__get_conditional_pval_from_bags(Z_final)
			assert(S.any())
			self.meta_summary = S
			return self.meta_summary

		elif strMethod == "all":
			if self.verbose:
				print ("Using all p-values")
			__get_conditional_pval_from_bags(Z_all)
			assert(S.any())
			self.meta_summary = S
			return self.meta_summary

	def _plot(self):
		"""
		Wrapper for plotting facilities
		"""

	def _report(self):
		"""
		helper function for reporting the output to the user,
		"""

		aaOut = []

		# self.meta_report = [] 

		aP = self.meta_summary
		iRow1 = self.meta_array[0].shape[0]
		iRow2 = self.meta_array[1].shape[0]

		for i, j in itertools.product(range(iRow1), range(iRow2)):
			# ## i <= j 
			fQ = aP[i][j][0] 
			fQ_adust = aP[i][j][1] 
			if fQ != -1:
				aaOut.append([[i, j], fQ, fQ_adust ])

		self.meta_report = aaOut
		# print "meta summary:", self.meta_report
		istm = list()  # We are using now X and Y 
 	
		#***************************************************************
		# We are using now X and Y - If Y was not set - we use X        *
		#***************************************************************
		if self.args.Y == None:
			istm = [self.args.X, self.args.X]  # Use X  
		else:
			istm = [self.args.X, self.args.Y]  # Use X and Y
	
		
		if len(istm) > 1:
			strFile1, strFile2 = istm[:2]
		else:
			strFile1, strFile2 = istm[0], istm[0]
		csvw = csv.writer(self.args.ostm, csv.excel_tab)
		bcsvw = csv.writer(self.args.bostm, csv.excel_tab)
		csvw.writerow(["Method: " + self.args.strPreset, "q value: " + str(self.args.dQ), "metric " + self.args.strMetric])
		bcsvw.writerow(["Method: " + self.args.strPreset, "q value: " + str(self.args.dQ), "metric " + self.args.strMetric])
		
		if self.args.Y == None:
			csvw.writerow([istm[0].name, istm[0].name, "nominal-pvalue", "adjusted-pvalue"])
			bcsvw.writerow([istm[0].name, istm[0].name, "nominal-pvalue", "adjusted-pvalue"])
		else:
			csvw.writerow([self.args.X.name, self.args.Y.name, "nominal-pvalue", "adjusted-pvalue"])
			bcsvw.writerow(["Association Number", self.args.X.name, self.args.Y.name, "nominal-pvalue", "adjusted-pvalue"])

		for line in aaOut:
			iX, iY = line[0]
			fP = line[1]
			fP_adjust = line[2]
			aLineOut = map(str, [self.aOutName1[iX], self.aOutName2[iY], fP, fP_adjust])
			csvw.writerow(aLineOut)
		# print 'H:', self.meta_alla
		# print 'H[0]', self.meta_alla[0]
		associated_feature_X_indecies = []
		associated_feature_Y_indecies = []
		association_number = 0 
		
		for line in self.meta_alla[0]:
			association_number += 1
			filename = "./output/" + "association" + str(association_number) + '/'
			dir = os.path.dirname(filename)
			try:
				shutil.rmtree(dir)
				os.mkdir(dir)
			except:
				os.mkdir(dir)
				
			iX, iY = line[0]
			associated_feature_X_indecies += iX
			associated_feature_Y_indecies += iY
			fP = line[1]
			fP_adjust = line[2]
			aLineOut = map(str, [association_number, str(';'.join(self.aOutName1[i] for i in iX)), str(';'.join(self.aOutName2[i] for i in iY)), fP, fP_adjust])
			bcsvw.writerow(aLineOut)
			# import pandas as pd
			import matplotlib.pyplot as plt 
			plt.figure()
			cluster1 = [self.aDataSet1[i] for i in iX]
			X_labels = np.array([self.aOutName1[i] for i in iX])
			# cluster = np.array([aOutData1[i] for i in iX]
			# df = pd.DataFrame(np.array(cluster1, dtype= float).T ,columns=X_labels )
			# axes = pd.tools.plotting.scatter_matrix(df)
			
			# plt.tight_layout()
			
			plt.savefig(filename + 'Dataset_1_cluster_' + str(association_number) + '_scatter_matrix.pdf')
			cluster2 = [self.aDataSet2[i] for i in iY]
			Y_labels = np.array([self.aOutName2[i] for i in iY])
			plt.figure()
			# df = pd.DataFrame(np.array(cluster2, dtype= float).T ,columns=Y_labels )
			# axes = pd.tools.plotting.scatter_matrix(df)
			# plt.tight_layout()
			plt.savefig(filename + 'Dataset_2_cluster_' + str(association_number) + '_scatter_matrix.pdf')
			df1 = np.array(cluster1, dtype=float)
			df2 = np.array(cluster2, dtype=float)
			plt.figure()
			plt.scatter(stats.pca(df1), stats.pca(df2), alpha=0.5)
			plt.savefig(filename + '/association_' + str(association_number) + '.pdf')
			# plt.figure()
			plt.close("all")
		
		
		csvwc = csv.writer(self.args.costm , csv.excel_tab)
		csvwc.writerow(['Level', "Dataset 1", "Dataset 2" ])
		for line in hierarchy.reduce_tree_by_layer([self.meta_hypothesis_tree]):
			(level, clusters) = line
			iX, iY = clusters[0], clusters[1]
			fP = line[1]
			# fP_adjust = line[2]
			aLineOut = map(str, [str(level), str(';'.join(self.aOutName1[i] for i in iX)), str(';'.join(self.aOutName2[i] for i in iY))])
			csvwc.writerow(aLineOut)
		print "R visualization!"
		from scipy.stats.stats import pearsonr
		X_labels = np.array([self.aOutName1[i] for i in associated_feature_X_indecies])
		Y_labels = np.array([self.aOutName2[i] for i in associated_feature_Y_indecies])
		cluster1 = [self.aDataSet1[i] for i in associated_feature_X_indecies]	
		cluster2 = [self.aDataSet2[i] for i in associated_feature_Y_indecies]
		df1 = np.array(cluster1, dtype=float)
		df2 = np.array(cluster2, dtype=float)
		p = np.zeros(shape=(len(associated_feature_X_indecies), len(associated_feature_Y_indecies)))
		for i in range(len(associated_feature_X_indecies)):
			for j in range(len(associated_feature_Y_indecies)):
				p[i][j] = pearsonr(df1[i], df2[j])[0]
		nmi = np.zeros(shape=(len(associated_feature_X_indecies), len(associated_feature_Y_indecies)))
		for i in range(len(associated_feature_X_indecies)):
			for j in range(len(associated_feature_Y_indecies)):
				nmi[i][j] = distance.NormalizedMutualInformation(stats.discretize(df1[i]), stats.discretize(df2[j])).get_distance()
		'''rpy2.robjects.numpy2ri.activate()
		ro.r('library("gplots")')
		ro.globalenv['nmi'] = nmi
		ro.globalenv['labRow'] = X_labels 
		ro.globalenv['labCol'] = Y_labels
		ro.r('pdf(file = "./output/NMI_heatmap.pdf")')
		ro.r('heatmap.2(nmi, labRow = labRow, labCol = labCol, col=redgreen(75), scale="row",  key=TRUE, symkey=FALSE, density.info="none", trace="none", cexRow=0.5)')
		ro.r('dev.off()')
		ro.globalenv['p'] = p
		ro.r('pdf(file = "./output/Pearson_heatmap.pdf")')
		ro.r('heatmap.2(p, , labRow = labRow, labCol = labCol, , col=redgreen(75), scale="column",  key=TRUE, symkey=FALSE, density.info="none", trace="none", cexRow=0.5)')
		ro.r('dev.off()')'''
		# set_default_mode(NO_CONVERSION)
		# rpy2.library("ALL")
		# hm = halla.plot.hclust2.Heatmap( p)#, cl.sdendrogram, cl.fdendrogram, snames, fnames, fnames_meta, args = args )
		# hm.draw()
		# halla.plot.heatmap(D = p, filename ='./output/pearson_heatmap')
		# halla.plot.heatmap(D = nmi, filename ='./output/nmi_heatmap')
		return self.meta_report 

	def _run(self):
		"""
		helper function: runs vanilla run of HAllA _as is_. 
		"""

		pass 

	#==========================================================#
	# Load and set data 
	#==========================================================# 

	def set_data(self, *ta):
		if ta:
			self.meta_array = ta 
			return self.meta_array 
		else:
			raise Exception("Data empty")


	#==========================================================#
	# Set parameters 
	#==========================================================# 

	def set_q(self, fQ):
		self.q = fQ

	def set_summary_method(self, strMethod):
		self.summary_method = strMethod 
		return self.summary_method 

	def set_p_adjust_method(self, strMethod):
		"""
		Set multiple hypothesis test correction method 

			{"BH", "FDR", "Bonferroni", "BHY"}
		"""

		self.p_adjust_method = strMethod 
		return self.p_adjust_method 

	def set_metric(self, pMetric):
		if isinstance(pMetric, str):
			self.distance = self.hash_metric[pMetric]
		else:
			self.distance = pMetric 
		return self.distance 

	def set_reduce_method(self, strMethod):
		if isinstance(strMethod, str):
			self.reduce_method = self.hash_reduce_method[strMethod]
		else:
			self.reduce_method = strMethod 
		return self.reduce_method

	def set_iterations(self, iIterations):
		self.iterations = iIterations
		return self.iterations 

	def set_randomization_method(self, strMethod):

		self.randomization_method = strMethod 
		return self.randomization_method 

	def set_exploration_function(self, strFunction):
		self.exploration_function = strFunction

	def set_verbose(self, bBool=True):
		self.verbose = bBool 

	def set_preset(self, strPreset):
		try:
			pPreset = self.hash_preset[strPreset] 
			pPreset()  # # run method 
		except KeyError:
			raise Exception("Preset not found. For the default preset, try set_preset('default')")

	#==========================================================#
	# Presets  
	#==========================================================# 
	"""
	These are hard-coded presets deemed useful for the user 
	"""

	######NEW PRESETS 
	# permutation_test_by_representative  -> norm_mi 
	# permutation_test_by_kpca_norm_mi -> 
	# permutation_test_by_kpca_pearson
	# permutation_test_by_cca_pearson 
	# permutation_test_by_cca_norm_mi 

	def __preset_medoid_norm_mi(self):

		pDistance = distance.norm_mi
		self.set_metric(pDistance)
		
		self._featurize()
		self._threshold()
		self._hclust()
		self._couple()
		self._all_against_all(strMethod="permutation_test_by_medoid") 
		self._summary_statistics() 
		return self._report() 

	def __preset_parametric_rep(self):

		self._featurize()
		self._threshold()
		self._hclust()
		self._couple()
		self._all_against_all(strMethod="parametric_test_by_representative") 
		self._summary_statistics() 
		return self._report()  
	
	def __preset_pca_mic(self):
		pDistance = distance.mic
		self.set_metric(pDistance)
		self._featurize()
		# self._threshold( )
		self._hclust()
		self._couple()
		self._all_against_all(strMethod="permutation_test_by_representative_mic") 
		self._summary_statistics('final') 
		return self._report()  
	
	# step 2 to add a new method for HAllA
	def __preset_ica_norm_mi(self):
		pDistance = distance.norm_mi
		self.set_metric(pDistance)
		self._featurize()
		# self._threshold( )
		self._hclust()
		self._couple()
		self._all_against_all(strMethod="permutation_test_by_ica_norm_mi") 
		self._summary_statistics('final') 
		return self._report() 
	
	def __preset_ica_mic(self):
		pDistance = distance.mic
		self.set_metric(pDistance)
		self._featurize()
		# self._threshold( )
		self._hclust()
		self._couple()
		self._all_against_all(strMethod="permutation_test_by_ica_mic") 
		self._summary_statistics() 
		return self._report() 
	def __preset_kpca_norm_mi(self):
		pDistance = distance.norm_mi
		self.set_metric(pDistance)
		
		self._featurize()
		# self._threshold( )
		self._hclust()
		self._couple()
		self._all_against_all(strMethod="permutation_test_by_kpca_norm_mi") 
		self._summary_statistics('final') 
		return self._report()  

	def __preset_kpca_pearson(self):
		pDistance = distance.pearson
		self.set_metric(pDistance)
		self._featurize()
		# self._threshold( )
		self._hclust()
		self._couple()
		self._all_against_all(strMethod="permutation_test_by_kpca_pearson") 
		self._summary_statistics('final') 
		return self._report() 

	def __preset_cca_pearson(self):
		pDistance = distance.pearson
		self.set_metric(pDistance)
		self._featurize()
		# self._threshold( )
		self._hclust()
		self._couple()
		self._all_against_all(strMethod="permutation_test_by_cca_pearson") 
		self._summary_statistics('final') 
		return self._report() 

	def __preset_pls_pearson(self):
		pDistance = distance.pearson
		self.set_metric(pDistance)
		self._featurize()
		# self._threshold( )
		self._hclust()
		self._couple()
		self._all_against_all(strMethod="parametric_test_by_pls_pearson") 
		self._summary_statistics('final') 
		return self._report() 


	def __preset_pls_norm_mi(self):
		pDistance = distance.norm_mi
		self.set_metric(pDistance)
		self._featurize()
		# self._threshold( )
		self._hclust()
		self._couple()
		self._all_against_all(strMethod="permutation_test_by_pls_norm_mi") 
		self._summary_statistics('final') 
		return self._report() 


	def __preset_cca_norm_mi(self):
		# # Constants for this preset 
		pDistance = distance.norm_mi
		self.set_metric(pDistance)
		# pDistance = norm_mi 
		# iIter = 100
		# strReduce = "pca"
		# strAdjust = "BH"
		# strRandomization = "permutation"

		# # Run 		
		self._featurize()
		# self._threshold( )
		self._hclust()
		self._couple()
		self._all_against_all(strMethod="permutation_test_by_cca_norm_mi") 
		self._summary_statistics('final') 
		return self._report() 


	######END 


	def __preset_layerwise(self):
		"""
		Layerwise MI preset 
		"""

		# # Constants for this preset 

		pDistance = distance.norm_mi 
		iIter = 100
		strReduce = "pca"
		strStep = "uniform"
		strAdjust = "BH"
		strRandomization = "permutation"
		strExplorationFunction = "layerwise"

		# # Set 
		self.set_metric(pDistance)
		self.set_reduce_method(strReduce)
		self.set_p_adjust_method(strAdjust)
		self.set_randomization_method(strRandomization)
		self.set_exploration_function(strExplorationFunction)

		# # Run 		
		self._featurize()
		# self._threshold( )
		self._hclust()

		# self._couple( )
		# self._all_against_all( )
		return self._layerwise_all_against_all()
		# self._summary_statistics( )
		# return self._report( )

	def __preset_parametric_multiple_representative(self):

		# # Run 		
		self._featurize()
		# self._threshold( )
		self._hclust()
		self._couple()
		self._all_against_all(strMethod="parametric_test_by_multiple_representative") 
		self._summary_statistics("all") 
		return self._report()

	def __preset_multiple_representative(self):

		# # Constants for this preset 
		pDistance = distance.norm_mi 
		strReduce = "pca"
		strStep = "uniform"
		strAdjust = "BH"
		strRandomization = "permutation"

		# # Set 
		self.set_metric(pDistance)
		self.set_reduce_method(strReduce)
		self.set_p_adjust_method(strAdjust)
		self.set_randomization_method(strRandomization)

		# # Run 		
		self._featurize()
		# self._threshold( )
		self._hclust()
		self._couple()
		self._all_against_all(strMethod="permutation_test_by_multiple_representative") 
		# self._summary_statistics( "all" ) 
		# return self._report( )

	def __preset_norm_mi(self):
		"""
		Mutual Information Preset 
		"""
		# # Constants for this preset 
		pDistance = distance.norm_mi 
		strReduce = "pca"
		strStep = "uniform"
		strAdjust = "BH"
		strRandomization = "permutation"

		# # Set 
		self.set_metric(pDistance)
		self.set_reduce_method(strReduce)
		self.set_p_adjust_method(strAdjust)
		self.set_randomization_method(strRandomization)

		# # Run 
		start_time = time.time()
		self._featurize()
		print("--- %s seconds: _featurize ---" % (time.time() - start_time))
		start_time = time.time()
		# #self._threshold( )
		# print("--- %s seconds: _threshold ---" % (time.time() - start_time))
		start_time = time.time()
		self._hclust()
		print("--- %s seconds: _hclust ---" % (time.time() - start_time))
		start_time = time.time()
		self._couple()
		print("--- %s seconds: _couple ---" % (time.time() - start_time))
		print("Association hypotheses testing is started ...")
		print("This task may take longer ...")
		start_time = time.time()
		self._all_against_all()
		print("--- %s seconds: _hypothesis testing ---" % (time.time() - start_time))
		start_time = time.time() 
		self._summary_statistics('final') 
		print("--- %s seconds: _summary_statistics ---" % (time.time() - start_time))
		start_time = time.time()
		return self._report()
	
	def __preset_pca_adj_mi(self):
		"""
		Adjusted Mutual Information Preset 
		"""
		# # Constants for this preset 
		pDistance = distance.adj_mi 
		strReduce = "pca"
		strStep = "uniform"
		strAdjust = "BH"
		strRandomization = "permutation"

		# # Set 
		self.set_metric(pDistance)
		self.set_reduce_method(strReduce)
		self.set_p_adjust_method(strAdjust)
		self.set_randomization_method(strRandomization)

		# # Run 		
		self._featurize()
		# self._threshold( )
		self._hclust()
		self._couple()
		self._all_against_all(strMethod="permutation_test_by_representative_adj_mi") 
		self._summary_statistics('final') 
		return self._report()

	def __preset_full(self):
		"""
		Give full-pvalue matrix;
		useful for evaluating the full AUC
		"""

		# # Constants for this preset 
		pDistance = distance.norm_mi 
		strReduce = "pca"
		strStep = "uniform"
		strAdjust = "BH"
		strRandomization = "permutation"

		# # Set 
		self.set_metric(pDistance)
		self.set_reduce_method(strReduce)
		self.set_p_adjust_method(strAdjust)
		self.set_randomization_method(strRandomization)

		# # Run 		
		self._featurize()
		# self._threshold( )
		self._hclust()
		self._couple()
		self._all_against_all() 
		return self._summary_statistics("all") 


	def __preset_full_cca(self):
		self._featurize()
		# self._threshold( )
		self._hclust()
		self._couple()
		self._all_against_all(strMethod="permutation_test_by_cca_pearson") 
		return self._summary_statistics("all") 

	def __preset_full_kpca_norm_mi(self):

		self._featurize()
		# self._threshold( )
		self._hclust()
		self._couple()
		self._all_against_all(strMethod="permutation_test_by_kpca_norm_mi") 
		return self._summary_statistics("all") 

	def __preset_full_kpca_pearson(self):

		self._featurize()
		# self._threshold( )
		self._hclust()
		self._couple()
		self._all_against_all(strMethod="permutation_test_by_kpca_pearson") 
		return self._summary_statistics("all") 

	def __preset_default(self):
		return self.__preset_norm_mi()
		# return self.__preset_layerwise( )

	def __preset_time(self):
		pass 

	def __preset_accuracy(self):
		# # Constants for this preset 

		pDistance = distance.adj_mi 
		iIter = 1000
		strReduce = "pca"
		strStep = "uniform"
		strAdjust = "BH"
		strRandomization = "permutation"

		# # Set 

		self.set_metric(distance.adj_mi)
		self.set_iterations(iIter)
		self.set_reduce_method(strReduce)
		self.set_p_adjust_method(strAdjust)
		self.set_randomization_method(strRandomization)

		# # Run 
		self._featurize()
		# self._threshold( )
		self._hclust()
		self._couple()
		return self._all_against_all()
 
	def __preset_parallel(self):
		pass 

	def __preset_naive(self):
		"""
		All against all 
		"""
		self._featurize()
		# print self.iterations 
		Out = self._naive_all_against_all(iIter=self.iterations)
		self.aOut = [Out]
		self._naive_summary_statistics()
		return self.aOut
	def __preset_mic(self):
		"""
		All against all using Maximum Information Coefficient 
		"""
		self._featurize()
		# print self.iterations 
		Out = self._naive_all_against_all_mic(iIter=self.iterations)
		self.aOut = [Out]
		self._naive_summary_statistics()
		return self.aOut

	#==========================================================#
	# Public Functions / Main Pipeline  
	#==========================================================# 	

	def load_data(self):
		pass 

	def get_data(self):
		return self.meta_array 

	def get_feature(self):
		return self.meta_feature

	def get_tree(self):
		return self.meta_data_tree

	def get_hypothesis(self):
		return self.meta_hypothesis_tree

	def get_association(self):
		return self.meta_alla 

	def get_attribute(self):
		"""
		returns current attributes and statistics about HAllA object implementation 

			* Print parameters in a text-table style 
		"""
		
		for item in self.keys_attribute:
			sys.stderr.write("\t".join([item, str(getattr(self, item))]) + "\n") 

	def run(self, strMethod="default"):
		"""
		Main run module 

		Parameters
		------------

			method : str 
				Specifies what method to use; e.g. which preset to follow 
				{"default", "custom", "time", "accuracy", "parallel"}

				* Custom: 
				* Default:  

		Returns 
		-----------

			Z : HAllA output object 
		
		Notes 
		---------

		* Main steps

			+ Parse input and clean data 
			+ Feature selection (discretization for MI, beta warping, copula selection)
			+ Hierarchical clustering 
			+ Hypothesis generation (tree coupling via appropriate step function)
			+ Hypothesis testing and agglomeration of test statistics, with multiple hypothesis correction 
			+ Parse output 

		* Visually, looks much nicer and is much nicely wrapped if functions are entirely self-contained and we do not have to pass around pointers 

		"""

		if self.q == 1.0:
			strMethod = "naive"
			return self.hash_preset[strMethod]()
		else:
			try:
				pMethod = self.hash_preset[strMethod]
				# print "Preset:", pMethod
				return pMethod()
			except KeyError:			
				raise Exception("Invalid Method.")

	def view_singleton(self, pBags):
		aOut = [] 
		for aIndices, fP in pBags:
			if len(aIndices[0]) == 1 and len(aIndices[1]) == 1:
				aOut.append([aIndices, fP])
		return aOut 



