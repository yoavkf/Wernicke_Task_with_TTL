# %%
import pandas as pd
from pathlib import Path

prompts = pd.read_excel('prompt_order.xlsx',
                        sheet_name='prompts', header=None)
prompts = prompts[0].tolist()
prompts = [str(x).zfill(4) + '.txt' for x in prompts]

# questions = pd.read_excel(
#     'prompt_order.xlsx', sheet_name='questions', header=None)
# questions = questions[0].tolist()
# questions = [str(x).zfill(4) + '.txt' for x in questions]
# %%
output = pd.DataFrame([], columns=['index', 'prompt_file', 'prompt'])
pathname = 'prompts/txt'
prompt = prompts[0]

for idx, prompt in enumerate(prompts):
    file = str(Path(pathname, prompt))
    with open(file) as f:
        text = f.readlines()

    line = pd.DataFrame({'index': idx, 'prompt_file': prompt, 'prompt': text})
    output = output.append(line, ignore_index=True)
# output.to_csv('output_order.csv')

output.to_clipboard()


# %%

sentence = list(range(1, 41)) + list(range(81, 121)) + list(range(161, 321))
question = list(range(41, 81)) + list(range(121, 161)) + list(range(461, 481))
wordlist = list(range(321, 361)) 
jabberwockey = list(range(361, 401))
non_word = list(range(401, 440))
passage = list(range(441, 461))

repeat_word = [481]
repeat_sentence = [482]

type = pd.Series([], dtype="string")

for idx, prompt in enumerate(prompts):
    prompt_num = int(prompt[1:4])
    if prompt_num in sentence:
        type.at[idx] = 'Sentence'
    elif prompt_num in question:
        type.at[idx] = 'question'
    elif prompt_num in wordlist:
        type.at[idx] = 'wordlist'
    elif prompt_num in jabberwockey:
        type.at[idx] = 'jabberwa'
    elif prompt_num in non_word:
        type.at[idx] = 'non_word'
    elif prompt_num in passage:
        type.at[idx] = 'passage'
    elif prompt_num in repeat_word:
        type.at[idx] = 'repeat word'
    elif prompt_num in repeat_sentence:
        type.at[idx] = 'repeat sent.'
    else:
        type.at[idx] = 'None'
        
output.insert(2, 'type', type)
output.to_csv('output_order.csv')
output.drop('index', 1).to_clipboard()


# %%
