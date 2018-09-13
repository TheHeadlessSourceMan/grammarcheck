python -m cProfile -o profile.dat grammarcheck.py %*
python profile2csv.py profile.dat
del profile.dat