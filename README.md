# B+ Tree

## Inserting data in a B+ Tree

To insert data in a B+ tree run:

	python bpt.py insert <filename>

The default argument for filename is `assgn2_bplus_data.txt`

Example:

	python bpt.py insert assgn2_bplus_data.txt

The tree is saved on running this query (the insert queries are persistent).
- The corresponding data is stored in data/
- The corresponding configs are stored in .bplustree

## Querying a B+ Tree

To run the queries on the B+ tree, run

	python query <filename>

The default argument for filename is `querysample.txt`

Example:

	python query querysample.txt

The tree is saved on running this query (the insert queries are persistent).
- The corresponding data is stored in data/
- The corresponding configs are stored in .bplustree

## Deleting the tree

To delete/destroy the tree and all it's node, run

	make clean

The tree is deleted by this query and a frest tree is created for new queries.



## Output

The query qutput is displayed on std. output. It can be stored in a file using '>'. Example:

	python query querysample.txt > out

The output format is as follows:

### Insert Query
The output contains "insert:" followed by key and value
	insert: key value

### Search Query
The output contains "search:" folloed by key
The corresponding values are printed in next line seperated by ','.
If no values are found, "Not Found" is printed.

### Range Query
The output contains "range:"
The following line contains a list of tuples where each tuple represents a (key, value) pair.


## Statistics

The stats are computed and stored in stats.txt

The initial stats.txt (present already) contains the stats for running querysample.txt

## Conclusion

- Point query runs faster than range query.
- Average time for point query and insert query is of the same order as both involve same order of disk accesses.
- The number of disk accesses decreases as we increase the block size. The decrease is small as the height of tree decreases slowly when we increase the block size.
