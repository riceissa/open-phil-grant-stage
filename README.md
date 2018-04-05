# Open Phil grant stage

See https://github.com/vipulnaik/donations/issues/11

To reproduce:

```bash
# Find the grant stage for each grant and store in CSV
./scrape.py > data.csv

# Use the data in CSV to edit the SQL file
./edit_sql.py > new.sql
```
