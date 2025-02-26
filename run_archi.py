#!/usr/bin/python

import os, sys
import argparse
import random

#from deeplearning.architecture_complexity import * #--- to be changed to test other configurations
# from deeplearning.architecture_rnn import * #--- to be changed to test other configurations
#from deeplearning.architecture_depth import * #--- to be changed to test other configurations
#from deeplearning.architecture_batchsize import * #--- to be changed to test other configurations
from deeplearning.architecture_pooling import * #--- to be changed to test other configurations
from outputfiles.save import *
from outputfiles.evaluation import *
from sits.readingsits import *


#-----------------------------------------------------------------------		
def main(sits_path, res_path, feature, noarchi, norun, seed):
	
	#-- Creating output path if does not exist
	if not os.path.exists(res_path):
		os.makedirs(res_path)
	
	#---- Parameters to set
	n_channels = 16 #-- NIR, R, G
	#val_rate = 0.05
	
	#---- Evaluated metrics
	eval_label = ['OA', 'train_loss', 'train_time', 'test_time']	
	
	#---- String variables
	train_str = f'train-{seed}'
	# test_str = 'test_dataset'					
	# #---- Get filenames
	# train_file = sits_path + '/' + train_str + '.csv'
	# test_file = sits_path + '/' + test_str + '.csv'
	# print("train_file: ", train_file)
	# print("test_file: ", test_file)

	#---- output files			
	res_path = res_path + '/Archi' + str(noarchi) + '/'
	if not os.path.exists(res_path):
		os.makedirs(res_path)
	print("noarchi: ", noarchi)
	str_result = feature + '-' + train_str + '-noarchi' + str(noarchi) + '-norun' + str(norun) 
	res_file = res_path + '/resultOA-' + str_result + '.csv'
	res_mat = np.zeros((len(eval_label),1))	
	traintest_loss_file = res_path + '/trainingHistory-' + str_result + '.csv'
	conf_file = res_path + '/confMatrix-' + str_result + '.csv'
	out_model_file = res_path + '/bestmodel-' + str_result + '.h5'

	#---- Downloading
	# X_train, polygon_ids_train, y_train = readSITSData(train_file)
	# X_test,  polygon_ids_test, y_test = readSITSData(test_file)
	
	# n_classes_test = len(np.unique(y_test))
	# n_classes_train = len(np.unique(y_train))
	# if(n_classes_test != n_classes_train):
	# 	print("WARNING: different number of classes in train and test")
	# n_classes = max(n_classes_train, n_classes_test)
	# y_train_one_hot = to_categorical(y_train, n_classes)
	# y_test_one_hot = to_categorical(y_test, n_classes)			
	
	# #---- Adding the features and reshaping the data if necessary
	# X_train = addingfeat_reshape_data(X_train, feature, n_channels)
	# X_test = addingfeat_reshape_data(X_test, feature, n_channels)		
	
		
	# #---- Normalizing the data per band
	# minMaxVal_file = '.'.join(out_model_file.split('.')[0:-1])
	# minMaxVal_file = minMaxVal_file + '_minMax.txt'
	# if not os.path.exists(minMaxVal_file): 
	# 	min_per, max_per = computingMinMax(X_train)
	# 	save_minMaxVal(minMaxVal_file, min_per, max_per)
	# else:
	# 	min_per, max_per = read_minMaxVal(minMaxVal_file)
	# X_train =  normalizingData(X_train, min_per, max_per)
	# X_test =  normalizingData(X_test, min_per, max_per)
	
	# #---- Extracting a validation set (if necesary)
	# if val_rate > 0:
	# 	X_train, y_train, X_val, y_val = extractValSet(X_train, polygon_ids_train, y_train, val_rate)
	# 	#--- Computing the one-hot encoding (recomputing it for train)
	# 	y_train_one_hot = to_categorical(y_train, n_classes)
	# 	y_val_one_hot = to_categorical(y_val, n_classes)

	X_train, X_val, X_test, y_train, y_val, y_test = load_train_val_test(seed, False)
	n_classes = len(np.unique(y_test))

	y_train_one_hot = to_categorical(y_train, n_classes)
	y_val_one_hot = to_categorical(y_val, n_classes)
	y_test_one_hot = to_categorical(y_test, n_classes)

	#---- Adding the features and reshaping the data if necessary
	X_train = addingfeat_reshape_data(X_train, feature, n_channels)
	X_val = addingfeat_reshape_data(X_val, feature, n_channels)
	X_test = addingfeat_reshape_data(X_test, feature, n_channels)

	#---- Normalizing the data per band
	minMaxVal_file = '.'.join(out_model_file.split('.')[0:-1])
	minMaxVal_file = minMaxVal_file + '_minMax.txt'
	if not os.path.exists(minMaxVal_file): 
		min_per, max_per = computingMinMax(X_train)
		save_minMaxVal(minMaxVal_file, min_per, max_per)
	else:
		min_per, max_per = read_minMaxVal(minMaxVal_file)

	X_train =  normalizingData(X_train, min_per, max_per)
	X_val =  normalizingData(X_val, min_per, max_per)
	X_test =  normalizingData(X_test, min_per, max_per)

	
	if not os.path.isfile(res_file):
		# if val_rate==0:
		# 	res_mat[0,norun], res_mat[1,norun], model, model_hist, res_mat[2,norun], res_mat[3,norun] = \
		# 		runArchi(noarchi, X_train, y_train_one_hot, X_test, y_test_one_hot, out_model_file)
		# else:
		res_mat[0,norun], res_mat[1,norun], model, model_hist, res_mat[2,norun], res_mat[3,norun] = \
			runArchi(noarchi, X_train, y_train_one_hot, X_val, y_val_one_hot, X_test, y_test_one_hot, out_model_file)

		saveLossAcc(model_hist, traintest_loss_file)		
		p_test = model.predict(x=X_test)
		#---- computing confusion matrices
		C = computingConfMatrix(y_test, p_test,n_classes)
		#---- saving the confusion matrix
		save_confusion_matrix(C, final_class_label, conf_file)
				
		print('Overall accuracy (OA): ', res_mat[0,norun])
		print('Train loss: ', res_mat[1,norun])
		print('Training time (s): ', res_mat[2,norun])
		print('Test time (s): ', res_mat[3,norun])
		
		#---- saving res_file
		saveMatrix(np.transpose(res_mat), res_file, eval_label)

