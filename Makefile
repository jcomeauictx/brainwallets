WORDS ?= /etc/dictionaries-common/words
BALANCES ?= ../btcposbal2csv/balances.csv
# $(SUFFIXES) is a GNU Makefile builtin, don't use it!
BTCSUFFIXES ?= BTC btc Bitcoin bitcoin Bitcoins bitcoins
QUIET ?= -OO
brainwallets: brainwallets.py
	python3 $(QUIET) $< 5 $(BALANCES) $(WORDS) $(BTCSUFFIXES)
test: brainwallets.py testwords.txt testbalances.csv
	$(MAKE) WORDS=testwords.txt BALANCES=testbalances.csv brainwallets
p2pk.csv: balances.csv
	grep '^1' $< > $@
testbalances.csv: $(BALANCES)
	grep '^16ga2uqn' $< > $@
