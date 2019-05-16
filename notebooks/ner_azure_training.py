import json
import random
import spacy
from pathlib import Path
from spacy.util import minibatch, compounding

TRAIN_DATA = []
with open('../data/processed/ner_azure_services_annotations/ner_azure_services_with_lower.jsonl') as annotations_file:
    for line in annotations_file.readlines():
        json_line = json.loads(line)
        ents = [(s['start'], s['end'], s['label']) for s in json_line['spans']]
        ann = (json_line['text'], {'entities': ents})
        TRAIN_DATA.append(ann)

        
n_iter = 1
model = 'en_vectors_web_lg'
output_dir = '../models/spacy_2.1-ner_azure_lower'
new_model_name = 'spacy_ner_azure_lower'

# create the built-in pipeline components and add them to the pipeline
# nlp.create_pipe works for built-ins that are registered with spaCy
nlp = spacy.load(model)

if "ner" not in nlp.pipe_names:
    ner = nlp.create_pipe("ner")
    nlp.add_pipe(ner, last=True)
# otherwise, get it so we can add labels
else:
    ner = nlp.get_pipe("ner")
move_names = list(ner.move_names)

# add labels
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])



# get names of other pipes to disable them during training
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
with nlp.disable_pipes(*other_pipes):  # only train NER
    # reset and initialize the weights randomly – but only if we're
    # training a new model
    print('starting training')
    nlp.begin_training()
    for itn in range(n_iter):
        random.shuffle(TRAIN_DATA)
        losses = {}
        # batch up the examples using spaCy's minibatch
        batches = minibatch(TRAIN_DATA, size=compounding(1.0, 4.0, 1.001))
        for batch in batches:
            texts, annotations = zip(*batch)
            nlp.update(
                texts,  # batch of texts
                annotations,  # batch of annotations
                drop=0.35,  # dropout - make it harder to memorise data
                losses=losses,
            )
        print(f"Losses after {itn} iterations", losses)

    
    for t, _ in TRAIN_DATA[:10]:
        doc = nlp(t)
        print('=' * 100)
        print(t)
        print([(e.text, e.label_) for e in doc.ents])
    
    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.meta["name"] = new_model_name  # rename model
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        # Check the classes have loaded back consistently
        assert nlp2.get_pipe("ner").move_names == move_names
        doc2 = nlp2(test_text)
        for ent in doc2.ents:
            print(ent.label_, ent.text)