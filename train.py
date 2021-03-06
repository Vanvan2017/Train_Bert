import torch
import random
from transformers import BertForSequenceClassification
from transformers import AdamW
import numpy as np
from transformers import BertTokenizer
from torch.utils.data import TensorDataset, DataLoader, random_split
from utils import get_data, encode_fn ,flat_accuracy
from transformers import get_linear_schedule_with_warmup
from tqdm import tqdm
import os
#os.environ["CUDA_VISIBLE_DEVICES"] = "3"
batch_size = 8
epochs = 20
seed = 42
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed_all(seed)
torch.backends.cudnn.deterministic = True

device = torch.device('cuda')
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
train_text, train_labels = get_data('six_emotions/fear_train.txt')
val_text, val_labels = get_data('six_emotions/fear_dev.txt')

train_input_ids = encode_fn(train_text, tokenizer)
train_labels = torch.tensor(train_labels)

val_input_ids = encode_fn(val_text, tokenizer)
val_labels = torch.tensor(val_labels)

train_dataset = TensorDataset(train_input_ids, train_labels)
val_dataset = TensorDataset(val_input_ids, val_labels)

train_dataloader = DataLoader(train_dataset, batch_size = batch_size, shuffle = True)
val_dataloader = DataLoader(val_dataset, batch_size = batch_size, shuffle = False)

model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2, output_attentions=False, output_hidden_states=False)

#num = torch.cuda.device_count()
#print('device:', num)
#model = torch.nn.DataParallel(model, device_ids=[0,1,2,3])
model = model.cuda()


optimizer = AdamW(model.parameters(), lr=2e-5)
total_steps = len(train_dataloader) * epochs
scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)


for epoch in tqdm(range(epochs)):
    print('epoch:', epoch)
    model.train()
    total_loss, total_val_loss = 0, 0
    total_eval_accuracy = 0
    for step, batch in enumerate(train_dataloader):
        model.zero_grad()
        loss, logits = model(batch[0].to(device), token_type_ids=None, attention_mask=(batch[0]>0).to(device), labels=batch[1].to(device))
        total_loss += loss.item()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step() 
        scheduler.step()
        
    model.eval()
    for i, batch in enumerate(val_dataloader):
        with torch.no_grad():
            loss, logits = model(batch[0].to(device), token_type_ids=None, attention_mask=(batch[0]>0).to(device), labels=batch[1].to(device))
                
            total_val_loss += loss.item()
            
            logits = logits.detach().cpu().numpy()
            label_ids = batch[1].to('cpu').numpy()
            total_eval_accuracy += flat_accuracy(logits, label_ids)
    
    avg_train_loss = total_loss / len(train_dataloader)
    avg_val_loss = total_val_loss / len(val_dataloader)
    avg_val_accuracy = total_eval_accuracy / len(val_dataloader)
    
    print('Train loss', avg_train_loss)
    print('Validation loss', avg_val_loss)
    print('Accuracy:', avg_val_accuracy)

tokenizer.save_pretrained('six_emotions/fear_tokenizer')
model.save_pretrained('six_emotions/fear_bert_model')
