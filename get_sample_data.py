from pymongo import MongoClient
import numpy as np

def get_data_from_mongo(percent_data):
    mc = MongoClient()
    db = mc['meetups']
    ed = db['events_data']
    num_events = ed.estimated_document_count()
    data = []
    count = 0
    np.random.seed(1969)
    nums = np.random.randint(0, num_events, int(num_events * percent_data))
    #import pdb; pdb.set_trace()
    for event in ed.find():
        if count in nums:
            data.append(event)
        count += 1
    return data
