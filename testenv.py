pcross = False
btc = 0.01
usd = 0.00

prev0 = None
prev1 = None

data = open('data.dmp', 'r')
for current in data:
	current = float(current)
	if not prev0 or not prev1:
		prev0 = current
		prev1 = current
	if pcross == None:
		if prev0 < prev1:
			pcross = False
		if prev0 > prev1:
			pcross = True
	prev0 = ((2 * (current - prev0)) / 10) + prev0
	prev1 = ((2 * (current - prev1)) / 22) + prev1
	if prev0 < prev1 and not pcross:
		pcross = True
		usd = btc * current
		btc = 0
		print "SELL " + str(usd) + "USD @" + str(current)
	if prev0 > prev1 and pcross:
		pcross = False
		btc = usd / current
		usd = 0
		print "BUY " + str(btc) + "BTC @" + str(current)
	#print str(current)
print '\n', btc, usd