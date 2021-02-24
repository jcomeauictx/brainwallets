WORDS ?= /etc/dictionaries-common/words
BALANCES ?= ../btcposbal2csv/balances.csv
TRIES ?= 10  # number of times to hash the keyword(s)
FOUND ?= foundkeys.txt
# $(SUFFIXES) is a GNU Makefile builtin, don't use it!
BTCSUFFIXES ?= BTC btc Bitcoin bitcoin Bitcoins bitcoins
QUIET ?= -OO
brainwallets: brainwallets.py
	python3 $(QUIET) $< $(TRIES) $(BALANCES) $(WORDS) $(BTCSUFFIXES) | \
	 tee >> $(FOUND)
test: brainwallets.py testwords.txt testbalances.csv
	$(MAKE) WORDS=testwords.txt BALANCES=testbalances.csv brainwallets
testbalances.csv: $(BALANCES)
	grep '^16ga2uqn' $< > $@
testwords.txt:
	echo satoshi nakamoto >> $@  # was emptied by a miner some time ago
	echo password >> $@  # still contains 546 satoshis 2021-02-23
