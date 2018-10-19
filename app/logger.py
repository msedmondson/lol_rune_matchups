import logging

logging.basicConfig()
logger = logging.getLogger('logger')

def log(obj):
    logger.error(obj)
    return
    
if __name__ == '__main__':
    pass