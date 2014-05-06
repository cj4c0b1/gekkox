'''
ToDo
- banking functionality by percentage
- fetch transaction fees
'''

import time
from mtgox import MtGox
import cPickle as pickle

# Settings
SETTINGS = {
	'POLLING_RATE':		180, #seconds
	'MIN_TRADE':			0.01, #BTC
	'MAX_TRADE':			1.00, #BTC
	'BTC':					0.02011920, #BTC
	'USD':					0.00, #USD
	'TRANS_FEE': 			0.00, #%
	'LAST_TRANS':			0.00, #USD
	'ITERATIONS':			0,
}

# Analysis Data
ADATA = {
	'EMA_FAST':		None, #BTC
	'EMA_SLOW':		None, #BTC
	'POS_CROSSOVER':	None,
	'LAST':				0,
}

# API Config
API_KEY =			""
API_SECRET =		""
API_CURRENCY =		"USD"
API = 				MtGox(API_KEY, API_SECRET, API_CURRENCY)


def analyze ():
	if not ADATA['EMA_FAST'] or not ADATA['EMA_SLOW']:
		ADATA['EMA_FAST'] = ADATA['LAST']
		ADATA['EMA_SLOW'] = ADATA['LAST']
	if ADATA['POS_CROSSOVER'] == None:
		if ADATA['EMA_FAST'] < ADATA['EMA_SLOW']:
			ADATA['POS_CROSSOVER'] = False
		if ADATA['EMA_FAST'] > ADATA['EMA_SLOW']:
			ADATA['POS_CROSSOVER'] = True
	ADATA['EMA_FAST'] = ((2 * (ADATA['LAST'] - ADATA['EMA_FAST'])) / 11) + ADATA['EMA_FAST']
	ADATA['EMA_SLOW'] = ((2 * (ADATA['LAST'] - ADATA['EMA_SLOW'])) / 22) + ADATA['EMA_SLOW']
	return ADATA
	
def trade ():
	if ADATA['EMA_FAST'] < ADATA['EMA_SLOW'] and not ADATA['POS_CROSSOVER']:
		ADATA['POS_CROSSOVER'] = True
		SETTINGS['USD'] = SETTINGS['BTC'] * ADATA['LAST']
		SETTINGS['BTC'] = 0.0
		SETTINGS['LAST_TRANS'] = ADATA['LAST']
		print "Sell: " + str(SETTINGS['USD']) + API_CURRENCY + " @" + str(ADATA['LAST'])
	if ADATA['EMA_FAST'] > ADATA['EMA_SLOW'] and ADATA['POS_CROSSOVER']:
		ADATA['POS_CROSSOVER'] = False
		SETTINGS['BTC'] = SETTINGS['USD'] / ADATA['LAST']
		SETTINGS['USD'] = 0.0
		SETTINGS['LAST_TRANS'] = ADATA['LAST']
		print "Buy: " + str(SETTINGS['BTC']) + "BTC @" + str(ADATA['LAST'])

def buy (amount):
	# fetch total USD
	# make purchase
	# update SETTINGS
	print "Buy " + amount
	return False
	
def sell (amount):
	print "Sell " + amount
	return False
		
def fetch ():
	data = API.ticker_data()
	if str(data['result']) == 'success':
		ADATA['LAST'] = float(data['data']['last']['value'])
	else:
		return False
	data = None
	data = API.get_info()
	if str(data['result']) == 'success':
		#SETTINGS['BTC'] = float(data['data']['Wallets']['BTC']['Balance']['value'])
		#SETTINGS['USD'] = float(data['data']['Wallets']['USD']['Balance']['value'])
		SETTINGS['TRANS_FEE'] = float(data['data']['Trade_Fee'])
	else:
		return False
	return True
		
def load ():
	try:
		input = open('data.pkl', 'rb')
		load = pickle.load(input)
		input.close()
		ADATA = load[0]
		SETTINGS = load[1]
	except:
		print "*** Error loading data ***"
	
def save ():
	output = open('data.pkl', 'wb')
	pickle.dump([ADATA, SETTINGS], output)
	output.close()
	
if __name__ == '__main__':
	load()
	SETTINGS['ITERATIONS'] = 0
	while True:
		start_time = time.time()
		if fetch():
			analyze()
			if ADATA['POS_CROSSOVER'] != None and SETTINGS['ITERATIONS'] > 6:
				trade()
			print time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ':\t' + str(ADATA)
			SETTINGS['ITERATIONS'] += 1
		else:
			print "*** Failed to poll data ***"
		save()
		time.sleep(SETTINGS['POLLING_RATE'] - (time.time() - start_time))
