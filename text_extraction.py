import string
import base64
import json
import os
import io

from PIL import Image, ImageEnhance

#import cloudstorage as gcs

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "Noteify-7ee05830ab6d.json"

from google.cloud import pubsub_v1
from google.cloud import storage
from google.cloud import translate
from google.cloud import vision

from HumongousDB import HumongousDB
from ExquisiteSushi import ExquisiteSushi

from nltk.corpus import stopwords

# Configure settings

project_id = 'noteify'

vision_client = vision.ImageAnnotatorClient()
translate_client = translate.Client()
publisher = pubsub_v1.PublisherClient()
storage_client = storage.Client()

with open('console.json') as f:
    data = f.read()
config = json.loads(data)

def sharpen_image(in_path):
    image = Image.open(in_path)
    enhancer = ImageEnhance.Sharpness(image)

    factor = 2.0
    enhanced = enhancer.enhance(factor)

    out_path = in_path[:-4] + "_sharp.jpg"
    fp = open(out_path, 'w')
    enhanced.save(fp)

def validate_message(message, param):
    var = message.get(param)
    if not var:
        raise ValueError('{} is not provided. Make sure you have \
                         property {} in the request.'.format(param, param))
    return var



def detect_text(bucket, filename):
#    print('Looking for text in image {}'.format(filename))

    futures = []

    text_detection_response = vision_client.text_detection({
        'source': {'image_uri': 'gs://{}/{}'.format(bucket, filename)}
    })
    annotations = text_detection_response.text_annotations
    if len(annotations) > 0:
        text = annotations[0].description
    else:
        text = ''
#    print('Extracted text {} from image ({} chars).'.format(text, len(text)))

    detect_language_response = translate_client.detect_language(text)
    src_lang = detect_language_response['language']
#    print('Detected language {} for text {}.'.format(src_lang, text))

    # Submit a message to the bus for each target language
    for target_lang in config.get('TO_LANG', []):
        topic_name = config['TRANSLATE_TOPIC']
        if src_lang == target_lang or src_lang == 'und':
            topic_name = config['RESULT_TOPIC']
        message = {
            'text': text,
            'filename': filename,
            'lang': target_lang,
            'src_lang': src_lang
        }
        message_data = json.dumps(message).encode('utf-8')
        topic_path = publisher.topic_path(project_id, topic_name)
        future = publisher.publish(topic_path, data=message_data)
        futures.append(future)
    for future in futures:
        future.result()



def process_image(file, context):
    """Cloud Function triggered by Cloud Storage when a file is changed.
    Args:
        file (dict): Metadata of the changed file, provided by the triggering
                                 Cloud Storage event.
        context (google.cloud.functions.Context): Metadata of triggering event.
    Returns:
        None; the output is written to stdout and Stackdriver Logging
    """
    bucket = validate_message(file, 'bucket')
    name = validate_message(file, 'name')

    detect_text(bucket, name)

#    print('File {} processed.'.format(file['name']))



def save_result(event, context):
    if event.get('data'):
        message_data = base64.b64decode(event['data']).decode('utf-8')
        message = json.loads(message_data)
    else:
        raise ValueError('Data sector is missing in the Pub/Sub message.')

    text = validate_message(message, 'text')
    filename = validate_message(message, 'filename')
    lang = validate_message(message, 'lang')

#    print('Received request to save file {}.'.format(filename))

    bucket_name = config['RESULT_BUCKET']
    result_filename = '{}_{}.txt'.format(filename, lang)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(result_filename)

#    print('Saving result to {} in bucket {}.'.format(result_filename,
#                                                     bucket_name))
    blob.upload_from_string(text)
#    print('File saved.')

storage_client = storage.Client("noteify")
bucket = storage_client.get_bucket("noteify")

def download_from_bucket(in_name, out_name):
    blob = bucket.blob(in_name)
    blob.download_to_filename("{}".format(out_name))

def upload_to_bucket(in_name, counter):
    img_name = "img{}_sharp.jpg".format(str(counter))
    blob = bucket.blob(img_name)
    blob.upload_from_filename(in_name)

    return img_name

def save_image(in_name):
    image = Image.open(in_name)
    out_file = open('/static/'+in_name, 'w')
    image.save(out_file)


def detect_document(path):
    """Detects document features in an image."""
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.document_text_detection(image=image)

    word_list = []

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
#            print('\nBlock confidence: {}\n'.format(block.confidence))

            for paragraph in block.paragraphs:
#                print('Paragraph confidence: {}'.format(
#                    paragraph.confidence))

                for word in paragraph.words:
                    word_text = ''.join([
                        symbol.text for symbol in word.symbols
                    ])
#                    print('Word text: {} (confidence: {})'.format(
#                        word_text, word.confidence))
                    word_list.append(word_text)

#                    for symbol in word.symbols:
#                        print('\tSymbol: {} (confidence: {})'.format(
#                            symbol.text, symbol.confidence))
    return word_list

def processWordlist(word_list):
    # remove punctuation
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in word_list]

    # eliminate non-alphabetic words
    words = [word for word in stripped if word.isalpha()]

    # only lowercase
    words = [word.lower() for word in words]

    # filter out stopwords
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]
    return words

if __name__ == '__main__':

    local_storage = ExquisiteSushi()
    local_storage2 = ExquisiteSushi()

    database = HumongousDB()
    database.init_connection()
    database.init_database("Noteify")
    database.init_collection("Images")
    
    database2 = HumongousDB()
    database2.init_connection()
    database2.init_database("Noteify2")
    database2.init_collection("Tags")

    download_from_bucket("img-16-02-22:46:00.jpg", "img-16-02-22:46:00.jpg")

    in_path = "img-16-02-22:46:00.jpg"
    sharpen_image(in_path)

    save_image("img-16-02-22:46:00.jpg")

    counter = 0
    sharp_image_name = upload_to_bucket("downloady_sharp.jpg", counter)
    counter += 1

    word_list = detect_document("downloady_sharp.jpg")

    pwords = processWordlist(word_list)
    for pword in pwords:
        local_storage.append(pword, sharp_image_name)
        local_storage2.append(sharp_image_name, pword)
    
    
    database.insert_token(local_storage.get_memory())
    database2.insert_token(local_storage2.get_memory())
   # database.print_collection()
    #database2.print_collection()

    retrieved_img_list = database.retrieve("mango")
    retrieved_tags_list = database2.retrieve("img0_sharp.jpg")

    #print(retrieved_img_list)
    #print(retrieved_tags_list)
    print(database.getDatabase())
    print(database2.getDatabase())


    database.clear_collection()
    database2.clear_collection()
    
    database.close_connection()
    database2.close_connection()


