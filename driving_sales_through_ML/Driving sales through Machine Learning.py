#!/usr/bin/env python
# coding: utf-8

# # Driving sales through targeted advertisement

# Businesses are profit driven, they aim to increase their revenue while keeping the cost low. One of the tools businesses employed to drive their revenue is marketing. However, marketing is expensive. In fact, Singapore's marketing expenditure on digital marketing alone is projected to reach US$760m in 2020 (statista, 2020).\
# Marketing spending does not always translate to profit, if a company wrongly designed a marketing campaign, perhaps by targeting the wrong target audience, the company might suffer loss instead. Therefore, there is a need to investigate the right customer for marketing.
# 
# In this project, we aim to increase the sucess rate for an audiobook company's marketing campaign by predicting the customers who are most likely to purchase an audiobook again.\
# We will be working with a dataset containing past user usage records, and we will be predicting the customer who will purchase another audiobook in 6 months time.
# 
# We are interested in maximising the potential user growth while minimising cost. Since F1-score measures the trade off between precision and recall, we will use F1-score as our business metrics. We will also set recall 3 times more important as precision to maximise the potential user growth while keeping cost at a reasonable level.\
# We will be solving this problem using a neural network model.
# 
# Dataset taken from: https://www.kaggle.com/faressayah/audiobook-app-data \
# Singapore's projected digital spending in 2020: https://www.statista.com/outlook/216/124/digital-advertising/singapore#market-revenue

# # Preprocessing

# ### Inspecting data

# In[1]:


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.utils import resample

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, classification_report

import tensorflow as tf
import tensorflow.keras as keras
import tensorflow.keras.layers as layers

from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import Recall
from tensorflow_addons.metrics import F1Score
from tensorflow.keras.callbacks import EarlyStopping
import kerastuner as kt
import keras.backend as K


# In[2]:


def report(true_y, predict):
    print('confusion matrix:\n')
    print(confusion_matrix(true_y, predict, labels=[0,1]))
    print('\nclassification report:\n')
    print(classification_report(true_y, predict))


# In[3]:


data = pd.read_csv('data/audiobook_data_2.csv',index_col=0)


# In[4]:


data.head()


# In[5]:


data.info()


# Good news for us, there is no missing data and no categorical data

# In[6]:


data.describe()


# However, the mean for target is 0.159. Implying that only ~16% of the customers purchased another audiobook after 6 months.\
# Since we have an imbalanced data, we will try to balance them later.\
# There is another interesting thing about Review10/10: the 25%, 50% and 75% are all 8.91.

# ### Splitting data into train, validation, test datasets

# In[7]:


X, y = data.drop('Target',axis=1), data['Target']
train_valid_x, test_x, train_valid_y, test_y = train_test_split(X,y,random_state=0,test_size=0.1)
train_x, valid_x, train_y, valid_y = train_test_split(train_valid_x,train_valid_y,random_state=0,test_size=0.1)


# In[8]:


train_y.describe()


# ### Solving unbalanced datasets

# We'll attempt 3 different strategies here:
# 1. No changing of data but focus on optimising f1 score
# 2. Oversampling minority cases
# 3. Undersampling majority cases
# 
# Here's an article talking about some common techniques to handle imbalanced datasets:\
# https://towardsdatascience.com/methods-for-dealing-with-imbalanced-data-5b761be45a18

# In[9]:


NUM_MAJOR = np.sum(train_y == 0)
NUM_MINOR = np.sum(train_y == 1)
print('Majority case count: {}\nMinority case count: {}'.format(NUM_MAJOR, NUM_MINOR))

major_class = pd.concat([train_x,train_y],axis=1)[train_y == 0]
minor_class = pd.concat([train_x,train_y],axis=1)[train_y == 1]


# In[10]:


oversampling = resample(minor_class, replace=True, n_samples=NUM_MAJOR, random_state=0)
undersampling = resample(major_class, replace=False, n_samples=NUM_MINOR, random_state=0)


# In[11]:


oversampled = pd.concat([major_class,oversampling],axis=0)
train_x_oversample, train_y_oversample = oversampled.drop('Target',axis=1), oversampled['Target']
undersampled = pd.concat([undersampling, minor_class], axis=0)
train_x_undersample, train_y_undersample = undersampled.drop('Target',axis=1), undersampled['Target']


