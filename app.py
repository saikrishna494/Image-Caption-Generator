
import mysql.connector 
from flask import Flask, render_template, request
import cv2
from keras.models import load_model
import numpy as np
from keras.layers import Dense,  LSTM, TimeDistributed, Embedding, Activation, RepeatVector,Concatenate
from keras.models import Sequential, Model
import cv2
from keras.preprocessing.sequence import pad_sequences
from tqdm import tqdm

import cv2
mysql_config ={
    'user':'root',
    'password':'root',
    'host':'localhost',
    'database':'sai'    
}

db = mysql.connector.connect(**mysql_config)
cursor = db.cursor()


vocab = np.load(r'E:\vs code\html\site\vocab.npy', allow_pickle=True)

vocab = vocab.item()

inv_vocab = {v:k for k,v in vocab.items()}



print("vocabulary loaded")


embedding_size = 128
vocab_size = len(vocab)
max_len = 40


image_model = Sequential()

image_model.add(Dense(embedding_size, input_shape=(2048,), activation='relu'))
image_model.add(RepeatVector(max_len))


language_model = Sequential()

language_model.add(Embedding(input_dim=vocab_size, output_dim=embedding_size, input_length=max_len))
language_model.add(LSTM(256, return_sequences=True))
language_model.add(TimeDistributed(Dense(embedding_size)))


conca = Concatenate()([image_model.output, language_model.output])
x = LSTM(128, return_sequences=True)(conca)
x = LSTM(512, return_sequences=False)(x)
x = Dense(vocab_size)(x)
out = Activation('softmax')(x)
model = Model(inputs=[image_model.input, language_model.input], outputs = out)

model.compile(loss='categorical_crossentropy', optimizer='RMSprop', metrics=['accuracy'])

model.load_weights(r'E:\vs code\html\site\mine_model_weights.h5')

print("="*150)
print("MODEL LOADED")

#resnet = ResNet50(include_top=False,weights='imagenet',input_shape=(224,224,3),pooling='avg')


resnet = load_model(r'E:\vs code\html\resnet.h5')

print("="*150)
print("RESNET MODEL LOADED")


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static' 


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/Sign_in",methods=["GET","POST"])
def Sign_in():
    return render_template("Sign_in.html")

@app.route('/submit_form',methods=['POST'])
def submit_form():
    username = request.form['username']
    emial = request.form['emial']
    password = request.form['password']

    
    # Insert the form data into the database
    sql = "INSERT INTO users (username, emial, password) VALUES (%s, %s, %s)"
    values = (username, emial, password )
    cursor.execute(sql, values)
    db.commit()


    
    # Redirect the user to a success page
    return render_template('success.html')

@app.route("/login",methods=["GET","POST"])
def login():
    return render_template("login.html")


@app.route('/login_test',methods=['POST'])
def login_test():
    if request.method == "POST":
        emial = request.form["emial"]
        password = request.form["password"]

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="sai"
        )

        cursor = conn.cursor() 
        query = "SELECT * FROM users WHERE emial = %s AND password = %s"
        values = (emial, password)
        cursor.execute(query, values)
        user = cursor.fetchone()

        if user:
            return render_template("img_upload.html")
        else:
            return "login failed"



@app.route('/predict', methods=['GET','POST'])

def predict():

    global model, resnet, vocab, inv_vocab

    img = request.files['image']

    img.save('static/file.jpg')

    print("IMAGE SAVED")


    
    image = cv2.imread('static/file.jpg')
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image = cv2.resize(image, (224,224))

    image = np.reshape(image, (1,224,224,3))

    
    
    incept = resnet.predict(image).reshape(1,2048)

    print("Predict Features")


    text_in = ['startofseq']

    final = ''

 
    print("GETTING Captions")

    count = 0
    while tqdm(count < 20):

        count += 1

        encoded = []
        for i in text_in:
            encoded.append(vocab[i])

        padded = pad_sequences([encoded], maxlen=max_len, padding='post', truncating='post').reshape(1,max_len)

        sampled_index = np.argmax(model.predict([incept, padded]))

        sampled_word = inv_vocab[sampled_index]

        if sampled_word != 'endofseq':
            final = final + ' ' + sampled_word

        text_in.append(sampled_word)


    return render_template('predict.html', data=final)
  
    
if __name__=="__main__":
   app.run(debug=True)
    