
import logging

# configure logger.
FORMAT = '%(asctime)s %(filename)s:%(lineno)d [%(levelname)s] - %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('launchdarkly')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)