# In[12]:


train_x.shape, train_x_oversample.shape, train_x_undersample.shape


# Now we have matching cases where\
# Original training set = 11407\
# Oversampled = number of majority cases * 2 = 9601 * 2 = 19202 \
# Undersampled = number of minority cases * 2 = 1806 * 2 = 3612

# ### Scaling

# Scaled data improves our accuracy and neural network requires the data to be scaled

# In[13]:


pipe = make_pipeline(StandardScaler()).fit(train_x)
pipe_oversample = make_pipeline(StandardScaler()).fit(train_x_oversample)
pipe_undersample = make_pipeline(StandardScaler()).fit(train_x_undersample)


# # Neural Network

# In[14]:


tf.random.set_seed(0)


# In[15]:


#we weigh recall 3 times more important than precision
def f1_metric(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    recall = true_positives / (possible_positives + K.epsilon())
    f1_val = (1+9)*(precision*recall)/(9*precision+recall+K.epsilon())
    return f1_val


# In[16]:


class Audiobook:
    def __init__(self):
        self.model = keras.Sequential()
        self.callbacks = [EarlyStopping(monitor='f1_metric', mode='max', patience=10,
                               restore_best_weights=True, verbose=2)]
    
    def build(self):
        self.model.add(layers.Dense(10))
        self.model.add(layers.Dense(50, activation='relu'))
        self.model.add(layers.Dense(50, activation='relu'))
        self.model.add(layers.Dense(1, activation='sigmoid'))
        self.model.compile(optimizer=Adam(lr=0.001), loss='binary_crossentropy',
                           metrics=['accuracy',f1_metric])
        return self


# We will run a maximum of 100 epochs for all models with a batch size 100

# In[17]:


EPOCHS = 100
BATCH_SIZE = 100


# ### No resampling

# In[18]:


model = Audiobook().build()
model_report = model.model.fit(pipe.transform(train_x), train_y, epochs=EPOCHS, batch_size=BATCH_SIZE,
         validation_data=(pipe.transform(valid_x), valid_y), verbose=0, callbacks=model.callbacks)


# ### Oversampling

# In[19]:


oversample = Audiobook().build()
oversample_report = oversample.model.fit(pipe_oversample.transform(train_x_oversample), train_y_oversample, 
                                         epochs=EPOCHS, batch_size=BATCH_SIZE,
                                         validation_data=(pipe_oversample.transform(valid_x), valid_y), 
                                         verbose=0, callbacks=oversample.callbacks)


# ### Undersampling

# In[20]:


undersample = Audiobook().build()
undersample_report = undersample.model.fit(pipe_undersample.transform(train_x_undersample), train_y_undersample, epochs=EPOCHS, batch_size=BATCH_SIZE,
         validation_data=(pipe_undersample.transform(valid_x), valid_y), verbose=0, callbacks=undersample.callbacks)


# ### Confusion matrix

# In[21]:


MAX_0, MAX_1 = np.sum(valid_y == 0), np.sum(valid_y == 1)
print('Validation set:\nNon returning customers: {}\nReturning customers: {}'.format(MAX_0,MAX_1))


# In[22]:


predict = np.where(model.model.predict(pipe.transform(valid_x)) > 0.5, 1, 0)
report(valid_y, predict)


# In[23]:


predict_oversample = np.where(oversample.model.predict(pipe_oversample.transform(valid_x))> 0.5, 1, 0)
report(valid_y, predict_oversample)


# In[24]:


predict_undersample = np.where(undersample.model.predict(pipe_undersample.transform(valid_x))> 0.5, 1, 0)
report(valid_y, predict_undersample)


# Comparing the 3 techniques to handle imbalanced datasets, original datasets gives us the highest precision but the lowest recall. This means that all the potential customers identified by us are correct, but we miss out on a lot of potential customers.\
# Comparing oversampling and undersampling, both have very similiar recalls but different precision (0.62 vs 0.54). This means that oversampling is able to caputure a relatively good proportion of the actual potential customers while making smaller mistakes, and undersampling is able to capture much higher proportion of the actual potential customers but makes a lot more mistakes. In business context, we will need to decide which is more important: more customers or more correct customers.
# 
# Since the business objective we set at first require us to balance between recall and precision, we will be using ***oversampling*** which has the highest f1-score to handle the imbalanced dataset.

# ### Hyperparameter tunning

# Since I'm using a Macbook without GPU, I ran the codes in Google Colab.\
# If you are interested in running the codes, you can uncomment the follow codes

# In[25]:


train_x, train_y = pipe_oversample.transform(train_x_oversample), train_y_oversample
valid_x, valid_y = pipe_oversample.transform(valid_x), valid_y
test_x, test_y = pipe_oversample.transform(test_x), test_y


# In[26]:


EPOCHS = 100
BATCH_SIZE = 100


# In[27]:


def model_builder(hp):
    model = keras.Sequential()
    model.add(layers.Dense(10))
    
    #changing breaths
    hp_units = hp.Choice('unit', values=[10,50,100,500,1000])
    model.add(layers.Dense(hp_units, activation='relu'))
    model.add(layers.Dense(hp_units, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))
    #changing learning rates
    hp_lr = hp.Choice('learning rate', values=[0.01, 0.001, 0.0001])
    model.compile(optimizer=Adam(lr=hp_lr), loss='binary_crossentropy',
                           metrics=['accuracy',f1_metric])
    return model


# In[28]:


tuner = kt.Hyperband(model_builder, metrics=[f1_metric], objective=kt.Objective("f1_metric", direction="max"), 
                     max_epochs=10, seed=0, directory='report', project_name='hyperparameter_tunning')


# In[29]:


tuner.search(train_x, train_y, epochs=EPOCHS, batch_size=BATCH_SIZE,
            validation_data=(valid_x, valid_y), 
             callbacks = [EarlyStopping(monitor='f1_metric', mode='max', patience=3,
                               restore_best_weights=True, verbose=2)], verbose=0)


# ### The best model

# In[30]:


tuner.results_summary(1)


# In[31]:


best_model = tuner.get_best_models(num_models=1)[0]


# In[32]:


best_model_report = best_model.fit(train_x, train_y, 
                             epochs=EPOCHS, batch_size=BATCH_SIZE,
                             validation_data=(valid_x, valid_y), 
                             verbose=0, callbacks=[EarlyStopping(monitor='f1_metric', mode='max', patience=3,
                                                  restore_best_weights=True, verbose=2)])
predict = best_model.predict(valid_x)
predict = np.where(predict> 0.5, 1, 0)
report(valid_y, predict)


# Our final model is captures more potential customers than the pre-tunned oversampling (recall: 0.75 vs 0.71) at a cost of lowered accuracy (precision: 0.60 vs 0.62). Compared to the undersampling data, our final model is more accurate at capturing potential customers (precision: 0.60 vs 0.54) but still worse at capturing all the potential customers (recall: 0.75 vs 0.82)

# ### Testing model

# In[33]:


test_predict = best_model.predict(test_x)
test_predict = np.where(test_predict> 0.5, 1, 0)
report(test_y, test_predict)


# The test dataset contains data points our model has never seen before. Therefore, test dataset shows the expected performance when we deploy our model in the real world.\
# As seen from the classficaition report, our model is able to capture ~70% of all potential customers while being ~60% correct in average.

# # Business impact

# Let us assume our marketing spending is 3 dollars/customer and each returned customer is able to generate 10 dollars in revenue. And we assume we target a total of 100 customers.
# 
# **Before deploying our model**\
# We targeted 100 customers randomly with 16\% (assumed population from dataset) of the customers are potential returning customers.\
# Total marketing spending: 3x100=300 dollars\
# Total revenue: 10x16=160 dollars\
# Net profit: (140) dollars
# 
# **After deploying our model**\
# We targeted 100 customers with 57\% (model precision) certain that these customers are returning customers.\
# Total marketing spending: 3x100=300 dollars\
# Total revenue: 10x0.57x100=570 dollars\
# Net profit: 270 dollars

# As seen from the above simplified example, deploying machine learning algorithm indeed helps us to turn a lossing strategy into a profiting strategy!
