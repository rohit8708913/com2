import os, time, re

id_pattern = re.compile(r'^.\d+$') 


class Config(object):
    # pyro client config
    API_ID    = os.environ.get("API_ID", "22469064")  # ⚠️ Required
    API_HASH  = os.environ.get("API_HASH", "c05481978a217fdb11fa6774b15cba32") # ⚠️ Required
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7942169109:AAFpemq2qXv92PP6XUD1l1YlI4lqLQdw8Bc") # ⚠️ Required
    FORCE_SUB = os.environ.get('FORCE_SUB', '-1002266025682') # ⚠️ Required
    AUTH_CHANNEL = int(FORCE_SUB) if FORCE_SUB and id_pattern.search(
    FORCE_SUB) else None
   
    # database config
    DB_URL = os.environ.get("DB_URL", "mongodb+srv://koyeb77user:rohit870@cluster0.wgdkp.mongodb.net/?retryWrites=true&w=majority")
    DB_NAME = os.environ.get("DATABASE_NAME", "cphdlust1234")

    # Other Configs 
    ADMIN = int(os.environ.get("ADMIN", "7328629001")) # ⚠️ Required
    LOG_CHANNEL = int(os.environ.get('LOG_CHANNEL', '-1002170811388')) # ⚠️ Required
    BOT_UPTIME = BOT_UPTIME  = time.time()
    START_PIC = os.environ.get("START_PIC", "https://graph.org/file/15e82d7e665eccc8bd9c5.jpg")

    # wes response configuration     
    WEBHOOK = bool(os.environ.get("WEBHOOK", True))
    PORT = int(os.environ.get("PORT", "6347"))


    caption = """
**File Name**: {0}

**Original File Size:** {1}
**Encoded File Size:** {2}
**Compression Percentage:** {3}

__Downloaded in {4}__
__Encoded in {5}__
__Uploaded in {6}__
"""
