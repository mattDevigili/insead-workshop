#%% Libraries
#--+ nlp
import spacy
nlp = spacy.load("en_core_web_lg")
from tomotopy.coherence import Coherence
from tomotopy.utils import Corpus
from tomotopy import LDAModel
#--+ other
from itertools import chain
from collections import Counter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient
#--+ connection
client = MongoClient()
db = client.insead_workshop
collection = db.python
#--+ get data
df = pd.DataFrame(collection.find({},{'_id':1, 'body':1}))
#%%
class TomotopyLDA:
    """This class bundles corpus creation utilities and LDA training using 
       Tomotopy
    """

    def __init__(self, preprocessed_docs, inplace_=False, out_path="corpus_xxx.cps"):
        """Initialize and populate a Tomotopy Corpus class object 

        Args:
            procesed_docs: iterable of pre-processed docs
            inplace_(boolean): save the file (default is False)
            out_path(str): file path to write

        Returns: Tomotopy Corpus class objec

        """
        self.corpus = Corpus()
        for i in preprocessed_docs:
            self.corpus.add_doc(i)
        # save for reuse
        if inplace_ is True:
            self.corpus.save(out_path)
    
    def get_coherence(self, min_, max_, delta_, seed=123):
        """
		params:
			corpus_: text corpus
			min_: min number of k to train LDA
			max_: max number of k to train LDA
			delta_: delta of variation to train the model
			seed: reproducibility purposes
		outcome:
			a dictionary containing number of topics: coherence 
			score
		"""
        cs = {}
        for k in range(min_, max_, delta_):
            print('Running model {}'.format(k))
            for i in range(0, 50, 1):
                lda_model = LDAModel(k=k, seed=seed, corpus=self.corpus)
                lda_model.train(20, workers=1)
            score = Coherence(lda_model, coherence='c_v').get_score()
            cs[k] = score
		# return
        return cs

    def lda(self, k_, min_df=0, rm_top=0, verbose_=True):
        """LDA implementation

           Args:
              corpus_(Tomotopy corpus): text corpus
              k_(int): number of k to train the LDA
              min_df(int): minimum collection frequency of words. Words
                      with a smaller collection frequency than min_cf
                      are excluded from the model (default 0)
              rm_top(int): the number of top words to be removed (default
                      0)

           Returns:
              A Tomotpy LDAModel class object
        """
        # model
        model = LDAModel(
            k=k_, seed=123, corpus=self.corpus, min_df=min_df, rm_top=rm_top
        )
        # model training
        for i in range(0, 50, 1):
            model.train(20, workers=1)
        # summary
        if verbose_ is True:
            model.summary()
        # return
        return model
#%% process documents
#--+ process text
docs = list(
    nlp.pipe(df['body'].to_list(), n_process=1)
)
# extract and polish tokens
docs_tokens = [
    [
        token.lemma_.lower()
        for token in doc
        if token.is_alpha
        and not token.is_stop
        and not token.is_digit
        and not token.is_oov
        and not token.like_num
        and not token.like_email
        and not token.like_url
    ]
    for doc in docs
]
# %% run Coherence analysis
model = TomotopyLDA(preprocessed_docs=docs_tokens).lda(k_=10)
# %% store
model.save('skills_10_topics.bin')
# %%
import pyLDAvis
def LDAvis(lda_model, outPath = 'ldavis.html'):
	"""
	params:
		lda_model: trained lda model
		outPath: save file to path
	outcome:
		a dynamic visualization of the topics via pyLDAvis.
	"""
	# extract model info
	topic_term_dists = np.stack([lda_model.get_topic_word_dist(k) for k in range(lda_model.k)])
	doc_topic_dists = np.stack([doc.get_topic_dist() for doc in lda_model.docs])
	doc_topic_dists /= doc_topic_dists.sum(axis=1, keepdims=True)
	doc_lengths = np.array([len(doc.words) for doc in lda_model.docs])
	vocab = list(lda_model.used_vocabs)
	term_frequency = lda_model.used_vocab_freq
	# prepare data
	prepared_data = pyLDAvis.prepare(
	    topic_term_dists, 
	    doc_topic_dists, 
	    doc_lengths, 
	    vocab, 
	    term_frequency,
	    start_index=0, # tomotopy starts topic ids with 0, pyLDAvis with 1
	    sort_topics=False # IMPORTANT: otherwise the topic_ids between pyLDAvis and tomotopy are not matching!
	)
	# save viz
	pyLDAvis.save_html(prepared_data, outPath)

LDAvis(model)
# %% Pass to pymongo
docs_topics = [
    model.infer(model.make_doc(doc))
    for doc in docs_tokens]
for t_d, id in zip(docs_topics, df['_id'].to_list()):
    collection.update_one(
        {
            '_id': id
        },
        {
            '$set': {'tm_10': [np.float64(i) for i in t_d[0]]}
        }
)
# %%