#-----------------------------------------------------------------------		
if __name__ == "__main__":
	try:
		if len(sys.argv) == 1:
			prog = os.path.basename(sys.argv[0])
			print('      '+sys.argv[0]+' [options]')
			print("     Help: ", prog, " --help")
			print("       or: ", prog, " -h")
			print("example 1: python %s --sits_path path/to/sits_datasets --res_path path/to/results " %sys.argv[0])
			sys.exit(-1)
		else:
			parser = argparse.ArgumentParser(description='Running deep learning architectures on SITS datasets')
			parser.add_argument('--sits_path', dest='sits_path',
								help='path for train and test sits datasets',
								default=None)
			parser.add_argument('--res_path', dest='result_path',
								help='path where to store the datasets',
								default=None)
			parser.add_argument('--feat', dest='feature',
								help='used feature vector',
								default="SB")
			parser.add_argument('--noarchi', dest='noarchi', type=int,
								help='archi to run', default=2)
			parser.add_argument('--norun', dest='norun', type=int,
								help='run number', default=0)
			parser.add_argument('--seed', type=int, required=True, default=23, help='GPU to use')
			args = parser.parse_args()
			print(args.sits_path)
			main(args.sits_path, args.result_path, args.feature, args.noarchi, args.norun, args.seed)
			print("0")
	except(RuntimeError):
		print >> sys.stderr
		sys.exit(1)

#EOF
