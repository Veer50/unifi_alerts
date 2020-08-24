from elasticsearch import Elasticsearch
from elasticsearch import helpers
from datetime import datetime, timezone, timedelta
import json
import pytz
import certifi
from pytz import timezone
import pandas as pd
import logging
import time
from pandas.io.json import json_normalize



import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase 
from email import encoders 
# from .venue_cache_check import VenueCacheCheck

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def start_process(gte, lte, config):
    venue_id = config.get('venue_config').get('venue_id')
    config_es = config['elastic_config']
    logging.info("Venue_id -> {}".format(venue_id))
    # print("gte -> ",gte,"   lte -> ",lte)
    # print("On es:", 1591315200000, 1591401599999)
    # print("Here", int(gte), int(lte))
    
    cfg = {
        "es": {
          "host": config_es['host'],
          "port": config_es['port'],
          "username": config_es['username'],
          "password": config_es['password'],
          "search_query": {
            "query": {
                "bool":{
                  "must":[
                    {
                      "range":{
                        "occured_at":{
                          "gte": int(gte),
                          "lte": int(lte),
                          "format":"epoch_millis"
                        }
                      }
                    },
                    # {
                    #   "match_phrase": {
                    #     "belongs.owner.veId": {
                    #       "query": venue_id
                    #     }
                    #   }
                    # }
                  ]
                }
              }
          },
          "index":config_es["index_prefix"]
        }
    }

    query = cfg.get('es').get("search_query")
    # index = cfg.get('es').get("index")
    
    es = Elasticsearch(hosts=[config_es['host']+":"+ str(config_es['port'])], http_auth=(config_es['username'], config_es['password']), timeout=120,ca_certs=certifi.where())
    
    count = 0
    page = es.search(index=config_es["index_prefix"], body=query, size=10000, scroll = "2m")
    raw_data = page["hits"]["hits"]

    sender = config["email_config"]["sender"]
    password = config["email_config"]["password"]
    recipient = config["email_config"]["recipient"]
    sub = config["email_config"]["sub"]
    body = config["email_config"]["body"]
    
    if raw_data:
        df_all = pd.json_normalize(raw_data)
        
        df_specific = df_all[[ '_source.received_at', '_source.location','_source.iDTag_id','_source.customer','_source.message',"_source.mail.from","_source.type","_source.device.device_name", "_source.alert.alert_name"]].copy()
        df_specific = df_specific.astype(str)

        for ind in df_specific.index: 
        #  print(df['Name'][ind], df['Stream'][ind]) 
            if (df_specific["_source.type"][ind] == "switch") or (df_specific["_source.type"][ind] == "ap") or (df_specific["_source.type"][ind] == "network") :
                df_specific['_source.message'][ind]  = df_specific['_source.alert.alert_name'][ind]
            else:
                df_specific['_source.device.device_name'][ind]= df_specific['_source.location'][ind]+' - '+df_specific['_source.iDTag_id'][ind]
                
        df_specific["_source.received_at"] = pd.to_datetime(df_specific['_source.received_at'])
        df_specific["_source.received_at"] = pd.Series([datetime.strptime(val.time().strftime('%H:%M'), "%H:%M") for val in df_specific["_source.received_at"]])
        df_specific["_source.received_at"] = pd.Series([val.strftime("%I:%M %p") for val in df_specific["_source.received_at"]])
        df_specific = df_specific.applymap(str)



        df_specific.rename(columns={"_source.received_at": "Alert Received Time (IST)", 
                                    "_source.device.device_name":"Device Name",
                                    "_source.customer": "Site", 
                                    "_source.message": "Message",
                                    "_source.mail.from":"Controller URL"}, inplace = True)

        df_specific.drop(columns = ['_source.location', '_source.iDTag_id',"_source.type","_source.alert.alert_name"] ,inplace = True)
        cols = ["Alert Received Time (IST)","Device Name","Site","Message","Controller URL"]
        df_specific = df_specific[cols]
        df_specific.sort_values("Alert Received Time (IST)", inplace  = True)


        filename = "dialy_report.csv"
        df_specific.to_csv(filename)



        send_mail( sender, password, recipient, sub,body , filename)
    else:
        send_mail( sender, password, recipient, sub,"Hi team, \n\n We dont have any unifi alerts for today.")
            
def get_data_for_day(config):
    
    fmt = "%Y-%m-%d %H:%M:%S"
    start = datetime.now().strftime("%Y-%m-%d")
    # start = "2020-08-01"
    
    start_time = datetime.strptime(str(start) + " 00:00:00", fmt)
    end_time = datetime.strptime(datetime.now().strftime(fmt) ,fmt)
    
    
    
    # def time_to_utc( input_time, zone_name):
    #   local = pytz.timezone(zone_name)
    #   local_dt = local.localize(input_time.replace(tzinfo=None))
    #   return local_dt.astimezone(pytz.utc)

    # def utc_to_time(input_time, zone_name):
    #   return input_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(zone_name))

    # start_time_string = pytz.timezone(config.get('venue_config').get('tz_region')).localize(start_time).astimezone(pytz.utc).strftime(fmt)
    # end_time_string = pytz.timezone(config.get('venue_config').get('tz_region')).localize(start_end).astimezone(pytz.utc).strftime(fmt)
    # start = datetime.strptime(start_time_string , fmt)
    # end = datetime.strptime(end_time_string , fmt)
    
    # ct = start_process(utc_to_time(start_time,"Asia/Kolkata").timestamp() * 1000, utc_to_time(start_end,"Asia/Kolkata").timestamp() * 1000,config.get('venue_config').get('venue_id'),config["venue_config"]['elastic_config'])
    ct = start_process(start_time.timestamp() * 1000, end_time.timestamp() * 1000,config)




def send_mail( sender, s_password, recipient, sub,body, filename = "No_alerts"):
    # print ("\n\n SEND MAIL IN CC")

    # msg = multipart.MIMEMultipart('alternative')
    msg = MIMEMultipart()
    msg['Subject'] = sub
    msg['From'] = sender
    msg['To'] = recipient
    # msg["Body"]  = body 
    msg.attach(MIMEText(body+"\n\n", 'plain'))
    if filename != "No_alerts":
        attachment = open("./"+filename, "rb")
        p = MIMEBase('application', 'octet-stream') 
        p.set_payload((attachment).read()) 
        encoders.encode_base64(p) 
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
        msg.attach(p)
    
    

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(sender, s_password)
    s.sendmail(sender, recipient, msg.as_string())
    s.quit()

# if __name__ == '__main__':
#   config = " "

#   main_process = get_data_for_day(config)
  







  