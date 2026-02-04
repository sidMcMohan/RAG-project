from pymilvus import connections, utility
import time

connections.connect(alias='default', host='localhost', port='19530')

if utility.has_collection('bitext_cases'):
    utility.drop_collection('bitext_cases')
    print('✅ Old collection dropped')
else:
    print('❌ Collection not found')

time.sleep(2)
connections.close()
