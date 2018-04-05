# Open Phil grant stage

See https://github.com/vipulnaik/donations/issues/11

To reproduce:

1. Reload data into the donations database. This step is needed because the
   `scrape.py` script queries the database in the course of determining which
   grant is "initial" or "repeated".

2. Copy over the file
   [`sql/donations/open-phil-grants.sql`](https://github.com/vipulnaik/donations/blob/master/sql/donations/open-phil-grants.sql)
   from the donations repo (save as `open-phil-grants.sql` in this repo).

3. Find the grant stage and grant review process for each grant, and store in CSV:

   ```bash
   ./scrape.py > data.csv
   ```

4. Use the data in CSV to edit the SQL file:

   ```bash
   ./edit_sql.py > new.sql
   ```
