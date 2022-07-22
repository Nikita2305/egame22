import torch
import torch.nn as nn
import pickle
import torch.nn.functional as F
import numpy as np
import random

class TextRNN(nn.Module):
    
    def __init__(self, input_size, hidden_size, embedding_size, n_layers, device):
        super(TextRNN, self).__init__()
        
        self.device = device

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.embedding_size = embedding_size
        self.n_layers = n_layers

        self.encoder = nn.Embedding(self.input_size, self.embedding_size)
        self.lstm = nn.LSTM(self.embedding_size, self.hidden_size, self.n_layers)
        self.dropout = nn.Dropout(0.2)
        self.fc = nn.Linear(self.hidden_size, self.input_size)
        
    def forward(self, x, hidden):
        x = self.encoder(x).squeeze(2)
        out, (ht1, ct1) = self.lstm(x, hidden)
        out = self.dropout(out)
        x = self.fc(out)
        return x, (ht1, ct1)
    
    def init_hidden(self, batch_size=1):
        return (torch.zeros(self.n_layers, batch_size, self.hidden_size, requires_grad=True).to(self.device),
               torch.zeros(self.n_layers, batch_size, self.hidden_size, requires_grad=True).to(self.device))

class TextGenerator:
    
    def __init__(self, path_to_model, path_to_char_to_idx, path_to_idx_to_char):
        self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        with open(path_to_char_to_idx, 'rb') as f:
            self.char_to_idx = pickle.load(f)
        with open(path_to_idx_to_char, 'rb') as f:
            self.idx_to_char = pickle.load(f)
        self.model = TextRNN(input_size=len(self.idx_to_char), hidden_size=128, embedding_size=128, n_layers=2, device=self.device)
        self.model.load_state_dict(torch.load(path_to_model)) 
        
    def evaluate(self, model, char_to_idx, idx_to_char, start_text=' ', prediction_len=200, temp=0.3):
        
        hidden = model.init_hidden()
        idx_input = [char_to_idx[char] for char in start_text]
        train = torch.LongTensor(idx_input).view(-1, 1, 1).to(self.device)
        predicted_text = start_text
        
        _, hidden = model(train, hidden)
            
        inp = train[-1].view(-1, 1, 1)
        
        for i in range(prediction_len):
            output, hidden = model(inp.to(self.device), hidden)
            output_logits = output.cpu().data.view(-1)
            p_next = F.softmax(output_logits / temp, dim=-1).detach().cpu().data.numpy()        
            top_index = np.random.choice(len(char_to_idx), p=p_next)
            inp = torch.LongTensor([top_index]).view(-1, 1, 1).to(self.device)
            predicted_char = idx_to_char[top_index]
            predicted_text += predicted_char
        
        return predicted_text

    def give_me_text(self, length):
        return self.evaluate(self.model, self.char_to_idx, self.idx_to_char, ". ", length, 0.3)

    def remove_patterns(self, text, patterns):
        for pattern in patterns:    
            if pattern in text:
                text = text.replace(pattern, "")
        return text
        
    def get_cute_message(self, length=1000):
        while (True):
            text = self.give_me_text(length)
            text = self.remove_patterns(text,
                ["admin",
                "Войти или зарегистрироваться",
                "Источник",
                "Команда форума",
                "Администратор",
                "Последнее редактирование:"]
            )
            if len(text) > 10:
                return text

    def get_words(self, n):
        while (True):
            text = self.get_cute_message(500)
            text = self.remove_patterns(text,
                ["admin",
                "Войти или зарегистрироваться",
                "Источник",
                "Команда форума",
                "Администратор",
                "Последнее редактирование:"]
            )
            tokens = text.split()
            if len(tokens) == 0:
                continue
            ret = []
            for i in range(n):
                ret += [tokens[random.randint(0, len(tokens) - 1)]]
            return ret

"""t = TextGenerator("result_1.rus", "char_to_idx_1.pickle", "idx_to_char_1.pickle")
print(" ".join(t.get_words(5)))"""
