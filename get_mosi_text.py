from mmsdk import mmdatasdk as md
import os

def get_mosi_train():
	return md.cmu_mosi.standard_folds.standard_train_fold


def get_mosi_val():
	return md.cmu_mosi.standard_folds.standard_valid_fold


def get_mosi_test():
	return md.cmu_mosi.standard_folds.standard_test_fold


def get_mosi_text():
	train = get_mosi_train()
	val = get_mosi_val()
	test = get_mosi_test()
	ftrain = open('mosi_text_train.txt', 'w')
	fval = open('mosi_text_val.txt', 'w')
	ftest = open('mosi_text_test.txt', 'w')
	dataset = load_dataset()
	text_files = os.listdir("/misc/kfdata01/kf_grp/hrwang/socialKG/raw_data/Raw/Transcript/Segmented")
	for text_file in text_files:
		video_name = text_file.split('.')[0]
		with open(os.path.join("/misc/kfdata01/kf_grp/hrwang/socialKG/raw_data/Raw/Transcript/Segmented", text_file), 'r') as f:
			i = 1
			for line in f.readlines():
				line = line.strip()
				text = line.replace(str(i) + '_DELIM_', '')
				label = get_mosi_label(dataset, video_name, i-1)
				i += 1
				if video_name in train:
					ftrain.write(text + ',' + str(label) + '\n')
				if video_name in val:
					fval.write(text + ',' + str(label) + '\n')
				if video_name in test:
					ftest.write(text + ',' + str(label) + '\n')
					

	ftrain.close()
	fval.close()
	ftest.close()


def load_dataset():
	visual_field = 'CMU_MOSI_Visual_Facet_41'
	acoustic_field = 'CMU_MOSI_COVAREP'
	text_field = 'CMU_MOSI_TimestampedWordVectors'
	label_field = 'CMU_MOSI_Opinion_Labels'

	features = [
		text_field,
		visual_field,
		acoustic_field
	]

	recipe = {feat: os.path.join('/misc/kfdata01/kf_grp/hrwang/socialKG/CMU-MultimodalSDK/cmumosi', feat) + '.csd' for feat in features}
	label_recipe = {label_field: os.path.join('/misc/kfdata01/kf_grp/hrwang/socialKG/CMU-MultimodalSDK/cmumosi', label_field + '.csd')}

	dataset = md.mmdataset(recipe)
	dataset.add_computational_sequences(label_recipe, destination=None)
	return dataset


def get_mosi_label(dataset, video_id, segement_id):
	label_field = 'CMU_MOSI_Opinion_Labels'
	return dataset[label_field][video_id]['features'][segement_id][0]

if __name__ == '__main__':
	get_mosi_text()
